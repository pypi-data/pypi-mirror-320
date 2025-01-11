"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Tools to process the results from the ParityOS cloud service.
"""

from datetime import datetime
from enum import Enum
from typing import Union

from attrs import field, frozen
from typing_extensions import override


class RunStatus(Enum):
    SUBMITTED = "S"
    RUNNING = "R"
    COMPLETED = "C"
    FAILED = "F"


def _str_to_datetime(date: Union[datetime, str]) -> Union[datetime, None]:
    """Helper method to convert dates in string format to datetime instances."""
    if date is None or isinstance(date, datetime):
        return date
    else:
        return datetime.fromisoformat(date.replace("Z", "+00:00"))


@frozen
class RunInfo:
    """
    Encapsulates the information about a service run; has attributes which describe relevant times
    at which they were submitted, started, and eventually finished or failed
    (in which case, a reason for failure is also given).

    :param id: The UUID4 id of the run in ParityOS cloud database.
    :param submission_id: The UUID4 id of the submission which triggered the run.
    :param status: The status of the submission; see `RunStatus`.
    :param submitted_at: Time at which the run was queued for execution, as `datetime` object.
    :param started_at: Time at which the run started being executed, as `datetime` object.
    :param finished_at: Time at which the run was completed, as `datetime` object.
    :param failed_at: time at which run failed
    :param failure_reason: reason for which run failed
    """

    id: str
    submission_id: str
    status: RunStatus = field(converter=RunStatus)
    submitted_at: Union[datetime, None] = field(default=None, converter=_str_to_datetime)
    started_at: Union[datetime, None] = field(default=None, converter=_str_to_datetime)
    finished_at: Union[datetime, None] = field(default=None, converter=_str_to_datetime)
    failed_at: Union[datetime, None] = field(default=None, converter=_str_to_datetime)
    failure_reason: str = field(default="")

    @override
    def __str__(self) -> str:
        """
        Return useful information about the run in string format.
        """
        info_lines = [f"Run id {self.id}. Status: {self.status}"]
        if self.submitted_at:
            info_lines.append(f"The run was submitted at {self.submitted_at.ctime()}.")

        if self.started_at:
            info_lines.append(f"The run started at {self.started_at.ctime()}.")
            if self.finished_at:
                duration_in_seconds = (self.finished_at - self.started_at).total_seconds()
                info_lines.append(f"The run took {duration_in_seconds:0.2f} seconds.")

        if self.failed_at:
            if self.started_at:
                duration_in_seconds = (self.failed_at - self.started_at).total_seconds()
                info_lines.append(f"The run was aborted after {duration_in_seconds:0.2f} seconds.")
            else:
                info_lines.append(f"An error occurred at {self.failed_at.ctime()}.")

        if self.failure_reason:
            info_lines.append(self.failure_reason)

        return "\n".join(info_lines)
