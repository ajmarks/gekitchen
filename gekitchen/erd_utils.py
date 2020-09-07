"""Conversion functions for ERD values"""

import logging
from datetime import timedelta
from textwrap import wrap
from typing import Optional, Set, Tuple, Union
from .erd_constants import *
from .erd_types import *

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
        return ErdCode(erd_code.lower())
    except ValueError:
        # raise UnknownErdCode(f"Unable to resolve erd_code '{erd_code}'")
        return erd_code


def decode_erd_int(value: str) -> int:
    """Decode an integer value sent as a hex encoded string."""
    return int(value, 16)


def decode_signed_byte(value: str) -> int:
    """
    Convert a hex byte to a signed int.  Copied from GE's hextodec method.
    """
    val = int(value, 16)
    if val > 128:
        return val - 256
    return val


def encode_signed_byte(value: int) -> str:
    """
    Convert a hex byte to a signed int.  Copied from GE's hextodec method.
    """
    value = int(value)
    if value < 0:
        value = value + 256
    return value.to_bytes(1, "big").hex()


def _encode_erd_int(value: int) -> str:
    """Encode an integer value as a hex string."""
    value = int(value)
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


def _decode_erd_bool(value: str) -> Optional[bool]:
    if value == "FF":
        return None
    return bool(int(value))


