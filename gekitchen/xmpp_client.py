import asyncio
import logging
import slixmpp
import socket
import ssl
from lxml import etree
from .ge_appliance import GeAppliance
from typing import Any, Dict, Optional, Tuple

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


class GeClient(slixmpp.ClientXMPP):
    def __init__(self, xmpp_credentials: Dict, event_loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs):
        # If we have our own even loop, use that
        self._loop = event_loop
        self._xmpp_credentials = xmpp_credentials

        super().__init__(xmpp_credentials['jid'], xmpp_credentials['password'], **kwargs)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping

        self.add_event_handler('message', self.on_message)
        self.add_event_handler('session_start', self.on_start)
        self.add_event_handler('presence_available', self.on_presence_available)
        self.add_event_handler('presence_unavailable', self.on_presence_unavailable)
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self._appliances = {}  # type: Dict[str, GeAppliance]

    def connect(self, address: Optional[Tuple[str, int]] = None, use_ssl: bool = False,
                force_starttls: bool = True, disable_starttls: bool = False):
        """Connect to the XMPP server."""
        if address is None:
            address = (self._xmpp_credentials['address'], self._xmpp_credentials['port'])
        super().connect(
            address=address,
            use_ssl=use_ssl,
            force_starttls=force_starttls,
            disable_starttls=disable_starttls
        )

    @property
    def appliances(self) -> Dict[str, GeAppliance]:
        return self._appliances

    async def on_presence_available(self, evt):
        """Perform actions when notified of an available JID."""
        jid = slixmpp.JID(evt['from']).bare
        if jid == self.boundjid.bare:
            return
        try:
            self.appliances[jid].set_available()
            _LOGGER.debug(f'Appliance {jid} marked available')
        except KeyError:
            await self.add_appliance(jid)

    async def add_appliance(self, jid: str):
        """Add an appliance to the registry and request an update."""
        if jid in self.appliances:
            raise RuntimeError('Trying to add duplicate appliance')
        new_appliance = GeAppliance(jid, self)
        new_appliance.request_update()
        self.appliances[jid] = new_appliance
        self.event('add_appliance', new_appliance)
        _LOGGER.info(f'Adding appliance {jid}')

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
                self.event('appliance_state_change', [appliance, state_changes])
        except KeyError:
            _LOGGER.warning('Received json message from unregistered appliance')

    async def on_start(self, event):
        _LOGGER.debug('Starting session: ' + str(event))
        self.send_presence('available')

    def complete_jid(self, jid) -> str:
        """Make a complete jid from a username"""
        if '@' in jid:
            return jid
        return f'{jid}@{self.boundjid.host}'

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
            self.event('connection_failed',
                       'No DNS record available for %s' % self.default_domain)
        except OSError as e:
            _LOGGER.debug('Connection failed: %s', e)
            self.event("connection_failed", e)
            if self._current_connection_attempt is None:
                return
            self.connect_loop_wait = self.connect_loop_wait * 2 + 1
            self._current_connection_attempt = asyncio.ensure_future(
                self._connect_routine(), loop=self.loop,
            )
