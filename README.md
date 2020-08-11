# gekitchen
Python SDK for GE WiFi-enabled kitchen appliances based on [`slixmpp`](https://slixmpp.readthedocs.io/).
The primary goal is to use this to power integrations for [Home Assistant](https://www.home-assistant.io/), though that
will probably need to wait on some new entity types.   

## Installation
```pip install gekitchen```

## Usage
### Simple Operation
```python
from gekitchen import do_full_login_flow, GeClient

USERNAME = 'me@email.com'
PASSWORD = '$7r0nkP@s$w0rD'

xmpp_credentials = do_full_login_flow(USERNAME, PASSWORD)
client = GeClient(xmpp_credentials)
client.connect()
client.process(timeout=120)
```

### Longer example
Here we're going to run the client in a pre-existing event loop.  We're also going to register some event callbacks
to update appliances every five minutes and to turn on our oven the first time we see it.  Because that is safe!
```python
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Tuple
from gekitchen import (
    ErdApplianceType,
    ErdCode,
    ErdCodeType,
    ErdOvenCookMode,
    GeAppliance,
    GeClient,
    OvenCookSetting,
    do_full_login_flow,
)

_LOGGER = logging.getLogger(__name__)
USERNAME = 'me@email.com'
PASSWORD = '$7r0nkP@s$w0rD'

async def detect_appliance_type(data: Tuple[GeAppliance, Dict[ErdCodeType, Any]]):
    """
    Detect the appliance type.
    This should only be triggered once since the appliance type should never change.

    Also, let's turn on ovens!
    """
    appliance, state_changes = data
    _LOGGER.debug(f'Appliance state change detected in {appliance:s}')
    try:
        _LOGGER.info(f'Setting appliance type to {state_changes[ErdCode.APPLIANCE_TYPE]:s}')
    except KeyError:
        # Not an APPLIANCE_TYPE update
        return
    if appliance.appliance_type == ErdApplianceType.OVEN:
        _LOGGER.info('Turning on the oven!')
        await appliance.async_set_erd_value(
            ErdCode.UPPER_OVEN_COOK_MODE,
            OvenCookSetting(ErdOvenCookMode.BAKE_NOOPTION, 350)
        )
        _LOGGER.info('Set the timer!')
        await appliance.async_set_erd_value(ErdCode.UPPER_OVEN_KITCHEN_TIMER, timedelta(minutes=45))


async def do_periodic_update(appliance: GeAppliance):
    """Request a full state update every five minutes forever"""
    _LOGGER.debug(f'Registering update callback for {appliance:s}')
    while True:
        await asyncio.sleep(5 * 60)
        _LOGGER.debug(f'Requesting update for {appliance:s}')
        if appliance.available:
            await appliance.async_request_update()

logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
xmpp_credentials = do_full_login_flow(USERNAME, PASSWORD)

evt_loop = asyncio.get_event_loop()
client = GeClient(xmpp_credentials, event_loop=evt_loop)
client.add_event_handler('appliance_state_change', detect_appliance_type)
client.add_event_handler('add_appliance', do_periodic_update)
client.connect()
asyncio.ensure_future(client.process_in_running_loop(), loop=evt_loop)
evt_loop.run_until_complete(asyncio.sleep(20 * 60))
```


## API Overview

The GE app communicates with devices via XMPP (Jabbber), sending pseudo-HTTP chat messages back and forth.  Device
properties are represented by hex codes (represented by `ErdCode` objects in `gekitchen`), and values are sent as 
hexadecimal strings without leading `"0x"`, then json encoded as a dictionary.  The device informs the client of a
state change by sending a `PUBLISH` message like this, informing us that the value of property 0x5205 
(`ErdCode.LOWER_OVEN_KITCHEN_TIMER` in `gekitchen`) is now "002d" (45 minutes):

```xml
<body>
    <publish>
        <method>PUBLISH</method>
        <uri>/UUID/erd/0x5205</uri>
        <json>{"0x5205":"002d"}</json>
    </publish>
</body>
```

Similarly, we can set the timer to 45 minutes by `POST`ing to the same "endpoint":
```xml
<body>
    <request>
        <method>POST</method>
        <uri>/UUID/erd/0x5205</uri>
        <json>{"0x5205":"002d"}</json>
    </request>
</body>
``` 
In `gekitchen`, that would handled by the `GeAppliance.async_set_erd_value` method:
```python
await appliance.async_set_erd_value(ErdCode.LOWER_OVEN_KITCHEN_TIMER, timedelta(minutes=45))
```

We can also get a specific property, or, more commonly, request a full cache refresh by `GET`ing the `/UUID/cache` 
endpoint:

```xml
<body>
    <request>
        <id>0</id>
        <method>GET</method>
        <uri>/UUID/cache</uri>
    </request>
</body>
```

The device will then respond to the `GET` with a `response` having a json payload:
```xml
<body>
    <response>
        <id>0</id>
        <method>GET</method>
        <uri>/UUID/cache</uri>
        <json>{
            "0x0006":"00",
            "0x0007":"00",
            "0x0008":"07",
            "0x0009":"00",
            "0x000a":"03",
            "0x0089":"",
            ...
        }</json>
    </response>
</body>
```

## Authentication

The authentication process has a few steps.  First, we use Oauth2 to authenticate to the HTTPS API.  After 
authenticating, we can get a mobile device token, which in turn be used to get a new `Bearer` token, which, finally,
is used to get XMPP credentials to authenticate to the Jabber server.  In `gekitchen`, going from username/password
to XMPP credentials is handled by `do_full_login_flow(username, password)`.

## Useful functions

### `do_full_login_flow(username, password)`
Function to authenticate to the web API and get XMPP credentials.  Returns a `dict` of XMPP credentials

## Objects
### GeClient(xmpp_credentials, event_loop=None, **kwargs)
Main XMPP client, and a subclass of `slixmpp.ClientXMPP`.
 * `xmpp_credentials: dict` A dictionary of XMPP credentials, usually obtained from either `do_full_login_flow` or, in a
 more manual process, `get_xmpp_credentials` 
 * `event_loop: asyncio.AbstractEventLoop` Optional event loop.  If `None`, the client will use `asyncio.get_event_loop()`
 * `**kwargs` Passed to `slixmpp.ClientXMPP`
#### Useful Methods
 * `connect()` Connect to the XMPP server
 * `process_in_running_loop(timeout: Optional[int] = None)` Run in an existing event loop.  If `timeout` is given, stop
 running after `timeout` seconds
 * `add_event_handler(name: str, func: Callable)` Add an event handler.  In addition to the events supported by
 `slixmpp.ClientXMPP`, we've added some more event types detailed below.
#### Properties
 * `appliances` A `Dict[str, GeAppliance]` of all known appliances keyed on the appliances' JIDs.

## Events

In addition to the standard `slixmpp` events, the `GeClient` object has support for the following:

* `'add_appliance'` - Triggered after a new appliance is added. The `GeAppliance` object is passed to the callback
* `'appliance_state_change'` - Triggered when an appliance message with a new state, different from the existing, cached
state is received.  A tuple `(appliance, state_changes)` is passed to the callback, where `appliance` is the 
`GeAppliance` object with the updated state and `state_changes` is a dictionary `{erd_key: new_value}` of the changed
state.

