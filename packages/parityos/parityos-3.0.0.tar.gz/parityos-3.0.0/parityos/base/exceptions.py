"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.
"""

from __future__ import annotations


class ParityOSException(Exception):
    """
    General exception thrown by ParityOS.
    """


class ParityOSImportError(ImportError):
    """
    ImportError related to uninstalled optional ParityOS dependencies.
    """


class ParityOSUniquenessError(ParityOSException):
    """
    Error related to duplicate qubits in OperatorProducts
    """


class ParityOSNotSupportedError(ParityOSException):
    """
    Error related to not supported features.
    """
