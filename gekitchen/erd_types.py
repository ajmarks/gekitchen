"""Types for structured ERD values"""

__all__ = (
    'AvailableCookMode',
    'FridgeDoorStatus',
    'FridgeIceBucketStatus',
    'FridgeSetPointLimits',
    'FridgeSetPoints',
    'HotWaterStatus',
    'IceMakerControlStatus',
    'OvenCookMode',
    'OvenCookSetting',
    'OvenConfiguration',
)

from datetime import timedelta
from typing import NamedTuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .erd_constants import (
        ErdOvenCookMode,
        ErdOvenState,
        ErdDoorStatus,
        ErdFullNotFull,
        ErdOnOff,
        ErdHotWaterStatus,
        ErdPodStatus,
        ErdPresent,
    )


class AvailableCookMode(NamedTuple):
    """Parsing helper for Available Cook Modes"""
    byte: int
    mask: int
    cook_mode: "ErdOvenCookMode"


class OvenConfiguration(NamedTuple):
    """Cleaner representation of ErdOvenConfiguration"""
    has_knob: bool
    has_warming_drawer: bool
    has_light_bar: bool
    has_lower_oven: bool
    has_lower_oven_kitchen_timer: bool
    raw_value: Optional[str] = None


class OvenCookMode(NamedTuple):
    """Named tuple to represent ErdOvenCookMode for easier formatting later"""
    oven_state: "ErdOvenState"
    delayed: bool = False
    timed: bool = False
    probe: bool = False
    warm: bool = False
    sabbath: bool = False


class OvenCookSetting(NamedTuple):
    """Cleaner representation of ErdOvenCookMode"""
    cook_mode: OvenCookMode
    temperature: int
    raw_bytes: Optional[bytes] = None


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

