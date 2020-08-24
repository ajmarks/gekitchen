import asyncio
import logging
import websockets
from async_timeout import timeout
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from aiohttp import ClientSession

from .base_client import GeBaseClient

from ..async_login_flow import async_do_full_wss_flow
from ..exc import GeNotAuthedError
from ..const import API_URL, EVENT_ADD_APPLIANCE, EVENT_APPLIANCE_STATE_CHANGE
from ..erd_constants import ErdCode
from ..erd_utils import ErdCodeType
from ..ge_appliance import GeAppliance
from ..login_flow import do_full_wss_flow

try:
    import ujson as json
except ImportError:
    import json

ALL_ERD = "allErd"
API_HOST = API_URL[8:]  # Drop the https://
CALLBACK_TIMEOUT = 0.05
LIST_APPLIANCES = "List-appliances"
SET_ERD = "setErd"
_LOGGER = logging.getLogger(__name__)


class GeWebsocketClient(GeBaseClient):
    """
    Client for GE's Websocket pseudo-MQTT API.

    TODO:
      Handle re-auth
      Better error handling in general
      Probably a ton of other stuff?
    """
    client_priority = 2  # This should be the primary client

    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = None,
                 username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(event_loop)
        self._endpoint = None  # type: Optional[str]
        self._socket = None  # type: Optional[websockets.client.WebSocketClientProtocol]
        self._pending_erds = {}  # type: Dict[Tuple[str, str], str]
        self._event_handlers = defaultdict(list)  # type: Dict[str, List[Callable]]
        self.username = username
        self.password = password

        self.add_event_handler(EVENT_APPLIANCE_STATE_CHANGE, self.maybe_trigger_appliance_init_event)

    def _apply_default_login(self, username: Optional[str] = None, password: Optional[str] = None) -> Tuple[str, str]:
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        if username is None or password is None:
            raise RuntimeError('username and password must be specified')
        return username, password

    async def async_get_credentials(self, session: ClientSession, username: Optional[str] = None,
                                    password: Optional[str] = None):
        username, password = self._apply_default_login(username, password)
        wss_credentials = await async_do_full_wss_flow(session, username, password)
        self.credentials = wss_credentials

    def get_credentials(self, username: Optional[str] = None, password: Optional[str] = None):
        username, password = self._apply_default_login(username, password)
        wss_credentials = do_full_wss_flow(username, password)
        self.credentials = wss_credentials

    @property
    def endpoint(self) -> str:
        try:
            return self.credentials['endpoint']
        except (TypeError, KeyError):
            raise GeNotAuthedError

    @property
    def event_handlers(self) -> Dict[str, List[Callable]]:
        return self._event_handlers

    def add_event_handler(self, event: str, callback: Callable, disposable: bool = False):
        if disposable:
            raise NotImplementedError('Support for disposable callbacks not yet implemented')
        self.event_handlers[event].append(callback)

    async def async_event(self, event: str, *args, **kwargs):
        """Trigger event callbacks sequentially"""
        for cb in self.event_handlers[event]:
            asyncio.ensure_future(cb(*args, **kwargs), loop=self.loop)

    @property
    def websocket(self):
        return self._socket

    def _process_pending_erd(self, message_id: str):
        id_parts = message_id.split("-")
        if id_parts[1] != SET_ERD:
            raise ValueError("Invalid message id")
        mac_addr = id_parts[0]
        raw_erd_code = id_parts[2]
        erd_value = self._pending_erds.get((mac_addr, raw_erd_code))
        if erd_value is not None:
            try:
                self.appliances[mac_addr].update_erd_value(raw_erd_code, erd_value)
            except KeyError:
                pass

    async def process_message(self, message: str):
        """
        Process an incoming message.
        """
        message_dict = json.loads(message)  # type: Dict
        try:
            kind = message_dict['kind']
        except KeyError:
            return

        if kind == "publish#erd":
            await self.process_erd_update(message_dict)
        elif kind == "websocket#api":
            try:
                message_id = message_dict["id"]
            except KeyError:
                return
            if message_id == LIST_APPLIANCES:
                await self.process_appliance_list(message_dict)
            elif f"-{SET_ERD}-" in message_id and message_dict.get("code") == 200:
                self._process_pending_erd(message_id)
            elif f"-{ALL_ERD}" in message_id and message_dict.get("code") == 200:
                await self.process_cache_update(message_dict)

    async def process_appliance_list(self, message_dict: Dict):
        """
        Process the appliance list.

        These messages should take the form::

            {"kind": "websocket#api",
             "id": "List-appliances",
             "request":{...},
             "success": True,
             "code": 200,
             "body": {
                "kind": "appliance#applianceList",
                "userId": "USER_ID",
                "items":[
                    {"applianceId": "MAC_ADDR_1",
                     "type": "TYPE_1",
                     "brand": "Unknown",
                     "jid":"<MAC_ADDR_1>_<USER_ID>",
                     "nickname":"NICKNAME",
                     "online":"ONLINE"
                    },
                    ...,
                ],
            }

        :param message_dict:
        """
        body = message_dict["body"]
        if body.get("kind") != "appliance#applianceList":
            raise ValueError("Not an applianceList")
        items = body["items"]
        for item in items:
            mac_addr = item["applianceId"].upper()
            if mac_addr in self.appliances:
                continue
            online = item['online'].upper() == "ONLINE"
            await self.add_appliance(mac_addr, online)

    async def process_cache_update(self, message_dict: Dict):
        """
        Process an appliance's full cache update.
        
        These messages should take the form::

            {
                "body": {
                    "applianceId": "MAC_ADDRESS",
                    "items": [
                        {"erd": "ERD_CODE_1", "time": "UPDATE_TIMESTAMP_1", "value": "VALUE_1"},
                        ...,
                        {"erd": "ERD_CODE_N", "time": "UPDATE_TIMESTAMP_N", "value": "VALUE_N"},
                    ],
                    "kind": "appliance#erdList",
                    "userId": "USER_ID"
                },
                "code": 200,
                "id": "<MAC_ADDRESS>-allErd",
                "kind": "websocket#api",
                "request": {...},
                "success": True,
            }
        """
        body = message_dict["body"]
        if body.get("kind") != "appliance#erdList":
            raise ValueError("Not an erdList")
        mac_addr = body["applianceId"].upper()
        updates = {i["erd"]: i["value"] for i in body["items"]}
        await self._update_appliance_state(mac_addr, updates)

    async def process_erd_update(self, message_dict: Dict):
        """
        Process an ERD update (pseudo-HTTP PUBLISH).

        These messages should be in the form::

            {
                "item": {
                    "applianceId": "MAC_ADDRESS",
                    "erd": "ERD_CODE",
                    "time": "UPDATE_TIMESTAMP",
                    "value": "SOME_VALUE",
                },
                "resource": "/appliance/<MAC_ADDRESS>/erd/<ERD_CODE>",
                "kind": "publish#erd",
                "userId":"USER_ID"
            }

        :param message_dict: dict, the json-decoded message.
        """
        item = message_dict["item"]
        mac_addr = item["applianceId"].upper()
        update = {item['erd']: item['value']}
        await self._update_appliance_state(mac_addr, update)

    async def _update_appliance_state(self, mac_addr: str, updates: Dict[ErdCodeType, str]):
        """Update appliance state, performing callbacks if necessary."""
        try:
            appliance = self.appliances[mac_addr]
        except KeyError:
            return
        state_changes = appliance.update_erd_values(updates)
        if state_changes:
            await self.async_event(EVENT_APPLIANCE_STATE_CHANGE, [appliance, state_changes])

    async def disconnect(self):
        await self.websocket.close()

    async def async_get_credentials_and_run(
            self, session: ClientSession, username: Optional[str] = None, password: Optional[str] = None,
            appliances: Optional[List[GeAppliance]] = None, keepalive: Optional[int] = 30):
        """Do a full login flow and run the client"""
        await self.async_get_credentials(session, username, password)
        await self.async_run_client(appliances, keepalive)

    async def async_run_client(self, appliances: Optional[List[GeAppliance]] = None, keepalive: Optional[int] = 30):
        """Run the client"""
        async with websockets.connect(self.endpoint) as socket:
            self._socket = socket
            if keepalive:
                asyncio.ensure_future(self.keep_alive(keepalive), loop=self.loop)
            if not appliances:
                await self.subscribe_all()
            else:
                await self.subscribe_appliances(appliances)
            await self.get_appliance_list()
            async for message in socket:
                await self.process_message(message)
        self._socket = None

    async def send_dict(self, msg_dict: Dict[str, Any]):
        payload = json.dumps(msg_dict)
        await self.websocket.send(payload)

    async def keep_alive(self, keepalive: int = 20):
        while not self.websocket.closed:
            await asyncio.sleep(keepalive)
            await self.send_ping()

    async def subscribe_all(self):
        msg_dict = {"kind": "websocket#subscribe", "action": "subscribe", "resources": ["/appliance/*/erd/*"]}
        await self.send_dict(msg_dict)

    async def subscribe_appliances(self, appliances: List[GeAppliance]):
        msg_dict = {
            "kind": "websocket#subscribe",
            "action": "subscribe",
            "resources": [f"/appliance/{appliance.mac_addr}/erd/*" for appliance in appliances]
        }
        await self.send_dict(msg_dict)

    async def subscribe_appliance(self, appliance: GeAppliance):
        await self.subscribe_appliances([appliance])

    async def async_set_erd_value(self, appliance: GeAppliance, erd_code: ErdCodeType, erd_value: Any):
        if isinstance(erd_code, ErdCode):
            raw_erd_code = erd_code.value
        else:
            raw_erd_code = erd_code

        mac_addr = appliance.mac_addr

        request_body = {
            "kind": "appliance#erdListEntry",
            "userId": self.user_id,
            "applianceId": appliance.mac_addr,
            "erd": raw_erd_code,
            "value": erd_value,
            "ackTimeout": 10,
            "delay": 0,
        }

        msg_dict = {
            "kind": "websocket#api",
            "action": "api",
            "host": API_URL,
            "method": "POST",
            "path": f"/v1/appliance/{mac_addr}/erd/{raw_erd_code}",
            "id": f"{mac_addr}-{SET_ERD}-{raw_erd_code}",
            "body": request_body,
        }
        self._pending_erds[(mac_addr, raw_erd_code)] = erd_value
        await self.send_dict(msg_dict)

    async def async_request_update(self, appliance: GeAppliance):
        _LOGGER.debug(f"Requesting update for client {appliance.mac_addr}")
        msg_dict = {
            "kind": "websocket#api",
            "action": "api",
            "host": API_HOST,
            "method": "GET",
            "path": f"/v1/appliance/{appliance.mac_addr}/erd",
            "id": f"{appliance.mac_addr}-{ALL_ERD}"
        }
        await self.send_dict(msg_dict)

    async def get_appliance_list(self):
        msg_dict = {
            "kind": "websocket#api",
            "action": "api",
            "host": API_HOST,
            "method": "GET",
            "path": "/v1/appliance",
            "id": LIST_APPLIANCES,
        }
        await self.send_dict(msg_dict)

    async def send_ping(self):
        _LOGGER.debug('Sending keepalive ping')
        msg_dict = {
            "kind": "websocket#ping",
            "id": "keepalive-ping",
            "action": "ping",
        }
        await self.send_dict(msg_dict)

    async def add_appliance(self, mac_addr: str, set_online: bool = True):
        """Add an appliance to the registry and request an update."""
        mac_addr = mac_addr.upper()
        if mac_addr in self.appliances:
            # TODO: Make this a package-specific exception
            raise RuntimeError('Trying to add duplicate appliance')
        new_appliance = GeAppliance(mac_addr, self)
        if set_online:
            new_appliance.set_available()

        _LOGGER.info(f'Adding appliance {mac_addr}')
        self.appliances[mac_addr] = new_appliance
        await self.async_event(EVENT_ADD_APPLIANCE, new_appliance)
        await self.async_request_update(new_appliance)
