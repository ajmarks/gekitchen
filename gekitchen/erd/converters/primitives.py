__all__ = (
    "ErdIntConverter",
    "ErdSignedByteConverter",
    "ErdBytesConverter",
    "ErdBoolConverter",
    "ErdStringConverter",   
    "ErdTimeSpanConverter",
    "erd_decode_int",
    "erd_encode_int",
    "erd_decode_signed_byte",
    "erd_encode_signed_byte",
    "erd_decode_bytes",
    "erd_encode_bytes",
    "erd_decode_bool",
    "erd_encode_bool",
    "erd_decode_string",
    "erd_encode_string",
    "erd_decode_timespan",
    "erd_encode_timespan" 
)

import logging
from datetime import timedelta
from typing import Optional

from .abstract import ErdValueConverter

_LOGGER = logging.getLogger(__name__)

class ErdIntConverter(ErdValueConverter[int]):
    def erd_decode(self, value) -> int:
        """Decode an integer value sent as a hex encoded string."""
        return int(value, 16)
    def erd_encode(self, value) -> str:
        """Encode an integer value as a hex string."""
        value = int(value)
        return value.to_bytes(2, 'big').hex()

class ErdSignedByteConverter(ErdValueConverter[int]):
    def erd_decode(self, value) -> int:
        """
        Convert a hex byte to a signed int.  Copied from GE's hextodec method.
        """
        val = int(value, 16)
        if val > 128:
            return val - 256
        return val
    def erd_encode(self, value) -> str:
        """
        Convert a hex byte to a signed int.  Copied from GE's hextodec method.
        """
        value = int(value)
        if value < 0:
            value = value + 256
        return value.to_bytes(1, "big").hex()

class ErdBytesConverter(ErdValueConverter[bytes]):
    def erd_decode(self, value) -> bytes:
        """Decode a raw bytes ERD value sent as a hex encoded string."""
        return bytes.fromhex(value)
    def erd_encode(self, value) -> str:
        """Encode a raw bytes ERD value."""
        return value.hex('big')

class ErdBoolConverter(ErdValueConverter[Optional[bool]]):
    def erd_decode(self, value) -> Optional[bool]:
        if value == "FF":
            return None
        return bool(int(value))
    def erd_encode(self, value) -> str:
        if value is None:
            return "FF"
        return "01" if value else "00"    

class ErdStringConverter(ErdValueConverter[str]):
    def erd_decode(self, value) -> str:
        """
        Decode an string value sent as a hex encoded string.
        """
        raw_bytes = bytes.fromhex(value)
        raw_bytes = raw_bytes.rstrip(b'\x00')

        return raw_bytes.decode('ascii')
    def erd_encode(self, value) -> str:
        """
        Encode an string value to a hex encoded string.
        """
        raw_bytes = value.encode('ascii')
        return bytes.hex(raw_bytes)

class ErdTimeSpanConverter(ErdValueConverter[Optional[timedelta]]):
    def erd_decode(self, value: str) -> Optional[timedelta]:
        minutes = int(value, 16)
        if minutes == 65535:
            _LOGGER.debug('Got timespan value of 65535. Treating as None.')
            return None
        return timedelta(minutes=minutes)
    def erd_encode(self, value: Optional[timedelta]) -> str:
        if value is None:
            minutes = 65535
        else:
            minutes = value.seconds // 60
        return minutes.to_bytes(2, 'big').hex()

_int_converter = ErdIntConverter()
_signed_byte_converter = ErdSignedByteConverter()
_bytes_converter = ErdBytesConverter()
_bool_converter = ErdBoolConverter()
_string_converter = ErdStringConverter()
_timespan_converter = ErdTimeSpanConverter()

def erd_decode_int(value: str) -> int:
    return _int_converter.erd_decode(value)
def erd_encode_int(value: int) -> str:
    return _int_converter.erd_encode(value)
def erd_decode_signed_byte(value: str) -> int:
    return _signed_byte_converter.erd_decode(value)
def erd_encode_signed_byte(value: int) -> str:
    return _signed_byte_converter.erd_encode(value)
def erd_decode_bytes(value: str) -> bytes:
    return _bytes_converter.erd_decode(value)
def erd_encode_bytes(value: bytes) -> str:
    return _bytes_converter.erd_encode(value)
def erd_decode_bool(value: str) -> Optional[bool]:
    return _bytes_converter.erd_decode(value)
def erd_encode_bool(value: Optional[bool]) -> str:
    return _bytes_converter.erd_encode(value)
def erd_decode_string(value: str) -> str:
    return _string_converter.erd_decode(value)
def erd_encode_string(value: str) -> str:
    return _string_converter.erd_encode(value)
def erd_decode_timespan(value: str) -> Optional[timedelta]:
    return _timespan_converter.erd_decode(value)
def erd_encode_timespan(value: Optional[timedelta]) -> str:
    return _timespan_converter.erd_encode(value)
