__all__ = (
    "ErdIntConverter",
    "ErdSignedByteConverter",
    "ErdBytesConverter",
    "ErdBoolConverter",
    "ErdStringConverter",   
    "ErdTimeSpanConverter" 
)

import logging
from datetime import timedelta
from typing import Optional

from .abstract import ErdValueConverter

_LOGGER = logging.getLogger(__name__)

class ErdIntConverter(ErdValueConverter[int]):
    @staticmethod
    def erd_decode(value) -> int:
        """Decode an integer value sent as a hex encoded string."""
        return int(value, 16)
    @staticmethod
    def erd_encode(value) -> str:
        """Encode an integer value as a hex string."""
        value = int(value)
        return value.to_bytes(2, 'big').hex()

class ErdSignedByteConverter(ErdValueConverter[int]):
    @staticmethod
    def erd_decode(value) -> int:
        """
        Convert a hex byte to a signed int.  Copied from GE's hextodec method.
        """
        val = int(value, 16)
        if val > 128:
            return val - 256
        return val
    @staticmethod
    def erd_encode(value) -> str:
        """
        Convert a hex byte to a signed int.  Copied from GE's hextodec method.
        """
        value = int(value)
        if value < 0:
            value = value + 256
        return value.to_bytes(1, "big").hex()

class ErdBytesConverter(ErdValueConverter[bytes]):
    @staticmethod
    def erd_decode(value) -> bytes:
        """Decode a raw bytes ERD value sent as a hex encoded string."""
        return bytes.fromhex(value)
    @staticmethod
    def erd_encode(value) -> str:
        """Encode a raw bytes ERD value."""
        return value.hex('big')

class ErdBoolConverter(ErdValueConverter[Optional[bool]]):
    @staticmethod
    def erd_decode(value) -> Optional[bool]:
        if value == "FF":
            return None
        return bool(int(value))
    @staticmethod
    def erd_encode(value) -> str:
        if value is None:
            return "FF"
        return "01" if value else "00"    

class ErdStringConverter(ErdValueConverter[str]):
    @staticmethod
    def erd_decode(value) -> str:
        """
        Decode an string value sent as a hex encoded string.

        TODO: At least for the dishwasher cycle the first character is not a check sum
        are there potentially different decoding methods needed?
        """
        raw_bytes = bytes.fromhex(value)
        raw_bytes = raw_bytes.rstrip(b'\x00')

        return raw_bytes.decode('ascii')
    @staticmethod
    def erd_encode(value) -> str:
        """
        Encode an string value to a hex encoded string.

        TODO: At least for the dishwasher cycle the first character is not a check sum
        are there potentially different decoding methods needed?
        """
        raw_bytes = value.encode('ascii')
        return bytes.hex(raw_bytes)

class ErdTimeSpanConverter(ErdValueConverter[Optional[timedelta]]):
    @staticmethod
    def erd_decode(value: str) -> Optional[timedelta]:
        minutes = ErdIntConverter.erd_decode(value)
        if minutes == 65535:
            _LOGGER.debug('Got timespan value of 65535. Treating as None.')
            return None
        return timedelta(minutes=minutes)
    @staticmethod
    def erd_encode(value: Optional[timedelta]) -> str:
        if value is None:
            minutes = 65535
        else:
            minutes = value.seconds // 60
        return ErdIntConverter.erd_encode(minutes)


