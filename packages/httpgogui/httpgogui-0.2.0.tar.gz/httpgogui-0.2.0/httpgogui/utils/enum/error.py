from enum import Enum


class ErrorEnum(str, Enum):
    """错误enum"""

    JSONDECODEERROR = "JSONDecodeError"
    INVALIDURL = "InvalidURL"
    MISSINGSCHEMA = "MissingSchema"
    READTIMEOUT = "ReadTimeout"
    UNKNOWNERROR = "unknownerror"
