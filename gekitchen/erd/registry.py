from typing import TypedDict

from .codes import ErdCode
from .converters import *

class ConverterRegistry(TypedDict):
    key: ErdCode
    value: ErdValueConverter

_registry = ConverterRegistry({
    #Universal
    ErdCode.APPLIANCE_TYPE: ErdApplianceTypeConverter(),
    ErdCode.MODEL_NUMBER: ErdModelSerialConverter(),
    ErdCode.SERIAL_NUMBER: ErdModelSerialConverter(),
    ErdCode.SABBATH_MODE: ErdBoolConverter(),
    ErdCode.ACM_UPDATING: ErdBoolConverter(),
    ErdCode.APPLIANCE_UPDATING: ErdBoolConverter(),
    ErdCode.LCD_UPDATING: ErdBoolConverter(),
    ErdCode.CLOCK_FORMAT: ErdClockFormatConverter(),
    ErdCode.END_TONE: ErdEndToneConverter(),
    ErdCode.SOUND_LEVEL: ErdSoundLevelConverter(),
    ErdCode.TEMPERATURE_UNIT: ErdMeasurementUnitsConverter(),
    ErdCode.APPLIANCE_SW_VERSION: ErdSoftwareVersionConverter(),
    ErdCode.APPLIANCE_SW_VERSION_AVAILABLE: ErdSoftwareVersionConverter(),
    ErdCode.LCD_SW_VERSION: ErdSoftwareVersionConverter(),
    ErdCode.LCD_SW_VERSION_AVAILABLE: ErdSoftwareVersionConverter(),
    ErdCode.WIFI_MODULE_SW_VERSION: ErdSoftwareVersionConverter(),
    ErdCode.WIFI_MODULE_SW_VERSION_AVAILABLE: ErdSoftwareVersionConverter(),

    #Fridge
    ErdCode.HOT_WATER_SET_TEMP: ErdIntConverter(),
    ErdCode.HOT_WATER_IN_USE: ErdBoolConverter(),
    ErdCode.TURBO_FREEZE_STATUS: ErdBoolConverter(),
    ErdCode.TURBO_COOL_STATUS: ErdBoolConverter(),
    ErdCode.DOOR_STATUS: FridgeDoorStatusConverter(),
    ErdCode.HOT_WATER_STATUS: HotWaterStatusConverter(),
    ErdCode.ICE_MAKER_BUCKET_STATUS: FridgeIceBucketStatusConverter(),
    ErdCode.ICE_MAKER_CONTROL: IceMakerControlStatusConverter(),
    ErdCode.WATER_FILTER_STATUS: ErdFilterStatusConverter(),
    ErdCode.SETPOINT_LIMITS: FridgeSetPointLimitsConverter(),
    ErdCode.CURRENT_TEMPERATURE: FridgeSetPointsConverter(),
    ErdCode.TEMPERATURE_SETTING: FridgeSetPointsConverter(),

    #Oven
    ErdCode.LOWER_OVEN_PROBE_PRESENT: ErdBoolConverter(),
    ErdCode.LOWER_OVEN_REMOTE_ENABLED: ErdBoolConverter(),
    ErdCode.LOWER_OVEN_DISPLAY_TEMPERATURE: ErdIntConverter(),
    ErdCode.LOWER_OVEN_PROBE_DISPLAY_TEMP: ErdIntConverter(),
    ErdCode.LOWER_OVEN_RAW_TEMPERATURE: ErdIntConverter(),
    ErdCode.LOWER_OVEN_USER_TEMP_OFFSET: ErdIntConverter(),
    ErdCode.LOWER_OVEN_COOK_TIME_REMAINING: ErdTimeSpanConverter(),
    ErdCode.LOWER_OVEN_DELAY_TIME_REMAINING: ErdTimeSpanConverter(),
    ErdCode.LOWER_OVEN_ELAPSED_COOK_TIME: ErdTimeSpanConverter(),
    ErdCode.LOWER_OVEN_KITCHEN_TIMER: ErdTimeSpanConverter(),
    ErdCode.LOWER_OVEN_CURRENT_STATE: ErdOvenStateConverter(),
    ErdCode.LOWER_OVEN_AVAILABLE_COOK_MODES: ErdAvailableCookModeConverter(),
    ErdCode.LOWER_OVEN_COOK_MODE: OvenCookModeConverter(),

    ErdCode.UPPER_OVEN_PROBE_PRESENT: ErdBoolConverter(),
    ErdCode.UPPER_OVEN_REMOTE_ENABLED: ErdBoolConverter(),
    ErdCode.UPPER_OVEN_DISPLAY_TEMPERATURE: ErdIntConverter(),
    ErdCode.UPPER_OVEN_PROBE_DISPLAY_TEMP: ErdIntConverter(),
    ErdCode.UPPER_OVEN_RAW_TEMPERATURE: ErdIntConverter(),
    ErdCode.UPPER_OVEN_USER_TEMP_OFFSET: ErdIntConverter(),
    ErdCode.UPPER_OVEN_COOK_TIME_REMAINING: ErdTimeSpanConverter(),
    ErdCode.UPPER_OVEN_DELAY_TIME_REMAINING: ErdTimeSpanConverter(),
    ErdCode.UPPER_OVEN_ELAPSED_COOK_TIME: ErdTimeSpanConverter(),
    ErdCode.UPPER_OVEN_KITCHEN_TIMER: ErdTimeSpanConverter(),
    ErdCode.UPPER_OVEN_CURRENT_STATE: ErdOvenStateConverter(),
    ErdCode.UPPER_OVEN_AVAILABLE_COOK_MODES: ErdAvailableCookModeConverter(),
    ErdCode.UPPER_OVEN_COOK_MODE: OvenCookModeConverter(),

    ErdCode.CONVECTION_CONVERSION: ErdBoolConverter(),
    ErdCode.HOUR_12_SHUTOFF_ENABLED: ErdBoolConverter(),
    ErdCode.OVEN_CONFIGURATION: OvenConfigurationConverter(),
    ErdCode.OVEN_MODE_MIN_MAX_TEMP: OvenRangesConverter(),

    # Dishwasher
    ErdCode.CYCLE_NAME: ErdStringConverter(),
    ErdCode.PODS_REMAINING_VALUE: ErdIntConverter(),
    ErdCode.TIME_REMAINING: ErdTimeSpanConverter(),
    ErdCode.CYCLE_STATE: ErdCycleStateConverter(),
    ErdCode.OPERATING_MODE: ErdOperatingStateConverter(),
    ErdCode.RINSE_AGENT: ErdRinseAgentConverter(),
})