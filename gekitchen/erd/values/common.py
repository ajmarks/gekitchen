"""Constants for handling ERD values - common"""

__all__ = (
    "ErdApplianceType",
    "ErdClockFormat",
    "ErdEndTone",
    "ErdMeasurementUnits",
    "ErdOnOff",
    "ErdPresent",
    "ErdSoundLevel",
)

import enum

@enum.unique
class ErdApplianceType(enum.Enum):
    UNKNOWN = "FF"
    WATER_HEATER = "00"
    DRYER = "01"
    WASHER = "02"
    FRIDGE = "03"
    MICROWAVE = "04"
    ADVANTIUM = "05"
    DISH_WASHER = "06"
    OVEN = "07"
    ELECTRIC_RANGE = "08"
    GAS_RANGE = "09"
    AIR_CONDITIONER = "0a"
    ELECTRIC_COOKTOP = "0b"
    COOKTOP = "11"
    PIZZA_OVEN = "0c"
    GAS_COOKTOP = "0d"
    SPLIT_AIR_CONDITIONER = "0e"
    HOOD = "0f"
    POE_WATER_FILTER = "10"
    WATER_SOFTENER = "15"
    PORTABLE_AIR_CONDITIONER = "16"
    COMBINATION_WASHER_DRYER = "17"
    ZONELINE = "14"
    DELEVERY_BOX = "12"
    CAFE_COFFEE_MAKER = "1A"

@enum.unique
class ErdMeasurementUnits(enum.Enum):
    IMPERIAL = 0
    METRIC = 1

@enum.unique
class ErdOnOff(enum.Enum):
    ON = "01"
    OFF = "00"
    NA = "FF"

@enum.unique
class ErdPresent(enum.Enum):
    PRESENT = "01"
    NOT_PRESENT = "00"
    NA = "FF"

@enum.unique
class ErdEndTone(enum.Enum):
    BEEP = "00"
    REPEATED_BEEP = "01"
    NA = "FF"

@enum.unique
class ErdSoundLevel(enum.Enum):
    OFF = 0
    LOW = 1
    STANDARD = 2
    HIGH = 3

@enum.unique
class ErdClockFormat(enum.Enum):
    TWELVE_HOUR = "00"
    TWENTY_FOUR_HOUR = "01"
    NO_DISPLAY = "02"
