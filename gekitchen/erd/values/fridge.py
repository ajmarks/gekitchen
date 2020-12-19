"""Constants for handling ERD values - fridge"""

__all__ = (
    "ErdDoorStatus",
    "ErdFilterStatus",
    "ErdFullNotFull",
    "ErdHotWaterStatus",
    "ErdPodStatus",
)

import enum

@enum.unique
class ErdFullNotFull(enum.Enum):
    FULL = "01"
    NOT_FULL = "00"
    NA = "NA"

@enum.unique
class ErdDoorStatus(enum.Enum):
    """Fridge door status"""
    CLOSED = "00"
    OPEN = "01"
    NA = "FF"

@enum.unique
class ErdHotWaterStatus(enum.Enum):
    NOT_HEATING = "00"
    HEATING = "01"
    READY = "02"
    FAULT_NEED_CLEARED = "FD"
    FAULT_LOCKED_OUT = "FE"
    NA = "NA"

@enum.unique
class ErdPodStatus(enum.Enum):
    REPLACE = "00"
    READY = "01"
    NA = "FF"

@enum.unique
class ErdFilterStatus(enum.Enum):
    GOOD = "00"
    REPLACE = "01"
    EXPIRED = "02"
    UNFILTERED = "03"
    LEAK_DETECTED = "04"
    NA = "FF"
