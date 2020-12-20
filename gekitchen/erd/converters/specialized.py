__all__ = (
    "ErdApplianceTypeConverter",
    "ErdMeasurementUnitsConverter",
    "ErdEndToneConverter",
    "ErdSoundLevelConverter",
    "ErdClockFormatConverter",
    "ErdModelSerialConverter",
    "ErdSoftwareVersionConverter"
)

from textwrap import wrap

from .abstract import ErdValueConverter, ErdReadOnlyConverter
from .base_types import *

from gekitchen.erd.values import ErdApplianceType, ErdMeasurementUnits, ErdEndTone, ErdSoundLevel, ErdClockFormat

class ErdApplianceTypeConverter(ErdReadOnlyConverter[ErdApplianceType]):
    @staticmethod
    def erd_decode(value) -> ErdApplianceType:
        try:
            return ErdApplianceType(value)
        except ValueError:
            return ErdApplianceType.UNKNOWN

class ErdMeasurementUnitsConverter(ErdValueConverter[ErdMeasurementUnits]):
    @staticmethod
    def erd_decode(value: str) -> ErdMeasurementUnits:
        return ErdMeasurementUnits(int(value))
    @staticmethod
    def erd_encode(value: ErdMeasurementUnits) -> str:
        return f'{value.value:02d}'

class ErdEndToneConverter(ErdValueConverter[ErdEndTone]):
    @staticmethod
    def erd_decode(value: str) -> ErdEndTone:
        try:
            return ErdEndTone(value)
        except ValueError:
            return ErdEndTone.NA
    @staticmethod
    def erd_encode(value: ErdEndTone) -> str:
        if value == ErdEndTone.NA:
            raise ValueError("Invalid EndTone value")
        return value.value

class ErdSoundLevelConverter(ErdValueConverter[ErdSoundLevel]):    
    @staticmethod
    def erd_decode(value: str) -> ErdSoundLevel:
        sound_level = ErdIntConverter.erd_decode(value)
        return ErdSoundLevel(sound_level)
    @staticmethod
    def erd_encode(value: ErdSoundLevel) -> str:
        return ErdIntConverter.erd_encode(value.value)

class ErdClockFormatConverter(ErdValueConverter[ErdClockFormat]):
    @staticmethod
    def erd_decode(value: str) -> ErdClockFormat:
        return ErdClockFormat(value)
    @staticmethod
    def erd_encode(value: ErdClockFormat) -> str:
        return value.value    

class ErdModelSerialConverter(ErdReadOnlyConverter[str]):
    @staticmethod
    def erd_decode(value) -> str:
        """
        Decode a serial/model number string value sent as a hex encoded string.

        TODO: I think the first byte is a checksum.  I need to confirm this so we can have an encoder as well.
        """
        raw_bytes = bytes.fromhex(value)
        raw_bytes = raw_bytes.rstrip(b'\x00')

        return raw_bytes[1:].decode('ascii')

class ErdSoftwareVersionConverter(ErdReadOnlyConverter[str]):
    @staticmethod
    def erd_decode(value) -> str:
        """
        Decode a software version string.
        These are sent as four bytes, encoding each part of a four-element version string.
        """
        vals = wrap(value, 2)
        return '.'.join(str(ErdIntConverter.erd_decode(val)) for val in vals)

