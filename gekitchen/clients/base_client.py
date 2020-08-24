"""Base client for GE ERD APIs"""

import abc
import asyncio
import logging
from aiohttp import ClientSession
from typing import Any, Callable, Dict, Optional, Tuple
from ..const import EVENT_APPLIANCE_INITIAL_UPDATE
from ..erd_constants import ErdCode
from ..erd_utils import ErdCodeType
from ..exc import GeNotAuthedError
from ..ge_appliance import GeAppliance

try:
    import ujson as json
except ImportError:
    import json

_LOGGER = logging.getLogger(__name__)


class GeBaseClient(metaclass=abc.ABCMeta):
    """Abstract base class for GE ERD APIs"""

    client_priority = 0  # Priority of this client class.  Higher is better.

    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = None):
        self._loop = event_loop
        self._appliances = {}  # type: Dict[str, GeAppliance]
        self._credentials = None  # type: Optional[Dict]

    @property
    def credentials(self) -> Optional[Dict]:
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: Dict):
        self._credentials = credentials

    @property
    def appliances(self) -> Dict[str, GeAppliance]:
        return self._appliances

    @property
    def user_id(self) -> Optional[str]:
        try:
            return self.credentials['userId']
        except (TypeError, KeyError):
            raise GeNotAuthedError

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return self._loop

    @abc.abstractmethod
    async def async_set_erd_value(self, appliance: GeAppliance, erd_code: ErdCodeType, erd_value: Any):
        """
        Send a new erd value to the appliance
        :param appliance: The appliance being updated
        :param erd_code: The ERD code to update
        :param erd_value: The new value to set
        """
        pass

    @abc.abstractmethod
    async def async_request_update(self, appliance: GeAppliance):
        """Request the appliance send a full state update"""
        pass

    @abc.abstractmethod
    async def async_get_credentials(self, session: ClientSession, username: str, password: str):
        """Get updated credentials"""
        pass

    @abc.abstractmethod
    async def async_event(self, event: str, data: Any = None):
        """Trigger an event."""
        pass

    @abc.abstractmethod
    def add_event_handler(self, event: str, callback: Callable, disposable: bool):
        pass

    async def maybe_trigger_appliance_init_event(self, data: Tuple[GeAppliance, Dict[ErdCodeType, Any]]):
        """
        Trigger the appliance_got_type event if appropriate

        :param data: GeAppliance updated and the updates
        """
        appliance, state_changes = data
        if ErdCode.APPLIANCE_TYPE in state_changes and not appliance.initialized:
            _LOGGER.debug(f'Got initial appliance type for {appliance:s}')
            appliance.initialized = True
            await self.async_event(EVENT_APPLIANCE_INITIAL_UPDATE, appliance)
