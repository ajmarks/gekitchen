"""Classes to implement GE appliances"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from slixmpp import JID, ClientXMPP
from .erd_utils import (
    ERD_DECODERS,
    ERD_ENCODERS,
    ErdCodeType,
    decode_erd_bytes,
    decode_erd_int,
    translate_erd_code,
)
from .erd_constants import ErdApplianceType, ErdCode

try:
    import ujson as json
except ImportError:
    import json

_LOGGER = logging.getLogger(__name__)


def _format_request(
        msg_id: Union[int, str], uri: str, method: str, key: Optional[str] = None, value: Optional[str] = None) -> str:
    if method.lower() == 'post':
        post_body = f"<json>{json.dumps({key:value})}</json>"
    else:
        post_body = ""
    message = (
        f"<request><id>{msg_id}</id>"
        f"<method>{method}</method>"
        f"<uri>{uri}</uri>"
        f"{post_body}"
        "</request>"  # [sic.]
    )
    return message


class GeAppliance:
    """Base class shared by all appliances"""

    # Registered encoders and decoders for ERD fields
    _erd_decoders = ERD_DECODERS
    _erd_encoders = ERD_ENCODERS

    def __init__(self, jid: Union[str, JID], xmpp_client: ClientXMPP):
        if not isinstance(jid, JID):
            jid = JID(jid)
        self._available = False
        self._jid = jid
        self._message_id = 0
        self._property_cache = {}  # type: Dict[ErdCodeType, Any]
        self._update_coroutines = []  # type: List[Callable[[Dict[ErdCodeType, Any]], Awaitable[Any]]]
        self._update_functions = []  # type: List[Callable[[Dict[ErdCodeType, Any]], Any]]
        self.xmpp_client = xmpp_client

    @property
    def jid(self) -> JID:
        return self._jid

    def register_update_callback(self, callback: Callable[[Dict[ErdCodeType, Any]], Any]):
        """
        Register a function to call after an update.
        A dictionary of the ERD codes and new values will be passed as an argument to the function
        :param callback: A function or coroutine function to call or await when a property is updated
        """
        if asyncio.iscoroutinefunction(callback):
            _LOGGER.debug(f'Registering async update callback: {callback.__name__}')
            self._update_coroutines.append(callback)
        else:
            _LOGGER.debug(f'Registering regular update callback: {callback.__name__}')
            self._update_functions.append(callback)

    def send_raw_message(self, mto: JID, mbody: str, mtype: str = 'chat', msg_id: Optional[str] = None):
        """TODO: Use actual xml for this instead of hacking it.  Then again, this is what GE does in the app."""
        if msg_id is None:
            msg_id = self.xmpp_client.new_id()
        raw_message = (
            f'<message type="{mtype}" from="{self.xmpp_client.boundjid.bare}" to="{mto}" id="{msg_id}">'
            f'<body>{mbody}</body>'
            f'</message>'
        )
        self.xmpp_client.send_raw(raw_message)

    async def async_send_request(
            self, method: str, uri: str, key: Optional[str] = None,
            value: Optional[str] = None, message_id: Optional[str] = None):
        """
        Send a pseudo-http request to the appliance
        :param method: str, Usually "GET" or "POST"
        :param uri: str, the "endpoint" for the request, usually of the form "/UUID/erd/{erd_code}"
        :param key: The json key to set in a POST request.  Usually a four-character hex string with leading "0x".
        :param value: The value to set, usually encoded as a hex string without a leading "0x"
        :param message_id:
        """
        if method.lower() != 'post' and (key is not None or value is not None):
            raise RuntimeError('Values can only be set in a POST request')

        if message_id is None:
            message_id = self._message_id
        else:
            self._message_id += 1
            message_id = self._message_id
        message_body = _format_request(message_id, uri, method, key, value)
        self.send_raw_message(self.jid, message_body)

    async def async_request_update(self):
        """Request the appliance send a full state update"""
        await self.async_send_request('GET', '/UUID/cache')

    async def async_set_available(self):
        self._available = True

    async def async_set_unavailable(self):
        self._available = False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def appliance_type(self) -> Optional[ErdApplianceType]:
        return self._property_cache.get(ErdCode.APPLIANCE_TYPE)

    def decode_erd_value(self, erd_code: ErdCodeType, erd_value: str) -> Any:
        """
        Decode and ERD Code raw value into something useful.  If the erd_code is a string that
        cannot be resolved to a known ERD Code, the value will be treated as raw byte string.
        Nonregistered ERD Codes will be translated as ints.

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

    async def _async_trigger_update_callbacks(self, state_changes: Dict[ErdCodeType, Any]):
        """
        Call all of the registered on update callbacks

        :param state_changes: Dictionary of updated ERD codes and values to pass to the callbacks
        """
        if state_changes:
            for f in self._update_functions:
                f(state_changes)
            for f in self._update_coroutines:
                await f(state_changes)

    async def async_update_erd_value(
            self, erd_code: ErdCodeType, erd_value: str, trigger_callbacks: bool = True) -> bool:
        """
        Setter for ERD code values.

        :param erd_code: ERD code to update
        :param erd_value: The new value to set, as returned by the appliance (usually a hex string)
        :param trigger_callbacks: bool, default True, If True, trigger update callbacks if the state changed
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

        if state_changed and trigger_callbacks:
            await self._async_trigger_update_callbacks({erd_code: value})
        return state_changed

    async def async_update_erd_values(
            self, erd_values: Dict[ErdCodeType, str], trigger_callbacks: bool = True) -> Dict[ErdCodeType, Any]:
        """
        Set one or more ERD codes value at once

        :param erd_values: Dictionary of erd codes and their new values as raw hex strings
        :param trigger_callbacks: bool, default True, If True, trigger update callbacks if the state changed
        :return: dictionary of new states
        """
        state_changes = {
            translate_erd_code(k): self.decode_erd_value(k, v)
            for k, v in erd_values.items()
            if await self.async_update_erd_value(k, v, trigger_callbacks=False)
        }

        if trigger_callbacks:
            await self._async_trigger_update_callbacks(state_changes)
        return state_changes

    async def async_set_erd_value(self, erd_code: ErdCodeType, value: Any):
        """
        Send a new erd value to the appliance
        :param erd_code: The ERD code to update
        :param value: The new value to set
        """
        erd_value = self.encode_erd_value(erd_code, value)
        if isinstance(erd_code, ErdCode):
            raw_erd_code = erd_code.value
        else:
            raw_erd_code = erd_code

        uri = f'/UUID/erd/{raw_erd_code}'
        await self.async_send_request('POST', uri, raw_erd_code, erd_value)

    def __str__(self):
        appliance_type = self.appliance_type
        if appliance_type is None:
            appliance_type = 'Unknown Type'
        return f'{self.__class__.__name__}({self.jid.node}) ({appliance_type})'
