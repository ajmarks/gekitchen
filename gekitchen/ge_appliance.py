"""Data model for GE kitchen appliances"""

import logging
from weakref import WeakValueDictionary
from typing import Any, Dict, Optional, Set, TYPE_CHECKING, Union
from slixmpp import JID
from .erd_utils import (
    ERD_DECODERS,
    ERD_ENCODERS,
    ErdCodeType,
    decode_erd_bytes,
    decode_erd_int,
    translate_erd_code,
)
from .erd_constants import ErdApplianceType, ErdCode

if TYPE_CHECKING:
    from .clients import GeBaseClient

try:
    import ujson as json
except ImportError:
    import json

_LOGGER = logging.getLogger(__name__)


class GeAppliance:
    """Base class shared by all appliances"""

    # Registered encoders and decoders for ERD fields
    _erd_decoders = ERD_DECODERS
    _erd_encoders = ERD_ENCODERS

    # Registry of initialized appliances
    _appliance_cache = WeakValueDictionary()

    def __new__(cls, mac_addr: Union[str, JID], client: "GeBaseClient", *args, **kwargs):
        if isinstance(mac_addr, JID):
            mac_addr = str(mac_addr.user).split('_')[0]
        try:
            obj = cls._appliance_cache[mac_addr]  # type: "GeAppliance"
        except KeyError:
            obj = super(GeAppliance, cls).__new__(cls)
            obj.__init__(mac_addr, client)
            cls._appliance_cache[obj.mac_addr] = obj
            return obj
        else:
            if client.client_priority >= obj.client.client_priority:
                obj.client = client
        return obj

    def __init__(self, mac_addr: Union[str, JID], client: "GeBaseClient"):
        if isinstance(mac_addr, JID):
            mac_addr = str(mac_addr.user).split('_')[0]
        self._available = False
        self._mac_addr = mac_addr.upper()
        self._message_id = 0
        self._property_cache = {}  # type: Dict[ErdCodeType, Any]
        self.client = client
        self.initialized = False

    @property
    def mac_addr(self) -> str:
        return self._mac_addr.upper()

    @property
    def known_properties(self) -> Set[ErdCodeType]:
        return set(self._property_cache)

    async def async_request_update(self):
        """Request the appliance send a full state update"""
        await self.client.async_request_update(self)

    def set_available(self):
        _LOGGER.debug(f'{self.mac_addr} marked available')
        self._available = True

    def set_unavailable(self):
        _LOGGER.debug(f'{self.mac_addr} marked unavailable')
        self._available = False

    @property
    def available(self) -> bool:
        return self._available and self.initialized

    @property
    def appliance_type(self) -> Optional[ErdApplianceType]:
        return self._property_cache.get(ErdCode.APPLIANCE_TYPE)

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

        erd_code = translate_erd_code(erd_code)

        if isinstance(erd_code, str):
            return decode_erd_bytes(erd_value)

        try:
            return self._erd_decoders[erd_code](erd_value)
        except KeyError:
            return decode_erd_int(erd_value)

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

        erd_code = translate_erd_code(erd_code)

        try:
            return self._erd_encoders[erd_code](value)
        except KeyError:
            raise

    def get_erd_value(self, erd_code: ErdCodeType) -> Any:
        """
        Get the value of a property represented by an ERD Code
        :param erd_code: ErdCode or str, The ERD code for the property to get
        :return: The current cached value of that ERD code
        """
        erd_code = translate_erd_code(erd_code)
        return self._property_cache[erd_code]

    async def async_set_erd_value(self, erd_code: ErdCodeType, value: Any):
        """
        Send a new erd value to the appliance.
        :param erd_code: The ERD code to update
        :param value: The new value to set
        """
        erd_value = self.encode_erd_value(erd_code, value)
        await self.client.async_set_erd_value(self, erd_code, erd_value)

    def update_erd_value(
            self, erd_code: ErdCodeType, erd_value: str) -> bool:
        """
        Setter for ERD code values.

        :param erd_code: ERD code to update
        :param erd_value: The new value to set, as returned by the appliance (usually a hex string)
        :return: Boolean, True if the state changed, False if no value changed
        """
        erd_code = translate_erd_code(erd_code)
        value = self.decode_erd_value(erd_code, erd_value)

        old_value = self._property_cache.get(erd_code)

        try:
            state_changed = ((old_value is None) != (value is None)) or (old_value != value)
        except ValueError:
            _LOGGER.info('Unable to compare new and prior states.')
            state_changed = False

        if state_changed:
            _LOGGER.debug(f'Setting {erd_code} to {value}')
        self._property_cache[erd_code] = value

        return state_changed

    def update_erd_values(self, erd_values: Dict[ErdCodeType, str]) -> Dict[ErdCodeType, Any]:
        """
        Set one or more ERD codes value at once

        :param erd_values: Dictionary of erd codes and their new values as raw hex strings
        :return: dictionary of new states
        """
        state_changes = {
            translate_erd_code(k): self.decode_erd_value(k, v)
            for k, v in erd_values.items()
            if self.update_erd_value(k, v)
        }

        return state_changes

    def __str__(self):
        appliance_type = self.appliance_type
        if appliance_type is None:
            appliance_type = 'Unknown Type'
        return f'{self.__class__.__name__}({self.mac_addr}) ({appliance_type})'

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)
