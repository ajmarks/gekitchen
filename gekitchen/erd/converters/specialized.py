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
from .primitives import *

from gekitchen.erd.values import ErdApplianceType, ErdMeasurementUnits, ErdEndTone, ErdSoundLevel, ErdClockFormat

class ErdApplianceTypeConverter(ErdReadOnlyConverter[ErdApplianceType]):
    def erd_decode(self, value) -> ErdApplianceType:
        try:
            return ErdApplianceType(value)
        except ValueError:
            return ErdApplianceType.UNKNOWN

class ErdMeasurementUnitsConverter(ErdValueConverter[ErdMeasurementUnits]):
    def erd_decode(self, value: str) -> ErdMeasurementUnits:
        return ErdMeasurementUnits(int(value))
    def erd_encode(self, value: ErdMeasurementUnits) -> str:
        return f'{value.value:02d}'

class ErdEndToneConverter(ErdValueConverter[ErdEndTone]):
    def erd_decode(self, value: str) -> ErdEndTone:
        try:
            return ErdEndTone(value)
        except ValueError:
            return ErdEndTone.NA
    def erd_encode(self, value: ErdEndTone) -> str:
        if value == ErdEndTone.NA:
            raise ValueError("Invalid EndTone value")
        return value.value

class ErdSoundLevelConverter(ErdValueConverter[ErdSoundLevel]):    
    def erd_decode(self, value: str) -> ErdSoundLevel:
        sound_level = erd_decode_int(value)
        return ErdSoundLevel(sound_level)
    def erd_encode(self, value: ErdSoundLevel) -> str:
        return erd_encode_int(value.value)

class ErdClockFormatConverter(ErdValueConverter[ErdClockFormat]):
    def erd_decode(self, value: str) -> ErdClockFormat:
        return ErdClockFormat(value)
    def erd_encode(self, value: ErdClockFormat) -> str:
        return value.value    

class ErdModelSerialConverter(ErdReadOnlyConverter[str]):
    def erd_decode(self, value) -> str:
        """
        Decode a serial/model number string value sent as a hex encoded string.

        TODO: I think the first byte is a checksum.  I need to confirm this so we can have an encoder as well.
        """
        raw_bytes = bytes.fromhex(value)
        raw_bytes = raw_bytes.rstrip(b'\x00')

        return raw_bytes[1:].decode('ascii')

class ErdSoftwareVersionConverter(ErdReadOnlyConverter[str]):
    def erd_decode(self, value) -> str:
        """
        Decode a software version string.
        These are sent as four bytes, encoding each part of a four-element version string.
        """
        vals = wrap(value, 2)
        return '.'.join(str(erd_decode_int(val)) for val in vals)

