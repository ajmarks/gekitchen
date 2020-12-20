"""Constants for handling fridge ERD values"""

__all__ = (
    "ErdDoorStatus",
    "ErdFilterStatus",
    "ErdFullNotFull",
    "ErdHotWaterStatus",
    "ErdPodStatus",
    'FridgeDoorStatus',
    'FridgeIceBucketStatus',
    'FridgeSetPointLimits',
    'FridgeSetPoints',
    'HotWaterStatus',
    'IceMakerControlStatus',
)

import enum
from datetime import timedelta
from typing import NamedTuple, Optional
from .common import ErdPresent, ErdOnOff

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
class FridgeIceBucketStatus(NamedTuple):
    state_full_fridge: ErdFullNotFull
    state_full_freezer: ErdFullNotFull
    is_present_fridge: bool
    is_present_freezer: bool
    total_status: ErdFullNotFull
   
class IceMakerControlStatus(NamedTuple):
    status_fridge: ErdOnOff
    status_freezer: ErdOnOff

class FridgeDoorStatus(NamedTuple):
    fridge_right: ErdDoorStatus
    fridge_left: ErdDoorStatus
    freezer: ErdDoorStatus
    drawer: ErdDoorStatus
    status: str

class FridgeSetPointLimits(NamedTuple):
    fridge_min: int
    fridge_max: int
    freezer_min: int
    freezer_max: int

class FridgeSetPoints(NamedTuple):
    fridge: int
    freezer: int

class HotWaterStatus(NamedTuple):
    status: ErdHotWaterStatus
    time_until_ready: Optional[timedelta]
    current_temp: Optional[int]
    tank_full: ErdFullNotFull
    brew_module: ErdPresent
    pod_status: ErdPodStatus