def _encode_erd_bool(value: Optional[bool]) -> str:
    if value is None:
        return "FF"
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
    TODO: Figure out what the other 10 bytes are for.
        I'm guessing they have to do with two-temp cooking, probes, delayed starts, timers, etc.
    """
    byte_string = decode_erd_bytes(value)
    cook_mode_code = byte_string[0]
    temperature = int.from_bytes(byte_string[1:3], 'big')
    cook_mode = ErdOvenCookMode(cook_mode_code)
    return OvenCookSetting(cook_mode=OVEN_COOK_MODE_MAP[cook_mode], temperature=temperature, raw_bytes=byte_string)


def _encode_oven_cook_mode(cook_setting: OvenCookSetting) -> str:
    """Re-encode a cook mode and temperature
    TODO: Other ten bytes"""
    cook_mode = cook_setting.cook_mode
    cook_mode_code = OVEN_COOK_MODE_MAP.inverse[cook_mode].value
    cook_mode_hex = cook_mode_code.to_bytes(1, 'big').hex()
    temperature_hex = int(cook_setting.temperature).to_bytes(2, 'big').hex()
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


def _decode_ice_bucket_status(value: str) -> FridgeIceBucketStatus:
    """Decode Ice bucket status"""
    if not value:
        n = 0
    else:
        n = decode_erd_int(value)

    is_present_ff = bool(n & 1)
    is_present_fz = bool(n & 2)
    state_full_ff = ErdFullNotFull.FULL if n & 4 else ErdFullNotFull.NOT_FULL
    state_full_fz = ErdFullNotFull.FULL if n & 8 else ErdFullNotFull.NOT_FULL

    if not is_present_ff:
        state_full_ff = ErdFullNotFull.NA
    if not is_present_fz:
        state_full_fz = ErdFullNotFull.NA

    if not (is_present_ff or is_present_ff):
        # No ice buckets at all
        total_status = ErdFullNotFull.NA
    elif (state_full_ff == ErdFullNotFull.NOT_FULL) or (state_full_fz == ErdFullNotFull.NOT_FULL):
        # At least one bucket is not full
        total_status = ErdFullNotFull.NOT_FULL
    else:
        total_status = ErdFullNotFull.FULL

    ice_status = FridgeIceBucketStatus(
        state_full_fridge=state_full_ff,
        state_full_freezer=state_full_fz,
        is_present_fridge=is_present_ff,
        is_present_freezer=is_present_fz,
        total_status=total_status,
    )
    return ice_status


def _decode_ice_maker_control(value: str) -> IceMakerControlStatus:
    def parse_status(val: str) -> ErdOnOff:
        try:
            return ErdOnOff(val)
        except ValueError:
            return ErdOnOff.NA

    status_fz = parse_status(value[:2])
    status_ff = parse_status(value[2:])

    return IceMakerControlStatus(status_fridge=status_ff, status_freezer=status_fz)


def _encode_ice_maker_control(value: IceMakerControlStatus) -> str:
    return value.status_freezer.value + value.status_fridge.value


def _decode_fridge_door(value: str) -> FridgeDoorStatus:
    def get_door_status(val: str) -> ErdDoorStatus:
        try:
            return ErdDoorStatus(val)
        except ValueError:
            return ErdDoorStatus.NA

    fridge_right = get_door_status(value[:2])
    fridge_left = get_door_status(value[2:4])
    freezer = get_door_status(value[4:6])
    drawer = get_door_status(value[6:8])
    if (fridge_right != ErdDoorStatus.OPEN) and (fridge_left != ErdDoorStatus.OPEN):
        if freezer == ErdDoorStatus.OPEN:
            status = "Freezer Open"
        else:
            status = "Closed"
    elif freezer == ErdDoorStatus.OPEN:
        status = "All Open"
    else:
        status = "Fridge Open"
    return FridgeDoorStatus(
        fridge_right=fridge_right,
        fridge_left=fridge_left,
        freezer=freezer,
        drawer=drawer,
        status=status,
    )


def _decode_fridge_limits(value: str) -> FridgeSetPointLimits:
    return FridgeSetPointLimits(
        fridge_min=decode_signed_byte(value[0:2]),
        fridge_max=decode_signed_byte(value[2:4]),
        freezer_min=decode_signed_byte(value[4:6]),
        freezer_max=decode_signed_byte(value[6:8]),
    )


def _decode_fridge_setpoint(value: str) -> FridgeSetPoints:
    return FridgeSetPoints(
        fridge=decode_signed_byte(value[0:2]),
        freezer=decode_signed_byte(value[2:4]),
    )


def _encode_fridge_setpoint(value: FridgeSetPoints) -> str:
    return encode_signed_byte(value.fridge) + encode_signed_byte(value.freezer)


def _decode_hot_water_status(value: str) -> HotWaterStatus:
    if not value:
        return HotWaterStatus(
            status=ErdHotWaterStatus.NA,
            time_until_ready=None,
            current_temp=None,
            tank_full=ErdFullNotFull.NA,
            brew_module=ErdPresent.NA,
            pod_status=ErdPodStatus.NA,
        )
    try:
        status = ErdHotWaterStatus(value[:2])
    except ValueError:
        status = ErdHotWaterStatus.NA

    time_until_ready = timedelta(minutes=decode_erd_int(value[2:6]))
    current_temp = decode_erd_int(value[6:8])

    try:
        tank_full = ErdFullNotFull(value[8:10])
    except ValueError:
        tank_full = ErdFullNotFull.NA

    try:
        brew_module = ErdPresent(value[10:12])
    except ValueError:
        brew_module = ErdPresent.NA

    try:
        pod_status = ErdPodStatus(value[12:14])
    except ValueError:
        pod_status = ErdPodStatus.NA

    return HotWaterStatus(
        status=status,
        time_until_ready=time_until_ready,
        current_temp=current_temp,
        tank_full=tank_full,
        brew_module=brew_module,
        pod_status=pod_status,
    )


def _decode_filter_status(value: str) -> ErdFilterStatus:
    """Decode water filter status.

    This appears to be 9 bytes, of which only the first two are obviously used. I suspect that the others
    relate to how much time remains on the filter.  Leaving as a TODO.
    """
    status_byte = value[:2]
    if status_byte == "00":
        status_byte = value[2:4]
    try:
        return ErdFilterStatus(status_byte)
    except ValueError:
        return ErdFilterStatus.NA


def _decode_sw_version(value: str) -> str:
    """
    Decode a software version string.
    These are sent as four bytes, encoding each part of a four-element version string.
    """
    vals = wrap(value, 2)
    return '.'.join(str(decode_erd_int(val)) for val in vals)


def _decode_end_tone(value: str) -> ErdEndTone:
    try:
        return ErdEndTone(value)
    except ValueError:
        return ErdEndTone.NA


def _encode_end_tone(value: ErdEndTone) -> str:
    if value == ErdEndTone.NA:
        raise ValueError("Invalid EndTone value")
    return value.value


def _decode_sound_level(value: str) -> ErdSoundLevel:
    sound_level = decode_erd_int(value)
    return ErdSoundLevel(sound_level)


def _encode_sound_level(value: ErdSoundLevel) -> str:
    return _encode_erd_int(value.value)


def _decode_clock_format(value: str) -> ErdClockFormat:
    return ErdClockFormat(value)


def _encode_clock_format(value: ErdClockFormat) -> str:
    return value.value


# Decoders for non-numeric fields

ERD_DECODERS = {
    ###################################################################
    # Integers
    ErdCode.HOT_WATER_SET_TEMP: decode_erd_int,
    ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE: decode_erd_int,
    ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP: decode_erd_int,
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE: decode_erd_int,
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET: decode_erd_int,
    ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE: decode_erd_int,
    ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP: decode_erd_int,
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE: decode_erd_int,
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET: decode_erd_int,

    ###################################################################
    # Strings
    ErdCode.MODEL_NUMBER: _decode_erd_string,
    ErdCode.SERIAL_NUMBER: _decode_erd_string,

    ###################################################################
    # Booleans
    ErdCode.CONVECTION_CONVERSION: _decode_erd_bool,
    ErdCode.HOT_WATER_IN_USE: _decode_erd_bool,
    ErdCode.HOUR_12_SHUTOFF_ENABLED: _decode_erd_bool,
    ErdCode.SABBATH_MODE: _decode_erd_bool,
    ErdCode.LOWER_OVEN_PROBE_PRESENT: _decode_erd_bool,
    ErdCode.LOWER_OVEN_REMOTE_ENABLED: _decode_erd_bool,
    ErdCode.UPPER_OVEN_PROBE_PRESENT: _decode_erd_bool,
    ErdCode.UPPER_OVEN_REMOTE_ENABLED: _decode_erd_bool,
    ErdCode.TURBO_FREEZE_STATUS: _decode_erd_bool,
    ErdCode.TURBO_COOL_STATUS: _decode_erd_bool,
    ErdCode.ACM_UPDATING: _decode_erd_bool,
    ErdCode.APPLIANCE_UPDATING: _decode_erd_bool,
    ErdCode.LCD_UPDATING: _decode_erd_bool,

    ###################################################################
    # Time spans
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING: _decode_timespan,
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING: _decode_timespan,
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME: _decode_timespan,
    ErdCode.LOWER_OVEN_KITCHEN_TIMER: _decode_timespan,
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING: _decode_timespan,
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING: _decode_timespan,
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME: _decode_timespan,
    ErdCode.UPPER_OVEN_KITCHEN_TIMER: _decode_timespan,

    ###################################################################
    # Special handling
    # Universal
    ErdCode.APPLIANCE_TYPE: _decode_appliance_type,
    ErdCode.CLOCK_FORMAT: _decode_clock_format,
    ErdCode.END_TONE: _decode_end_tone,
    ErdCode.SOUND_LEVEL: _decode_sound_level,
    ErdCode.TEMPERATURE_UNIT: _decode_measurement_unit,
    ErdCode.APPLIANCE_SW_VERSION: _decode_sw_version,
    ErdCode.APPLIANCE_SW_VERSION_AVAILABLE: _decode_sw_version,
    ErdCode.LCD_SW_VERSION: _decode_sw_version,
    ErdCode.LCD_SW_VERSION_AVAILABLE: _decode_sw_version,
    ErdCode.WIFI_MODULE_SW_VERSION: _decode_sw_version,
    ErdCode.WIFI_MODULE_SW_VERSION_AVAILABLE: _decode_sw_version,

    # Fridge
    ErdCode.DOOR_STATUS: _decode_fridge_door,
    ErdCode.HOT_WATER_STATUS: _decode_hot_water_status,
    ErdCode.ICE_MAKER_BUCKET_STATUS: _decode_ice_bucket_status,
    ErdCode.ICE_MAKER_CONTROL: _decode_ice_maker_control,
    ErdCode.SETPOINT_LIMITS: _decode_fridge_limits,
    ErdCode.CURRENT_TEMPERATURE: _decode_fridge_setpoint,
    ErdCode.TEMPERATURE_SETTING: _decode_fridge_setpoint,
    # Oven
    ErdCode.OVEN_CONFIGURATION: _decode_oven_configuration,
    ErdCode.OVEN_MODE_MIN_MAX_TEMP: _decode_oven_ranges,
    ErdCode.LOWER_OVEN_CURRENT_STATE: _decode_oven_state,
    ErdCode.LOWER_OVEN_AVAILABLE_COOK_MODES: _decode_cook_modes,
    ErdCode.LOWER_OVEN_COOK_MODE: _decode_oven_cook_mode,
    ErdCode.UPPER_OVEN_CURRENT_STATE: _decode_oven_state,
    ErdCode.UPPER_OVEN_AVAILABLE_COOK_MODES: _decode_cook_modes,
    ErdCode.UPPER_OVEN_COOK_MODE: _decode_oven_cook_mode,
    ErdCode.WATER_FILTER_STATUS: _decode_filter_status,
}
# Encoders for all fields
ERD_ENCODERS = {
    # Integers
    ErdCode.HOT_WATER_SET_TEMP: _encode_erd_int,

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
    ErdCode.TURBO_FREEZE_STATUS: _encode_erd_bool,
    ErdCode.TURBO_COOL_STATUS: _encode_erd_bool,

    # Special handling
    ErdCode.CLOCK_FORMAT: _encode_clock_format,
    ErdCode.END_TONE: _encode_end_tone,
    ErdCode.ICE_MAKER_CONTROL: _encode_ice_maker_control,
    ErdCode.LOWER_OVEN_COOK_MODE: _encode_oven_cook_mode,
    ErdCode.SOUND_LEVEL: _encode_sound_level,
    ErdCode.TEMPERATURE_SETTING: _encode_fridge_setpoint,
    ErdCode.TEMPERATURE_UNIT: _encode_measurement_unit,
    ErdCode.UPPER_OVEN_COOK_MODE: _encode_oven_cook_mode,
}
