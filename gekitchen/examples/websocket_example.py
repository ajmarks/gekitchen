"""
Websocket client example

We're going to run the client in a pre-existing event loop.  We're also going to register some event callbacks
to update appliances every five minutes and to turn on our oven the first time we see it.  Because that is safe!
"""

import aiohttp
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Tuple
from gekitchen.secrets import USERNAME, PASSWORD
from gekitchen import (
    EVENT_ADD_APPLIANCE,
    EVENT_APPLIANCE_STATE_CHANGE,
    EVENT_APPLIANCE_INITIAL_UPDATE,
    ErdApplianceType,
    ErdCode,
    ErdCodeType,
    ErdOvenCookMode,
    GeAppliance,
    GeWebsocketClient,
    OvenCookSetting,
)

_LOGGER = logging.getLogger(__name__)


async def log_state_change(data: Tuple[GeAppliance, Dict[ErdCodeType, Any]]):
    """Log changes in appliance state"""
    appliance, state_changes = data
    updated_keys = ', '.join([str(s) for s in state_changes])
    _LOGGER.debug(f'Appliance state change detected in {appliance}. Updated keys: {updated_keys}')


async def detect_appliance_type(appliance: GeAppliance):
    """
    Detect the appliance type.
    This should only be triggered once since the appliance type should never change.

    Also, let's turn on ovens!
    """
    _LOGGER.debug(f'Appliance state change detected in {appliance}')
    if appliance.appliance_type == ErdApplianceType.OVEN:
        _LOGGER.info('Turning on the oven!')
        await appliance.async_set_erd_value(
            ErdCode.UPPER_OVEN_COOK_MODE,
            OvenCookSetting(ErdOvenCookMode.BAKE_NOOPTION, 350)
        )
        _LOGGER.info('Set the timer!')
        await appliance.async_set_erd_value(ErdCode.UPPER_OVEN_KITCHEN_TIMER, timedelta(minutes=45))
        pass


async def do_periodic_update(appliance: GeAppliance):
    """Request a full state update every minute forever"""
    _LOGGER.debug(f'Registering update callback for {appliance:s}')
    while True:
        await asyncio.sleep(60 * 1)
        _LOGGER.debug(f'Requesting update for {appliance:s}')
        await appliance.async_request_update()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    loop = asyncio.get_event_loop()
    client = GeWebsocketClient(loop, USERNAME, PASSWORD)
    client.add_event_handler(EVENT_APPLIANCE_INITIAL_UPDATE, detect_appliance_type)
    client.add_event_handler(EVENT_APPLIANCE_STATE_CHANGE, log_state_change)
    client.add_event_handler(EVENT_ADD_APPLIANCE, do_periodic_update)

    session = aiohttp.ClientSession()
    asyncio.ensure_future(client.async_get_credentials_and_run(session), loop=loop)
    loop.run_until_complete(asyncio.sleep(60))
