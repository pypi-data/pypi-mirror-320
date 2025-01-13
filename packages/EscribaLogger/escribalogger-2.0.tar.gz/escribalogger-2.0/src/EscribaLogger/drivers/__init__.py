from typing import TypedDict, Optional, Literal, TypeAlias

from .driver_file import driver_file, DriverOptionsFile
from .driver_graylog import driver_graylog, DriverOptionsGraylog
from .driver_stdout import driver_stdout, DriverOptionsStdout

class DriverOptions(TypedDict):
    file: Optional[DriverOptionsFile]
    graylog: Optional[DriverOptionsGraylog]
    stdout: Optional[DriverOptionsStdout]

t_available_drivers: TypeAlias = Literal["file", "stdout", "graylog"]

__all__ = [
    "driver_file",
    "driver_graylog",
    "driver_stdout",

    "DriverOptions",
    "t_available_drivers",
]
