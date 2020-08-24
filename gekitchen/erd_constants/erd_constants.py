"""Constants for handling ERD values"""

__all__ = (
    "ErdApplianceType",
    "ErdAvailableCookMode",
    "ErdClockFormat",
    "ErdDoorStatus",
    "ErdEndTone",
    "ErdFilterStatus",
    "ErdFullNotFull",
    "ErdHotWaterStatus",
    "ErdMeasurementUnits",
    "ErdOnOff",
    "ErdOvenConfiguration",
    "ErdOvenCookMode",
    "ErdOvenState",
    "ErdPodStatus",
    "ErdPresent",
    "ErdSoundLevel",
    "OVEN_COOK_MODE_MAP",
)

import enum
import bidict
from ..erd_types import AvailableCookMode, OvenCookMode


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
class ErdOvenCookMode(enum.Enum):
    """See ErdCookMode.smali"""
    BAKED_GOODS = 60
    BAKETIMEDSHUTOFF_DELAYSTART = 7
    BAKETIMED_TWOTEMP = 5
    BAKETIMED_TWOTEMP_DELAYSTART = 9
    BAKETIMED_WARM = 4
    BAKETIMED_WARM_DELAYSTART = 8
    BAKE_DELAYSTART = 3
    BAKE_NOOPTION = 1
    BAKE_PROBE = 2
    BAKE_PROBE_DELAYSTART = 6
    BAKE_SABBATH = 10
    BROIL_HIGH = 12
    BROIL_LOW = 11
    CONVBAKETIMEDSHUTOFF_DELAYSTART = 24
    CONVBAKETIMED_TWOTEMP = 22
    CONVBAKETIMED_TWOTEMP_DELAYSTART = 26
    CONVBAKETIMED_WARM = 21
    CONVBAKETIMED_WARM_DELAYSTART = 25
    CONVBAKE_DELAYSTART = 20
    CONVBAKE_NOOPTION = 18
    CONVBAKE_PROBE = 19
    CONVBAKE_PROBE_DELAYSTART = 23
    CONVBROILCRISP_NOOPTION = 47
    CONVBROILCRISP_PROBE = 48
    CONVBROIL_HIGH_NOOPTION = 46
    CONVBROIL_LOW_NOOPTION = 45
    CONVMULTIBAKETIMEDSHUTOFF_DELAYSTART = 33
    CONVMULTIBAKETIMED_TWOTEMP = 31
    CONVMULTIBAKETIMED_TWOTEMP_DELAYSTART = 35
    CONVMULTIBAKETIMED_WARM = 30
    CONVMULTIBAKETIMED_WARM_DELAYSTART = 34
    CONVMULTIBAKE_DELAYSTART = 29
    CONVMULTIBAKE_NOOPTION = 27
    CONVMULTIBAKE_PROBE = 28
    CONVMULTIBAKE_PROBE_DELAYSTART = 32
    CONVROASTTIMEDSHUTOFF_DELAYSTART = 42
    CONVROASTTIMED_TWOTEMP = 40
    CONVROASTTIMED_TWOTEMP_DELAYSTART = 44
    CONVROASTTIMED_WARM = 39
    CONVROASTTIMED_WARM_DELAYSTART = 43
    CONVROAST_DELAYSTART = 38
    CONVROAST_NOOPTION = 36
    CONVROAST_PROBE = 37
    CONVROAST_PROBE_DELAYSTART = 41
    CUSTOMSELFCLEAN = 49
    CUSTOMSELFCLEAN_DELAYSTART = 50
    DUALBROIL_HIGH_NOOPTION = 54
    DUALBROIL_LOW_NOOPTION = 53
    FROZEN_PIZZA = 58
    FROZEN_PIZZA_MULTI = 59
    FROZEN_SNACKS = 56
    FROZEN_SNACKS_MULTI = 567
    NOMODE = 0
    PROOF_DELAYSTART = 14
    PROOF_NOOPTION = 13
    STEAMCLEAN = 51
    STEAMCLEAN_DELAYSTART = 52
    WARM_DELAYSTART = 17
    WARM_NOOPTION = 15
    WARM_PROBE = 16


