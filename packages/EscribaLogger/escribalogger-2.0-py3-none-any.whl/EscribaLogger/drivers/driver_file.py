from typing import TypedDict, Optional
import logging
import datetime
import os


class DriverOptionsFile(TypedDict):
    file_location: Optional[str]
    file_name: Optional[str]

def driver_file(driver_option: DriverOptionsFile = None):
    if not driver_option:
        driver_option = {"file_location": "logs"}

    formatter_string = "[%(asctime)s] "
    formatter_string += "%(name)s.%(levelname)s "
    formatter_string += "- %(message)s "
    formatter_string += "(%(filename)s:%(lineno)d) "
    formatter_string += "%(extra_context)s"

    formatter = logging.Formatter(formatter_string)
    # formatter.default_time_format = '%Y-%m-%d %H:%M:%s'

    now_time = datetime.datetime.now().strftime("%Y-%m-%d")
    default_filename = f"{now_time}.log"

    log_file_name = driver_option.get("file_name", default_filename)
    log_file_location = driver_option.get("file_location", "logs")

    log_file_path = os.path.join(log_file_location, log_file_name)

    stream = logging.FileHandler(log_file_path)
    stream.setFormatter(formatter)
    return stream
