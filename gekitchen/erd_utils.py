"""Conversion functions for ERD values"""

from datetime import timedelta
import logging
from typing import Any, Optional, Set, Tuple, Union
from .erd_constants import (
    ErdApplianceType,
    ErdCode,
    ErdMeasurementUnits,
    ErdAvailableCookMode,
    ErdOvenConfiguration,
    ErdOvenCookMode,
    ErdOvenState,
)
from .erd_types import AvailableCookMode, OvenCookSetting, OvenConfiguration

ErdCodeType = Union[ErdCode, str]

_LOGGER = logging.getLogger(__name__)


def translate_erd_code(erd_code: ErdCodeType) -> ErdCodeType:
    """
    Try to resolve an ERD codes from string to ErdCode if possible.  If an ErdCode
    object is passed in, it will be returned.
    :param erd_code: ErdCode or str
    :return: Either an ErdCode object matching the `erd_code` string, or, if resolution fails,
    the `erd_code` string itself.
    """
    if isinstance(erd_code, ErdCode):
        return erd_code

    try:
        return ErdCode[erd_code]
    except KeyError:
        pass

    try:
        return ErdCode(erd_code)
    except ValueError:
        # raise UnknownErdCode(f"Unable to resolve erd_code '{erd_code}'")
        return erd_code


def decode_erd_int(value: str) -> int:
    """Decode an integer value sent as a hex encoded string."""
    return int(value, 16)


def _encode_erd_int(value: int) -> str:
    """Encode an integer value as a hex string."""
    return value.to_bytes(2, 'big').hex()


def _decode_erd_string(value: str) -> str:
    """
    Decode an string value sent as a hex encoded string.

    TODO: I think the first byte is a checksum.  I need to confirm this so we can have an encoder as well.
    """
    raw_bytes = bytes.fromhex(value)
    raw_bytes = raw_bytes.rstrip(b'\x00')

    return raw_bytes[1:].decode('ascii')


def decode_erd_bytes(value: str) -> bytes:
    """Decode a raw bytes ERD value sent as a hex encoded string."""
    return bytes.fromhex(value)


def _encode_erd_bytes(value: bytes) -> str:
    """Encode a raw bytes ERD value."""
    return value.hex('big')


def _decode_erd_bool(value: str) -> bool:
    return bool(int(value))


def _encode_erd_bool(value: bool) -> str:
    return "01" if value else "00"


def _decode_oven_ranges(value: str) -> Tuple[int, int]:
    raw_bytes = bytes.fromhex(value)
    upper_temp = int.from_bytes(raw_bytes[:2], 'big')
    lower_temp = int.from_bytes(raw_bytes[-2:], 'big')
    return lower_temp, upper_temp


def _decode_appliance_type(value: str) -> ErdApplianceType:
    try:
        return ErdApplianceType(value)
    except ValueError:
        return ErdApplianceType.UNKNOWN


def _decode_measurement_unit(value: str) -> str:
    return ErdMeasurementUnits(int(value))


def _encode_measurement_unit(value: ErdMeasurementUnits) -> str:
    return f'{value.value:02d}'


def _decode_timespan(value: str) -> Optional[timedelta]:
    minutes = decode_erd_int(value)
    if minutes == 65535:
        _LOGGER.debug('Got timespan value of 65535. Treating as None.')
        return None
    return timedelta(minutes=minutes)


def _encode_timespan(value: Optional[timedelta]) -> str:
    if value is None:
        minutes = 65535
    else:
        minutes = value.seconds // 60
    return _encode_erd_int(minutes)


def _decode_cook_modes(value: str) -> Set[AvailableCookMode]:
    if not value:
        return {ErdAvailableCookMode.OVEN_BAKE.value.cook_mode}
    mode_bytes = [int(i) for i in decode_erd_bytes(value)]
    available_modes = {
        mode.value.cook_mode
        for mode in ErdAvailableCookMode
        if mode_bytes[mode.value.byte] & mode.value.mask
    }
    return available_modes


def _decode_oven_state(value: str) -> ErdOvenState:
    """
    See erdCurrentState.smali
    """
    state_code = decode_erd_int(value)
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


def _decode_oven_cook_mode(value: str) -> OvenCookSetting:
    """
    Get the cook mode and temperature.
    TODO: Figure out what the other 10 bytes are for
    """
    byte_string = decode_erd_bytes(value)
    cook_mode_code = byte_string[0]
    temperature = int.from_bytes(byte_string[1:3], 'big')
    return OvenCookSetting(cook_mode=ErdOvenCookMode(cook_mode_code), temperature=temperature, raw_bytes=byte_string)