@enum.unique
class ErdAvailableCookMode(enum.Enum):
    """
    Available cooking modes.
    In the XMPP API, they are represented as an index into an array of bytes and a bitmask.
    Thus these take the form (byte: int, mask: int, cook_mode: ErdOvenCookMode).  See ErdAvailableCookMode.smali
    in the Android app.
    """
    OVEN_BAKE = AvailableCookMode(byte=9, mask=2, cook_mode=ErdOvenCookMode.BAKE_NOOPTION)
    OVEN_CONVECTION_BAKE = AvailableCookMode(byte=7, mask=4, cook_mode=ErdOvenCookMode.CONVBAKE_NOOPTION)
    OVEN_CONVECTION_MULTI_BAKE = AvailableCookMode(byte=6, mask=8, cook_mode=ErdOvenCookMode.CONVMULTIBAKE_NOOPTION)
    OVEN_CONVECTION_ROAST = AvailableCookMode(byte=5, mask=16, cook_mode=ErdOvenCookMode.CONVROAST_NOOPTION)
    OVEN_FROZEN_SNACKS = AvailableCookMode(byte=2, mask=1, cook_mode=ErdOvenCookMode.FROZEN_SNACKS)
    OVEN_FROZEN_SNACKS_MULTI = AvailableCookMode(byte=2, mask=2, cook_mode=ErdOvenCookMode.FROZEN_SNACKS_MULTI)
    OVEN_FROZEN_PIZZA = AvailableCookMode(byte=2, mask=4, cook_mode=ErdOvenCookMode.FROZEN_PIZZA)
    OVEN_FROZEN_PIZZA_MULTI = AvailableCookMode(byte=2, mask=8, cook_mode=ErdOvenCookMode.FROZEN_PIZZA_MULTI)
    OVEN_BAKED_GOODS = AvailableCookMode(byte=2, mask=16, cook_mode=ErdOvenCookMode.BAKED_GOODS)


@enum.unique
class ErdOvenConfiguration(enum.Enum):
    """Representation of oven configurations."""
    HAS_KNOB = 1
    HAS_WARMING_DRAWER = 2
    HAS_LIGHT_BAR = 4
    HAS_LOWER_OVEN = 8
    HAS_LOWER_OVEN_KITCHEN_TIMER = 16


@enum.unique
class ErdOvenState(enum.Enum):
    """
    Oven state constants for display purposes.
    These are found in ErdCurrentState.smali.  That they are not aligned with the values for
    ErdCookMode and AvailableCookMode is infuriating.
    """
    BAKE = 5
    BAKE_PREHEAT = 1
    BAKE_TWO_TEMP = 6
    BROIL_HIGH = 14
    BROIL_LOW = 13
    CLEAN_COOL_DOWN = 23
    CLEAN_STAGE1 = 21
    CLEAN_STAGE2 = 22
    CONV_BAKE = 7
    CONV_BAKE_PREHEAT = 2
    CONV_BAKE_TWO_TEMP = 8
    CONV_BROIL_CRISP = 17
    CONV_BROIL_HIGH = 15
    CONV_BROIL_LOW = 16
    CONV_MULTI_BAKE_PREHEAT = 3
    CONV_MULTI_TWO_BAKE = 10
    CONV_MUTLI_BAKE = 9
    CONV_ROAST = 11
    CONV_ROAST2 = 12
    CONV_ROAST_BAKE_PREHEAT = 4
    CUSTOM_CLEAN_STAGE2 = 24
    DELAY = 27
    NO_MODE = 0
    PROOF = 19
    SABBATH = 20
    STEAM_CLEAN_STAGE2 = 25
    STEAM_COOL_DOWN = 26
    WARM = 18
    OVEN_STATE_BAKE = "oven_bake"
    OVEN_STATE_BAKED_GOODS = "oven_state_baked_goods"
    OVEN_STATE_BROIL = "oven_state_broil"
    OVEN_STATE_CONV_BAKE = "oven_state_conv_bake"
    OVEN_STATE_CONV_BAKE_MULTI = "oven_state_conv_bake_multi"
    OVEN_STATE_CONV_BROIL = "oven_state_conv_broil"
    OVEN_STATE_CONV_ROAST = "oven_state_conv_roast"
    OVEN_STATE_DELAY_START = "oven_state_delay_start"
    OVEN_STATE_DUAL_BROIL_HIGH = "oven_state_dual_broil_high"
    OVEN_STATE_DUAL_BROIL_LOW = "oven_state_dual_broil_low"
    OVEN_STATE_FROZEN_PIZZA = "oven_state_frozen_pizza"
    OVEN_STATE_FROZEN_PIZZA_MULTI = "oven_state_frozen_pizza_multi"
    OVEN_STATE_FROZEN_SNACKS = "oven_state_frozen_snacks"
    OVEN_STATE_FROZEN_SNACKS_MULTI = "oven_state_frozen_snacks_multi"
    OVEN_STATE_PROOF = "oven_state_proof"
    OVEN_STATE_SELF_CLEAN = "oven_state_self_clean"
    OVEN_STATE_SPECIAL_X = "oven_state_speical_x"  # [sic.]
    OVEN_STATE_STEAM_START = "oven_state_steam_start"
    OVEN_STATE_WARM = "oven_state_warm"
    STATUS_DASH = "status_dash"


