import logging
from datetime import timedelta
from textwrap import wrap
from typing import Any, Dict, Optional, Set, Tuple, Union

from .codes import ErdCode
from .registry import _registry
from .converters import ErdValueConverter
from .converters.primitives import *

_LOGGER = logging.getLogger(__name__)

ErdCodeType = Union[ErdCode, str]

class ErdSerializer:
    def translate_erd_code(self, erd_code: ErdCodeType) -> ErdCodeType:
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

    def decode_erd_value(self, erd_code: ErdCodeType, erd_value: str) -> Any:
        """
        Decode and ERD Code raw value into something useful.  If the erd_code is a string that
        cannot be resolved to a known ERD Code, the value will be treated as raw byte string.
        Unregistered ERD Codes will be translated as ints.

        TODO: Register the numeric fields, and change the default behavior to bytestring

        :param erd_code: ErdCode or str, the ERD Code the value of which we want to decode
        :param erd_value: The raw ERD code value, usually a hex string without leading "0x"
        :return: The decoded value.
        """
        if erd_value == '':
            return None

        erd_code = self.translate_erd_code(erd_code)

        if isinstance(erd_code, str):
            return erd_decode_bytes(erd_value)

        try:
            return _registry[erd_code].erd_decode(erd_value)
        except KeyError:
            return erd_decode_int(erd_value)

    def encode_erd_value(self, erd_code: ErdCodeType, value: Any) -> str:
        """
        Encode an ERD Code value as a hex string.
        Only ERD Codes registered with self.erd_encoders will processed.  Otherwise an error will be returned.

        :param erd_code: ErdCode or str, the ERD Code the value of which we want to decode
        :param value: The value to re-encode
        :return: The encoded value as a hex string
        """
        if value is None:
            return ''

        erd_code = self.translate_erd_code(erd_code)

        try:
            return _registry[erd_code].erd_encode(value)
        except KeyError:
            raise
