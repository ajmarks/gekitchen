"""Types for structured ERD values"""

from collections import namedtuple


OvenCookSetting = namedtuple(
    "OvenCookSetting",
    ["cook_mode", "temperature", "raw_bytes"],
    defaults=[None]
)
AvailableCookMode = namedtuple("AvailableCookMode", ["byte", "mask", "cook_mode"])
OvenConfiguration = namedtuple(
    "OvenConfiguration",
    ["has_knob", "has_warming_drawer", "has_light_bar", "has_lower_oven", "has_lower_oven_kitchen_timer", "raw_value"],
    defaults=[None]
)
