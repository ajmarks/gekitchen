"""Types for structured ERD values - fridge"""

__all__ = (
    'FridgeDoorStatus',
    'FridgeIceBucketStatus',
    'FridgeSetPointLimits',
    'FridgeSetPoints',
    'HotWaterStatus',
    'IceMakerControlStatus',
)

from datetime import timedelta
from typing import NamedTuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from gekitchen.erd.values import (
        ErdDoorStatus,
        ErdFullNotFull,
        ErdOnOff,
        ErdHotWaterStatus,
        ErdPodStatus,
        ErdPresent,
    )

class FridgeIceBucketStatus(NamedTuple):
    state_full_fridge: "ErdFullNotFull"
    state_full_freezer: "ErdFullNotFull"
    is_present_fridge: bool
    is_present_freezer: bool
    total_status: "ErdFullNotFull"

class IceMakerControlStatus(NamedTuple):
    status_fridge: "ErdOnOff"
    status_freezer: "ErdOnOff"

class FridgeDoorStatus(NamedTuple):
    fridge_right: "ErdDoorStatus"
    fridge_left: "ErdDoorStatus"
    freezer: "ErdDoorStatus"
    drawer: "ErdDoorStatus"
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
    status: "ErdHotWaterStatus"
    time_until_ready: Optional[timedelta]
    current_temp: Optional[int]
    tank_full: "ErdFullNotFull"
    brew_module: "ErdPresent"
    pod_status: "ErdPodStatus"

