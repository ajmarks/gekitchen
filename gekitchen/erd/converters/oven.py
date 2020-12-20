""" ERD Converters for oven """

__all__ = (
    "ErdOvenStateConverter",
    "ErdAvailableCookModeConverter",
    "OvenCookModeConverter",
    "OvenConfigurationConverter",
    "OvenRangesConverter"
)

from .abstract import ErdReadOnlyConverter, ErdValueConverter
from .primitives import *
from gekitchen.erd.values.oven import *

class ErdOvenStateConverter(ErdReadOnlyConverter[ErdOvenState]):
    def erd_decode(self, value: str) -> ErdOvenState:
        """
        See erdCurrentState.smali
        """
        state_code = erd_decode_int(value)
        if 44 <= state_code <= 59:
            return ErdOvenState.OVEN_STATE_SPECIAL_X
        if 42 <= state_code <= 43:
            return ErdOvenState.OVEN_STATE_BAKED_GOODS
        if 40 <= state_code <= 41:
            return ErdOvenState.OVEN_STATE_FROZEN_PIZZA_MULTI
        if 38 <= state_code <= 39:
            return ErdOvenState.OVEN_STATE_FROZEN_SNACKS_MULTI
        if 36 <= state_code <= 37:
            return ErdOvenState.OVEN_STATE_FROZEN_PIZZA
        if 33 <= state_code <= 35:
            return ErdOvenState.OVEN_STATE_FROZEN_SNACKS
        if 1 <= state_code <= 27:
            # These 27 were nicely enumerated in v1.0.3 of the app, though the display logic is more similar to
            # to those above, grouping similar things. See ErdCurrentState.smali for more details.
            return ErdOvenState(state_code)
        return ErdOvenState.STATUS_DASH

class ErdAvailableCookModeConverter(ErdReadOnlyConverter[ErdAvailableCookMode]):
    def erd_decode(self, value: str) -> ErdAvailableCookMode:
        if not value:
            return {ErdAvailableCookMode.OVEN_BAKE.value.cook_mode}
        mode_bytes = [int(i) for i in erd_decode_bytes(value)]
        available_modes = {
            mode.value.cook_mode
            for mode in ErdAvailableCookMode
            if mode_bytes[mode.value.byte] & mode.value.mask
        }
        return available_modes

class OvenCookModeConverter(ErdValueConverter[OvenCookSetting]):
    def erd_decode(self, value: str) -> OvenCookSetting:
        """
        Get the cook mode and temperature.
        TODO: Figure out what the other 10 bytes are for.
            I'm guessing they have to do with two-temp cooking, probes, delayed starts, timers, etc.
        """
        byte_string = erd_decode_bytes(value)
        cook_mode_code = byte_string[0]
        temperature = int.from_bytes(byte_string[1:3], 'big')
        cook_mode = ErdOvenCookMode(cook_mode_code)
        return OvenCookSetting(cook_mode=OVEN_COOK_MODE_MAP[cook_mode], temperature=temperature, raw_bytes=byte_string)
    def erd_encode(self, value: OvenCookSetting) -> str:
        """Re-encode a cook mode and temperature
        TODO: Other ten bytes"""
        cook_mode = value.cook_mode
        cook_mode_code = OVEN_COOK_MODE_MAP.inverse[cook_mode].value
        cook_mode_hex = cook_mode_code.to_bytes(1, 'big').hex()
        temperature_hex = int(value.temperature).to_bytes(2, 'big').hex()
        return cook_mode_hex + temperature_hex + ('00' * 10)

class OvenConfigurationConverter(ErdReadOnlyConverter[OvenConfiguration]):
    def erd_decode(self, value: str) -> OvenConfiguration:
        if not value:
            n = 0
        else:
            n = erd_decode_int(value)

        config = OvenConfiguration(
            has_knob=bool(n & ErdOvenConfiguration.HAS_KNOB.value),
            has_warming_drawer=bool(n & ErdOvenConfiguration.HAS_WARMING_DRAWER.value),
            has_light_bar=bool(n & ErdOvenConfiguration.HAS_LIGHT_BAR.value),
            has_lower_oven=bool(n & ErdOvenConfiguration.HAS_LOWER_OVEN.value),
            has_lower_oven_kitchen_timer=bool(n & ErdOvenConfiguration.HAS_LOWER_OVEN_KITCHEN_TIMER.value),
            raw_value=value,
        )
        return config

class OvenRangesConverter(ErdReadOnlyConverter[OvenRanges]):  
    def erd_decode(self, value: str) -> OvenRanges:
        raw_bytes = bytes.fromhex(value)
        upper_temp = int.from_bytes(raw_bytes[:2], 'big')
        lower_temp = int.from_bytes(raw_bytes[-2:], 'big')
        return OvenRanges(
            lower=lower_temp, 
            upper=upper_temp
        )
