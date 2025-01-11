from __future__ import annotations

import time
from abc import abstractmethod
from typing import Any, Generic, TypeVar

from attrs import define, field, frozen
from typing_extensions import TypeAlias, override

from parityos.api_interface.client import HTTPClient
from parityos.api_interface.exceptions import ParityOSRunError, ParityOSTimeoutException
from parityos.api_interface.run_info import RunInfo, RunStatus
from parityos.base import Circuit, ProblemRepresentation, from_dict, to_dict
from parityos.base.bit import GridQubit2D
from parityos.device_connectivity import DeviceConnectivity
from parityos.encodings.parity_mapping import ParityMapping


def to_options_dict(options: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(options, dict):
        return options
    elif isinstance(options, str):
        return {"preset": options}
    else:
        raise NotImplementedError(f"The options input has to be str or dict, got {options}")


@frozen
class InputData:
    """Base class for the input data of a service run"""

    options: dict[str, Any] = field(converter=to_options_dict)


InputDataT = TypeVar("InputDataT", bound=InputData)
OutputDataT = TypeVar("OutputDataT")

SubmissionID: TypeAlias = str


class Service(Generic[InputDataT, OutputDataT]):
    """Interface for running services in ParityOS."""

    @abstractmethod
    def run(self, input_data: InputDataT) -> OutputDataT:
        """Runs the full service synchronously, from input to output."""


class AsyncService(Service[InputDataT, OutputDataT]):
    TIME_BETWEEN_TRIALS: float = 2  # seconds
    TIMEOUT: float = 60 * 15  # 15 minutes in seconds

    @override
    def run(self, input_data: InputDataT) -> OutputDataT:
        """A synchronous wrapper around the asynchronous functionality of this class."""
        submission_id = self.submit(input_data)
        print(f"Running submission {submission_id}")

        stop_time = time.time() + self.TIMEOUT
        while time.time() <= stop_time:
            time.sleep(self.TIME_BETWEEN_TRIALS)
            run_info = self.get_info(submission_id)

            if run_info.status == RunStatus.FAILED:
                raise ParityOSRunError(f"Run failed for submission {submission_id}.")
            elif run_info.status == RunStatus.COMPLETED:
                output_data = self.get_result(submission_id)
                return output_data

        raise ParityOSTimeoutException(
            f"Client-side timeout of {self.TIMEOUT} seconds reached for submission {submission_id}."
        )

    @abstractmethod
    def submit(self, input_data: InputDataT) -> SubmissionID:
        """
        Submits input data and returns a submission id string that can be used to get results
        """

    @abstractmethod
    def get_info(self, submission_id: SubmissionID) -> RunInfo:
        """Gets information about the run of a submission."""

    @abstractmethod
    def get_result(self, submission_id: SubmissionID) -> OutputDataT:
        """
        Gets the output for a submission, the caller is responsible for making sure the
        run is complete (by calling get_info).
        """


@define
class APIService(AsyncService[InputDataT, OutputDataT]):
    """
    A class that can be used to connect to the ParityAPI, a username is required to authenticate.
    """

    client: HTTPClient

    @property
    @abstractmethod
    def input_data_type(self) -> type[InputDataT]:
        """The type of input data for this service."""

    @property
    @abstractmethod
    def output_data_type(self) -> type[OutputDataT]:
        """The type of the output data for this service."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The string name of this service."""

    @property
    def url(self) -> str:
        """The host location of this service."""
        return f"{self.client.host}/{self.name}"

    @override
    def submit(self, input_data: InputDataT) -> SubmissionID:
        """
        Asynchronously submit a request, returns a submission id which can be used to obtain the
        results.
        """
        data = to_dict(input_data)
        response = self.client.send_request("POST", url=f"{self.url}/submission", data=data)
        submission_id = response.json()
        return submission_id

    @override
    def get_result(self, submission_id: str) -> OutputDataT:
        """Get the results found by a run."""
        response = self.client.send_request("GET", url=f"{self.url}/run_result/{submission_id}")
        return from_dict(response.json(), self.output_data_type)

    @override
    def get_info(self, submission_id: str) -> RunInfo:
        """Gets information on the current status of a submission."""
        response = self.client.send_request("GET", url=f"{self.url}/run_info/{submission_id}")
        return from_dict(response.json(), RunInfo)


@frozen
class LayoutInput(InputData):
    problem: ProblemRepresentation
    device: DeviceConnectivity[GridQubit2D]


@define
class LayoutService(APIService[LayoutInput, ParityMapping]):
    @property
    @override
    def name(self) -> str:
        return "layout"

    @property
    @override
    def input_data_type(self) -> type[LayoutInput]:
        return LayoutInput

    @property
    @override
    def output_data_type(self) -> type[ParityMapping]:
        return ParityMapping


@frozen
class CircuitInput(InputData):
    circuit: Circuit
    device: DeviceConnectivity[GridQubit2D]


@define
class CircuitService(APIService[CircuitInput, Circuit]):
    @property
    @override
    def name(self) -> str:
        return "circuit"

    @property
    @override
    def input_data_type(self) -> type[CircuitInput]:
        return CircuitInput

    @property
    @override
    def output_data_type(self) -> type[Circuit]:
        return Circuit
