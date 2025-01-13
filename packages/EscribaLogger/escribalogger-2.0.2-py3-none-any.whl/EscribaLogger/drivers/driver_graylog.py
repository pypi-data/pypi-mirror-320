from typing import TypedDict, Optional, Literal
import logging

HAS_GRAYPY = True

try:
    import graypy
except ImportError:
    HAS_GRAYPY = False

class DriverOptionsGraylog(TypedDict):
    graylog_host: Optional[str]
    graylog_port: Optional[int]
    graylog_protocol: Optional[Literal["http", "udp"]]

def driver_graylog(driver_options: DriverOptionsGraylog = None):
    if not HAS_GRAYPY:
        raise ImportError(
            "You must install graypy to use the graylog driver. "
            "Run: pip install graypy"
        )

    graylog_host = driver_options.get("graylog_host", "localhost")
    graylog_port = driver_options.get("graylog_port", 12201)
    protocol = driver_options.get("graylog_protocol", "http")

    formatter_string = "%(name)s.%(levelname)s - %(message)s"
    formatter = logging.Formatter(formatter_string)
    stream = graypy.GELFHTTPHandler(graylog_host, graylog_port)

    if protocol == "udp":
        stream = graypy.GELFUDPHandler(graylog_host, graylog_port)
    elif protocol == "http":
        stream = graypy.GELFHTTPHandler(graylog_host, graylog_port)

    stream.setFormatter(formatter)
    return stream