# Translate OVEN_COOK_MODE values into something easier to work with
OVEN_COOK_MODE_MAP = bidict.bidict({
    ErdOvenCookMode.BAKED_GOODS: OvenCookMode(ErdOvenState.OVEN_STATE_BAKED_GOODS, False, False, False),
    ErdOvenCookMode.BAKETIMEDSHUTOFF_DELAYSTART: OvenCookMode(ErdOvenState.BAKE, True, True, False),
    ErdOvenCookMode.BAKETIMED_TWOTEMP: OvenCookMode(ErdOvenState.BAKE_TWO_TEMP, False, True, False),
    ErdOvenCookMode.BAKETIMED_TWOTEMP_DELAYSTART: OvenCookMode(ErdOvenState.BAKE_TWO_TEMP, True, True, False),
    ErdOvenCookMode.BAKETIMED_WARM: OvenCookMode(ErdOvenState.WARM, False, True, False),
    ErdOvenCookMode.BAKETIMED_WARM_DELAYSTART: OvenCookMode(ErdOvenState.WARM, True, True, False),
    ErdOvenCookMode.BAKE_DELAYSTART: OvenCookMode(ErdOvenState.BAKE, True, False, False),
    ErdOvenCookMode.BAKE_NOOPTION: OvenCookMode(ErdOvenState.BAKE, False, False, False),
    ErdOvenCookMode.BAKE_PROBE: OvenCookMode(ErdOvenState.BAKE, False, False, True),
    ErdOvenCookMode.BAKE_PROBE_DELAYSTART: OvenCookMode(ErdOvenState.BAKE, True, False, True),
    ErdOvenCookMode.BAKE_SABBATH: OvenCookMode(ErdOvenState.BAKE, False, False, False, False, True),
    ErdOvenCookMode.BROIL_HIGH: OvenCookMode(ErdOvenState.BROIL_HIGH, False, False, False),
    ErdOvenCookMode.BROIL_LOW: OvenCookMode(ErdOvenState.BROIL_LOW, False, False, False),
    ErdOvenCookMode.CONVBAKETIMEDSHUTOFF_DELAYSTART: OvenCookMode(ErdOvenState.CONV_BAKE, True, True, False),
    ErdOvenCookMode.CONVBAKETIMED_TWOTEMP: OvenCookMode(ErdOvenState.CONV_BAKE_TWO_TEMP, False, True, False),
    ErdOvenCookMode.CONVBAKETIMED_TWOTEMP_DELAYSTART: OvenCookMode(ErdOvenState.CONV_BAKE_TWO_TEMP, True, True, False),
    ErdOvenCookMode.CONVBAKETIMED_WARM: OvenCookMode(ErdOvenState.CONV_BAKE, False, True, False, True),
    ErdOvenCookMode.CONVBAKETIMED_WARM_DELAYSTART: OvenCookMode(ErdOvenState.CONV_BAKE, True, True, False, True),
    ErdOvenCookMode.CONVBAKE_DELAYSTART: OvenCookMode(ErdOvenState.CONV_BAKE, True, False, False),
    ErdOvenCookMode.CONVBAKE_NOOPTION: OvenCookMode(ErdOvenState.CONV_BAKE, False, False, False),
    ErdOvenCookMode.CONVBAKE_PROBE: OvenCookMode(ErdOvenState.CONV_BAKE, False, False, True),
    ErdOvenCookMode.CONVBAKE_PROBE_DELAYSTART: OvenCookMode(ErdOvenState.CONV_BAKE, True, False, True),
    ErdOvenCookMode.CONVBROILCRISP_NOOPTION: OvenCookMode(ErdOvenState.CONV_BROIL_CRISP, False, False, False),
    ErdOvenCookMode.CONVBROILCRISP_PROBE: OvenCookMode(ErdOvenState.CONV_BROIL_CRISP, False, False, True),
    ErdOvenCookMode.CONVBROIL_HIGH_NOOPTION: OvenCookMode(ErdOvenState.CONV_BROIL_HIGH, False, False, False),
    ErdOvenCookMode.CONVBROIL_LOW_NOOPTION: OvenCookMode(ErdOvenState.CONV_BROIL_LOW, False, False, False),
    ErdOvenCookMode.CONVMULTIBAKETIMEDSHUTOFF_DELAYSTART: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, True, True, False),
    ErdOvenCookMode.CONVMULTIBAKETIMED_TWOTEMP: OvenCookMode(ErdOvenState.CONV_MULTI_TWO_BAKE, False, True, False),
    ErdOvenCookMode.CONVMULTIBAKETIMED_TWOTEMP_DELAYSTART: OvenCookMode(ErdOvenState.CONV_MULTI_TWO_BAKE, True, True, False),
    ErdOvenCookMode.CONVMULTIBAKETIMED_WARM: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, False, True, False, True),
    ErdOvenCookMode.CONVMULTIBAKETIMED_WARM_DELAYSTART: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, True, True, False, True),
    ErdOvenCookMode.CONVMULTIBAKE_DELAYSTART: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, True, False, False),
    ErdOvenCookMode.CONVMULTIBAKE_NOOPTION: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, False, False, False),
    ErdOvenCookMode.CONVMULTIBAKE_PROBE: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, False, False, True),
    ErdOvenCookMode.CONVMULTIBAKE_PROBE_DELAYSTART: OvenCookMode(ErdOvenState.CONV_MUTLI_BAKE, True, False, True),
    ErdOvenCookMode.CONVROASTTIMEDSHUTOFF_DELAYSTART: OvenCookMode(ErdOvenState.CONV_ROAST, True, True, False),
    ErdOvenCookMode.CONVROASTTIMED_TWOTEMP: OvenCookMode(ErdOvenState.CONV_ROAST2, False, True, False),
    ErdOvenCookMode.CONVROASTTIMED_TWOTEMP_DELAYSTART: OvenCookMode(ErdOvenState.CONV_ROAST2, True, True, False),
    ErdOvenCookMode.CONVROASTTIMED_WARM: OvenCookMode(ErdOvenState.CONV_ROAST, False, True, False, True),
    ErdOvenCookMode.CONVROASTTIMED_WARM_DELAYSTART: OvenCookMode(ErdOvenState.CONV_ROAST, True, True, False, True),
    ErdOvenCookMode.CONVROAST_DELAYSTART: OvenCookMode(ErdOvenState.CONV_ROAST, True, False, False),
    ErdOvenCookMode.CONVROAST_NOOPTION: OvenCookMode(ErdOvenState.CONV_ROAST, False, False, False),
    ErdOvenCookMode.CONVROAST_PROBE: OvenCookMode(ErdOvenState.CONV_ROAST, False, False, True),
    ErdOvenCookMode.CONVROAST_PROBE_DELAYSTART: OvenCookMode(ErdOvenState.CONV_ROAST, True, False, True),
    ErdOvenCookMode.CUSTOMSELFCLEAN: OvenCookMode(ErdOvenState.CUSTOM_CLEAN_STAGE2, False, False, False),
    ErdOvenCookMode.CUSTOMSELFCLEAN_DELAYSTART: OvenCookMode(ErdOvenState.CUSTOM_CLEAN_STAGE2, True, False, False),
    ErdOvenCookMode.DUALBROIL_HIGH_NOOPTION: OvenCookMode(ErdOvenState.OVEN_STATE_DUAL_BROIL_HIGH, False, False, False),
    ErdOvenCookMode.DUALBROIL_LOW_NOOPTION: OvenCookMode(ErdOvenState.OVEN_STATE_DUAL_BROIL_LOW, False, False, False),
    ErdOvenCookMode.FROZEN_PIZZA: OvenCookMode(ErdOvenState.OVEN_STATE_FROZEN_PIZZA, False, False, False),
    ErdOvenCookMode.FROZEN_PIZZA_MULTI: OvenCookMode(ErdOvenState.OVEN_STATE_FROZEN_PIZZA_MULTI, False, False, False),
    ErdOvenCookMode.FROZEN_SNACKS: OvenCookMode(ErdOvenState.OVEN_STATE_FROZEN_SNACKS, False, False, False),
    ErdOvenCookMode.FROZEN_SNACKS_MULTI: OvenCookMode(ErdOvenState.OVEN_STATE_FROZEN_SNACKS_MULTI, False, False, False),
    ErdOvenCookMode.NOMODE: OvenCookMode(ErdOvenState.NO_MODE, False, False, False),
    ErdOvenCookMode.PROOF_DELAYSTART: OvenCookMode(ErdOvenState.PROOF, True, False, False),
    ErdOvenCookMode.PROOF_NOOPTION: OvenCookMode(ErdOvenState.PROOF, False, False, False),
    ErdOvenCookMode.STEAMCLEAN: OvenCookMode(ErdOvenState.STEAM_CLEAN_STAGE2, False, False, False),
    ErdOvenCookMode.STEAMCLEAN_DELAYSTART: OvenCookMode(ErdOvenState.STEAM_CLEAN_STAGE2, True, False, False),
    ErdOvenCookMode.WARM_DELAYSTART: OvenCookMode(ErdOvenState.WARM, True, False, False),
    ErdOvenCookMode.WARM_NOOPTION: OvenCookMode(ErdOvenState.WARM, False, False, False),
    ErdOvenCookMode.WARM_PROBE: OvenCookMode(ErdOvenState.WARM, False, False, True),
})


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
