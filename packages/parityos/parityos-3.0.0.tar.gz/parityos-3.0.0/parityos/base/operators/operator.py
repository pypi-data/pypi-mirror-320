"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    Literal,
    Optional,
    TypeVar,
    overload,
)

from attrs import Attribute, astuple, evolve, field, frozen
from symengine import Symbol
from typing_extensions import Self, TypeGuard, override

from parityos.base.bit import Cbit, Qubit
from parityos.base.exceptions import ParityOSException
from parityos.base.io_utils import register_subclasses
from parityos.base.utils import (
    Weight,
    WeightTypes,
    stringify_iterable,
    to_frozenset_check_unique,
)

if TYPE_CHECKING:
    from parityos.base.operator_polynomial import OperatorPolynomial
    from parityos.base.operator_product import OperatorProduct

DEFAULT_PARAMETER_NAME = "parameter"
OPERATOR_TYPE_TAG = "operator_type"
OPERATOR_NAME_TO_CLASS: dict[str, type[OperatorLike]] = {}


class OperatorLike(ABC):
    """Abstract base class for all objects that behave like operators acting on a set of qubits."""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The dynamically generated name for this operator.
        Where applicable the name must coincide with the OpenQASM standard.
        """

    @property
    @abstractmethod
    def qubits(self) -> frozenset[Qubit]:
        """The set of qubits the operator acts on."""

    @property
    def n_qubits(self) -> int:
        """The amount of qubits this operator acts on."""
        return len(self.qubits)

    @abstractmethod
    def get_hermitian_conjugate(self) -> OperatorLike:
        """Return the hermitian conjugate (or dagger) of this operator."""

    @property
    @abstractmethod
    def is_hermitian(self) -> bool:
        """True if this operator is hermitian."""


class Parameterized(ABC):
    """Mixin interface for any object that contains symbolic parameters."""

    @property
    @abstractmethod
    def parameters(self) -> frozenset[Symbol]: ...


class HasCBits(ABC):
    """Mixin interface for any operator with classical bits."""

    @property
    @abstractmethod
    def cbits(self) -> frozenset[Cbit]: ...


class Operator(OperatorLike, ABC):
    # __init_subclass__ doesn't play well with attrs decorated classes
    # https://www.attrs.org/en/stable/init.html#attrs-and-init-subclass
    @classmethod
    def __attrs_init_subclass__(cls) -> None:
        register_subclasses(Operator, OPERATOR_TYPE_TAG)

    ## Arithmetic #################################################################################
    def __neg__(self) -> OperatorPolynomial[Self]:
        """Compute -operator, represented by a single element OperatorPolynomial with weight -1."""
        return self.__mul__(-1.0)

    @overload
    def __mul__(
        self, other: OtherOperatorT | OperatorProduct[OtherOperatorT]
    ) -> OperatorProduct[Self | OtherOperatorT]: ...
    @overload
    def __mul__(
        self, other: OperatorPolynomial[OtherOperatorT]
    ) -> OperatorPolynomial[Self | OtherOperatorT]: ...
    @overload
    def __mul__(self, other: Weight) -> OperatorPolynomial[Self]: ...
    def __mul__(self, other):
        """Compute multiplication of Operator with
        - scalar: returns single element OperatorProduct with `weight=other`
        - Operator: returns a two element OperatorProduct
        - OperatorProduct: adds `self` to the operators of `other`
        """
        from parityos.base.operator_product import OperatorProduct

        # combine with other Operator into 2-element OperatorProduct
        if isinstance(other, Operator):
            return OperatorProduct((self, other))
        # append self to other OperatorProduct
        if isinstance(other, OperatorProduct):
            return evolve(
                other,
                operators=chain(other.operators, (self,)),
            )

        from parityos.base.operator_polynomial import OperatorPolynomial

        # promote to weighted OperatorPolynomial
        if isinstance(other, WeightTypes):
            return OperatorPolynomial({OperatorProduct(self): other})
        if isinstance(other, OperatorPolynomial):
            return evolve(
                other,
                term_weight_pairs={term * self: weight for term, weight in other.term_weight_pairs},
            )
        return NotImplemented

    def __add__(
        self,
        other: (
            Literal[0]
            | OtherOperatorT
            | OperatorProduct[OtherOperatorT]
            | OperatorPolynomial[OtherOperatorT]
        ),
    ) -> OperatorPolynomial[Self | OtherOperatorT]:
        """Compute addition between Operator and
        - 0: enable `sum` of `Iterable[Operator]`.
        - Operator: return a two element OperatorPolynomial with both self and other turned into
            single element OperatorProducts with weight 1.
        - OperatorProduct: return a two element OperatorPolynomial with self turned into a
            single element OperatorProducts with weight 1.
        - OperatorPolynomial: turn self into a single element OperatorProducts with weight 1 and
            add it to the terms of `other`.
        """
        # import here to avoid cyclic imports
        from parityos.base.operator_polynomial import OperatorPolynomial
        from parityos.base.operator_product import DEFAULT_WEIGHT, OperatorProduct

        # to enable sum()
        if other == 0:
            return OperatorPolynomial({OperatorProduct(self): DEFAULT_WEIGHT})
        if isinstance(other, Operator):
            return OperatorPolynomial(
                {
                    OperatorProduct(self): DEFAULT_WEIGHT,
                    OperatorProduct(other): DEFAULT_WEIGHT,
                }
            )
        if isinstance(other, OperatorProduct):
            return OperatorPolynomial(
                {OperatorProduct(self): DEFAULT_WEIGHT, other: DEFAULT_WEIGHT}
            )
        if isinstance(other, OperatorPolynomial):
            return evolve(
                other,
                term_weight_pairs=chain(
                    other.term_weight_pairs, ((OperatorProduct(self), DEFAULT_WEIGHT),)
                ),
            )
        return NotImplemented

    def __sub__(
        self,
        other: (
            OtherOperatorT | OperatorProduct[OtherOperatorT] | OperatorPolynomial[OtherOperatorT]
        ),
    ) -> OperatorPolynomial[Self | OtherOperatorT]:
        """Compute Operator - Operator/OperatorProduct/OperatorPolynomial as self + (-other)."""
        return self + (-other)

    def __rsub__(
        self,
        other: OperatorProduct[OtherOperatorT] | OperatorPolynomial[OtherOperatorT],
    ) -> OperatorPolynomial[Self | OtherOperatorT]:
        """Compute OperatorProduct/OperatorPolynomial - Operator as -self + other."""
        return -self + other

    __rmul__ = __mul__  # pyright: ignore[reportUnannotatedClassAttribute]
    __radd__ = __add__  # pyright: ignore[reportUnannotatedClassAttribute]

    def __lt__(self, other: object) -> bool:
        """Enable sorting of Operators."""
        if isinstance(other, Operator):
            return (sorted(self.qubits), self.name) < (sorted(other.qubits), other.name)
        return NotImplemented


OperatorT = TypeVar("OperatorT", bound=Operator, covariant=True)
OtherOperatorT = TypeVar("OtherOperatorT", bound=Operator, covariant=True)


class OperatorCompound(OperatorLike, Generic[OperatorT], ABC):
    # TODO(VS): Fix name ambiguity
    #  (e.g. cxx and cnot * X yield different objects with the same name "cxx")
    @abstractmethod
    def is_all(self, cls: type[OtherOperatorT]) -> TypeGuard[OperatorCompound[OtherOperatorT]]:
        """Check whether all contained operators are instances of `cls`."""

    @property
    @abstractmethod
    def is_mixed(self) -> bool:
        """Check whether all contained operators are of the same type."""

    def __lt__(self, other: object) -> bool:
        """Enable sorting against other Operators or OperatorCompounds
        based on the sorted set of qubits.
        """
        if isinstance(other, (Operator, OperatorCompound)):
            return (sorted(self.qubits), self.name) < (sorted(other.qubits), other.name)
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Operator):
            return not self.__lt__(other)
        return NotImplemented


def _check_n_qubits(
    self: ElementaryOperator, _: Attribute[frozenset[Qubit]], qubits: frozenset[Qubit]
):
    """
    Check whether the amount of passed qubits is correct based on self.N_QUBITS, if not None.
    """
    if self.N_QUBITS is not None and len(qubits) != self.N_QUBITS:
        raise ParityOSException(
            f"{self.name} takes {self.N_QUBITS} target qubits, got {len(qubits)}"
        )


@frozen(order=False)
class ElementaryOperator(Operator, ABC):
    """
    Abstract base class for all elementary operators that act on an unordered collection of qubits.

    Subclasses must implement get_hermitian_conjugate().
    """

    # override with integer in a subclass to enable checking the amount of qubits passed to the init
    N_QUBITS: ClassVar[Optional[int]] = None

    qubits: frozenset[Qubit] = field(converter=to_frozenset_check_unique, validator=_check_n_qubits)

    @override
    def __str__(self) -> str:
        return f"{type(self).__name__}({stringify_iterable(sorted(self.qubits))})"

    ## NamedOperator ##############################################################################
    @property
    @override
    def name(self) -> str:
        return type(self).__name__.lower()

    @property
    @override
    def is_hermitian(self) -> bool:
        return False


@frozen(order=False)
class HermitianOperator(ElementaryOperator):
    """
    Represents a general hermitian operator, which returns a copy of itself as hermitian conjugate
    """

    @override
    def get_hermitian_conjugate(self) -> Self:
        return evolve(self)

    @property
    @override
    def is_hermitian(self) -> bool:
        return True


# marker class for Pauli X, Y, Z
class PauliOperator(HermitianOperator): ...


@frozen(order=False)
class X(PauliOperator):
    """The Pauli X operator"""

    N_QUBITS: ClassVar[int] = 1


@frozen(order=False)
class Y(PauliOperator):
    """The Pauli Y operator"""

    N_QUBITS: ClassVar[int] = 1


@frozen(order=False)
class Z(PauliOperator):
    """The Pauli Z operator"""

    N_QUBITS: ClassVar[int] = 1


@frozen(order=False)
class H(HermitianOperator):
    """The Hadamard gate"""

    N_QUBITS: ClassVar[int] = 1


@frozen(order=False)
class SX(ElementaryOperator):
    """The square root of the Pauli X operator"""

    N_QUBITS: ClassVar[int] = 1

    @override
    def get_hermitian_conjugate(self) -> SXDg:
        return SXDg(*astuple(self, recurse=False))


@frozen(order=False)
class SXDg(ElementaryOperator):
    """The hermitian conjugate of SX"""

    N_QUBITS: ClassVar[int] = 1

    @override
    def get_hermitian_conjugate(self) -> SX:
        return SX(*astuple(self, recurse=False))


@frozen(order=False)
class Swap(HermitianOperator):
    """the two-qubit Swap gate"""

    N_QUBITS: ClassVar[int] = 2


@frozen(order=False)
class ISwap(ElementaryOperator):
    """The two-qubit ISwap gate"""

    N_QUBITS: ClassVar[int] = 2

    @override
    def get_hermitian_conjugate(self) -> ISwapDg:
        return ISwapDg(*astuple(self, recurse=False))


@frozen(order=False)
class ISwapDg(ElementaryOperator):
    """The hermitian conjugate of the two-qubit ISwap gate"""

    N_QUBITS: ClassVar[int] = 2

    @override
    def get_hermitian_conjugate(self) -> ISwap:
        return ISwap(*astuple(self, recurse=False))


@frozen
class ID(Operator):
    """An identity operator"""

    qubits: frozenset[Qubit] = field(converter=to_frozenset_check_unique)

    @override
    def __str__(self) -> str:
        return f"{type(self).__name__}({stringify_iterable(sorted(self.qubits))})"

    @property
    @override
    def name(self) -> str:
        return type(self).__name__.lower()

    @override
    def get_hermitian_conjugate(self) -> Self:
        return self

    @property
    @override
    def is_hermitian(self) -> bool:
        return True
