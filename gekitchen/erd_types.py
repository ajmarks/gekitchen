"""Types for structured ERD values"""

from typing import NamedTuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .erd_constants import ErdOvenCookMode, ErdOvenState


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