def _encode_oven_cook_mode(cook_setting: OvenCookSetting) -> str:
    """Re-encode a cook mode and temperature
    TODO: Other ten bytes"""
    cook_mode_code = cook_setting.cook_mode.value
    cook_mode_hex = cook_mode_code.to_bytes(1, 'big').hex()
    temperature_hex = cook_setting.temperature.to_bytes(2, 'big').hex()
    return cook_mode_hex + temperature_hex + ('00' * 10)


def _decode_oven_configuration(value: str) -> OvenConfiguration:
    if not value:
        n = 0
    else:
        n = decode_erd_int(value)

    config = OvenConfiguration(
        has_knob=bool(n & ErdOvenConfiguration.HAS_KNOB.value),
        has_warming_drawer=bool(n & ErdOvenConfiguration.HAS_WARMING_DRAWER.value),
        has_light_bar=bool(n & ErdOvenConfiguration.HAS_LIGHT_BAR.value),
        has_lower_oven=bool(n & ErdOvenConfiguration.HAS_LOWER_OVEN.value),
        has_lower_oven_kitchen_timer=bool(n & ErdOvenConfiguration.HAS_LOWER_OVEN_KITCHEN_TIMER.value),
        raw_value=value,
    )
    return config


# Decoders for non-numeric fields
ERD_DECODERS = {
    # Integers
    ErdCode.CLOCK_FORMAT: decode_erd_int,
    ErdCode.END_TONE: decode_erd_int,
    ErdCode.SOUND_LEVEL: decode_erd_int,
    ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE: decode_erd_int,
    ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP: decode_erd_int,
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE: decode_erd_int,
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET: decode_erd_int,
    ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE: decode_erd_int,
    ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP: decode_erd_int,
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE: decode_erd_int,
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET: decode_erd_int,

    # Strings
    ErdCode.MODEL_NUMBER: _decode_erd_string,
    ErdCode.SERIAL_NUMBER: _decode_erd_string,

    # Booleans
    ErdCode.CONVECTION_CONVERSION: _decode_erd_bool,
    ErdCode.HOUR_12_SHUTOFF_ENABLED: _decode_erd_bool,
    ErdCode.SABBATH_MODE: _decode_erd_bool,
    ErdCode.LOWER_OVEN_PROBE_PRESENT: _decode_erd_bool,
    ErdCode.LOWER_OVEN_REMOTE_ENABLED: _decode_erd_bool,
    ErdCode.UPPER_OVEN_PROBE_PRESENT: _decode_erd_bool,
    ErdCode.UPPER_OVEN_REMOTE_ENABLED: _decode_erd_bool,

    # Time spans
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING: _decode_timespan,
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING: _decode_timespan,
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME: _decode_timespan,
    ErdCode.LOWER_OVEN_KITCHEN_TIMER: _decode_timespan,
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING: _decode_timespan,
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING: _decode_timespan,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME: _decode_timespan,
    ErdCode.UPPER_OVEN_KITCHEN_TIMER: _decode_timespan,

    # Special handling
    ErdCode.APPLIANCE_TYPE: _decode_appliance_type,
    ErdCode.OVEN_CONFIGURATION: _decode_oven_configuration,
    ErdCode.OVEN_MODE_MIN_MAX_TEMP: _decode_oven_ranges,
    ErdCode.TEMPERATURE_UNIT: _decode_measurement_unit,
    ErdCode.LOWER_OVEN_CURRENT_STATE: _decode_oven_state,
    ErdCode.LOWER_OVEN_AVAILABLE_COOK_MODES: _decode_cook_modes,
    ErdCode.LOWER_OVEN_COOK_MODE: _decode_oven_cook_mode,
    ErdCode.UPPER_OVEN_CURRENT_STATE: _decode_oven_state,
    ErdCode.UPPER_OVEN_AVAILABLE_COOK_MODES: _decode_cook_modes,
    ErdCode.UPPER_OVEN_COOK_MODE: _decode_oven_cook_mode,
}

# Encoders for all fields
ERD_ENCODERS = {
    # Time spans
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING: _encode_timespan,
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING: _encode_timespan,
    ErdCode.LOWER_OVEN_KITCHEN_TIMER: _encode_timespan,
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING: _encode_timespan,
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING: _encode_timespan,
    ErdCode.UPPER_OVEN_KITCHEN_TIMER: _encode_timespan,

    # Booleans
    ErdCode.CONVECTION_CONVERSION: _encode_erd_bool,
    ErdCode.SABBATH_MODE: _encode_erd_bool,

    # Special handling
    ErdCode.LOWER_OVEN_COOK_MODE: _encode_oven_cook_mode,
    ErdCode.UPPER_OVEN_COOK_MODE: _encode_oven_cook_mode,
    ErdCode.TEMPERATURE_UNIT: _encode_measurement_unit,
}
