import asyncio
import logging

import slixmpp
import socket
import ssl
from aiohttp import ClientSession
from lxml import etree
from ..const import (
    EVENT_ADD_APPLIANCE,
    EVENT_APPLIANCE_STATE_CHANGE,
)
from ..async_login_flow import async_do_full_xmpp_flow
from ..erd_constants import ErdCode
from ..erd_utils import ErdCodeType
from ..ge_appliance import GeAppliance
from .base_client import GeBaseClient
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

try:
    import ujson as json
except ImportError:
    import json

_LOGGER = logging.getLogger(__name__)


def _first_or_none(lst: list) -> Any:
    try:
        return lst[0]
    except IndexError:
        return None


set_timer = False


def _format_request(
        msg_id: Union[int, str], uri: str, method: str, key: Optional[str] = None, value: Optional[str] = None) -> str:
    """Format a XMPP pseudo-HTTP request."""
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


class GeXmppClient(GeBaseClient, slixmpp.ClientXMPP):
    client_priority = 1

    def add_event_handler(self, event: str, callback: Callable, disposable: bool = False):
        super(GeBaseClient, self).add_event_handler(event, callback, disposable)

    def __init__(self, xmpp_credentials: Dict, event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 known_jids: Optional[List[str]] = None, **kwargs):
        GeBaseClient.__init__(self, event_loop)
        slixmpp.ClientXMPP.__init__(self, xmpp_credentials['jid'], xmpp_credentials['password'], **kwargs)
        self.credentials = xmpp_credentials
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping

        self.add_event_handler('message', self.on_message)
        self.add_event_handler('session_start', self.on_start)
        self.add_event_handler('presence_available', self.on_presence_available)
        self.add_event_handler('presence_unavailable', self.on_presence_unavailable)
        self.add_event_handler(EVENT_APPLIANCE_STATE_CHANGE, self.maybe_trigger_appliance_init_event)
        self.ssl_context.verify_mode = ssl.CERT_NONE

        if known_jids is None:
            known_jids = []
        self._known_jids = [self.complete_jid(j) for j in known_jids]

        self._initial_update_ids = set()  # type: Set[str]

    def connect(self, address: Optional[Tuple[str, int]] = None, use_ssl: bool = False,
                force_starttls: bool = True, disable_starttls: bool = False):
        """Connect to the XMPP server."""
        if address is None:
            address = (self._credentials['address'], self._credentials['port'])
        super().connect(
            address=address,
            use_ssl=use_ssl,
            force_starttls=force_starttls,
            disable_starttls=disable_starttls
        )

    async def add_appliance(self, jid: str):
        """Add an appliance to the registry and request an update."""
        mac_addr = jid.split('_')[0]
        if jid in self.appliances:
            # TODO: Make this a package-specific exception
            raise RuntimeError('Trying to add duplicate appliance')
        new_appliance = GeAppliance(mac_addr, self)

        _LOGGER.info(f'Adding appliance {jid}')
        self.appliances[jid] = new_appliance
        self.event(EVENT_ADD_APPLIANCE, new_appliance)
        await new_appliance.async_request_update()

    async def maybe_add_add_appliance(self, jid: str):
        """Add an appliance, suppressing the error if it already exists."""
        try:
            await self.add_appliance(jid)
        except RuntimeError:
            pass

    async def on_presence_available(self, evt: slixmpp.ElementBase):
        """Perform actions when notified of an available JID."""
        await asyncio.sleep(2)  # Wait 2 seconds to give it time to register
        jid = slixmpp.JID(evt['from']).bare

        if jid == self.boundjid.bare:
            return
        try:
            self.appliances[jid].set_available()
            _LOGGER.debug(f'Appliance {jid} marked available')
        except KeyError:
            await self.add_appliance(jid)
            self.appliances[jid].set_available()

    async def on_presence_unavailable(self, evt):
        """When appliance is no longer available, mark it as such."""
        jid = slixmpp.JID(evt['from']).bare

        if jid == self.boundjid.bare:
            return
        try:
            self.appliances[jid].set_unavailable()
            _LOGGER.debug(f'Appliance {jid} marked unavailable')
        except KeyError:
            pass

    async def on_message(self, event):
        """Handle incoming messages."""
        global set_timer
        msg = str(event)
        msg_from = slixmpp.JID(event['from']).bare
        try:
            message_data = self.extract_message_json(msg)
        except ValueError:
            _LOGGER.info(f"From: {msg_from}: Not a GE message")
            return
        try:
            appliance = self.appliances[msg_from]
            state_changes = appliance.update_erd_values(message_data)
            if state_changes:
                self.event(EVENT_APPLIANCE_STATE_CHANGE, [appliance, state_changes])
        except KeyError:
            _LOGGER.warning('Received json message from unregistered appliance')

    async def on_start(self, event):
        _LOGGER.debug('Starting session: ' + str(event))
        self.send_presence('available')
        await asyncio.sleep(5)
        for jid in self._known_jids:
            await self.maybe_add_add_appliance(jid)

    def complete_jid(self, jid) -> str:
        """Make a complete jid from a username"""
        if "@" in jid:
            return jid
        return f"{jid}@{self.boundjid.host}"

    def get_appliance_jid(self, appliance: GeAppliance) -> str:
        return self.complete_jid(f"{appliance.mac_addr}_{self.user_id}")

    @staticmethod
    def extract_message_json(message: str) -> Dict:
        """The appliances send messages that don't play nice with slixmpp, so let's do this."""
        etr = etree.XML(message)
        json_elem = _first_or_none(etr.xpath('//json'))
        if json_elem is None:
            raise ValueError('Not a GE appliance message')

        data = _first_or_none(json_elem.xpath('text()'))
        data = json.loads(data)
        return data

    async def process_in_running_loop(self, timeout: Optional[int] = None):
        """Process all the available XMPP events (receiving or sending data on the
        socket(s), calling various registered callbacks, calling expired
        timers, handling signal events, etc).  If timeout is None, this
        coroutine will run forever or until disconnected. If timeout is a number,
        this function will return after the given time in seconds."""

        if timeout is None:
            await asyncio.ensure_future(self.disconnected, loop=self.loop)
        else:
            await asyncio.wait([self.disconnected], loop=self.loop, timeout=timeout)

    async def _connect_routine(self):
        """
        Override the _connect_routine method from xmlstream.py.
        This is to address the bug corrected in open PR https://github.com/poezio/slixmpp/pull/19.
        """
        self.event_when_connected = "connected"

        if self.connect_loop_wait > 0:
            self.event('reconnect_delay', self.connect_loop_wait)
            await asyncio.sleep(self.connect_loop_wait, loop=self.loop)

        record = await self.pick_dns_answer(self.default_domain)
        if record is not None:
            host, address, dns_port = record
            port = self.address[1] if self.address[1] else dns_port
            self.address = (address, port)
            self._service_name = host
        else:
            # No DNS records left, stop iterating
            # and try (host, port) as a last resort
            self.dns_answers = None

        if self.use_ssl:
            ssl_context = self.get_ssl_context()
        else:
            ssl_context = None

        if self._current_connection_attempt is None:
            return
        try:
            await self.loop.create_connection(
                lambda: self, self.address[0], self.address[1], ssl=ssl_context,
                server_hostname=self.default_domain if self.use_ssl else None
            )
            self.connect_loop_wait = 0
        except socket.gaierror:
            self.event('connection_failed', 'No DNS record available for %s' % self.default_domain)
        except OSError as e:
            _LOGGER.debug('Connection failed: %s', e)
            self.event("connection_failed", e)
            if self._current_connection_attempt is None:
                return
            self.connect_loop_wait = self.connect_loop_wait * 2 + 1
            self._current_connection_attempt = asyncio.ensure_future(
                self._connect_routine(), loop=self.loop,
            )

    def send_raw_message(self, mto: slixmpp.JID, mbody: str, mtype: str = 'chat', msg_id: Optional[str] = None):
        """TODO: Use actual xml for this instead of hacking it.  Then again, this is what GE does in the app."""
        if msg_id is None:
            msg_id = self.new_id()
        raw_message = (
            f'<message type="{mtype}" from="{self.boundjid.bare}" to="{mto}" id="{msg_id}">'
            f'<body>{mbody}</body>'
            f'</message>'
        )
        self.send_raw(raw_message)

    def send_request(
            self, appliance: GeAppliance, method: str, uri: str, key: Optional[str] = None,
            value: Optional[str] = None, message_id: Optional[str] = None):
        """
        Send a pseudo-http request to the appliance
        :param appliance: GeAppliance, the appliance to send the request to
        :param method: str, Usually "GET" or "POST"
        :param uri: str, the "endpoint" for the request, usually of the form "/UUID/erd/{erd_code}"
        :param key: The json key to set in a POST request.  Usually a four-character hex string with leading "0x".
        :param value: The value to set, usually encoded as a hex string without a leading "0x"
        :param message_id:
        """
        if method.lower() != 'post' and (key is not None or value is not None):
            raise RuntimeError('Values can only be set in a POST request')

        if message_id is None:
            message_id = self.new_id()
        message_body = _format_request(message_id, uri, method, key, value)
        jid = slixmpp.JID(self.get_appliance_jid(appliance))
        self.send_raw_message(jid, message_body)

    async def async_request_update(self, appliance: GeAppliance):
        """Request a full update from the appliance."""
        self.send_request(appliance, 'GET', '/UUID/cache')

    async def async_set_erd_value(self, appliance: GeAppliance, erd_code: ErdCodeType, erd_value: Any):
        """
        Send a new erd value to the appliance
        :param appliance: GeAppliance, the appliance to update
        :param erd_code: The ERD code to update
        :param erd_value: The new value to set
        """
        if isinstance(erd_code, ErdCode):
            raw_erd_code = erd_code.value
        else:
            raw_erd_code = erd_code

        uri = f'/UUID/erd/{raw_erd_code}'
        self.send_request(appliance, 'POST', uri, raw_erd_code, erd_value)

    async def async_get_credentials(self, session: ClientSession, username: str, password: str) -> bool:
        xmpp_credentials = await async_do_full_xmpp_flow(session, username, password)
        self.credentials = xmpp_credentials
        self.set_jid(xmpp_credentials['jid'])
        self.password = xmpp_credentials['password']
        return True

    async def async_event(self, event: str, data: Any = None):
        """Make awaiting work here"""
        super(GeBaseClient, self).event(event, data)
