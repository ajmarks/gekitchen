"""Constants for handling ERD values"""

import enum
from ..erd_types import AvailableCookMode


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
