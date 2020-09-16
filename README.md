# gekitchen
Python SDK for GE WiFi-enabled kitchen appliances.
The primary goal is to use this to power integrations for [Home Assistant](https://www.home-assistant.io/), though that
will probably need to wait on some new entity types.   

## Installation
```pip install gekitchen```

## Usage
### Simple example
Here we're going to run the client in a pre-existing event loop.  We're also going to register some event callbacks
to update appliances every five minutes and to turn on our oven the first time we see it.  Because that is safe!
```python
import aiohttp
import asyncio
import logging
from gekitchen.secrets import USERNAME, PASSWORD
from gekitchen import GeWebsocketClient

_LOGGER = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    loop = asyncio.get_event_loop()
    client = GeWebsocketClient(loop, USERNAME, PASSWORD)

    session = aiohttp.ClientSession()
    asyncio.ensure_future(client.async_get_credentials_and_run(session), loop=loop)
    loop.run_until_complete(asyncio.sleep(60))

    for appliance in client.appliances:
        print(appliance)
```

## Authentication
The authentication process has a few steps.  First, for both the websocket and XMPP APIs, we use Oauth2 to authenticate
to the HTTPS API.  From there, we can either get a websocket endpoint with `access_token` or proceed with the XMPP login
flow.  For XMPP, we get a mobile device token, which in turn be used to get a new `Bearer` token, which, finally,
is used to get XMPP credentials to authenticate to the Jabber server.  In `gekitchen`, going from username/password
to XMPP credentials is handled by `do_full_xmpp_flow(username, password)`.

## Useful functions
### `do_full_xmpp_flow(username, password)`
Function to authenticate to the web API and get XMPP credentials.  Returns a `dict` of XMPP credentials
### `do_full_wss_flow(username, password)`
Function to authenticate to the web API and get websocket credentials.  Returns a `dict` of WSS credentials

## Objects
### GeWebsocketClient(event_loop=None, username=None, password=None)
Main Websocket client
 * `event_loop: asyncio.AbstractEventLoop` Optional event loop.  If `None`, the client will use `asyncio.get_event_loop()`
 * `username`/`password` Optional strings to use when authenticating
#### Useful Methods
 * `async_get_credentials(session, username=None, password=None)` Get new WSS credentials using either the specified 
 `username` and `password` or ones already set in the constructor. 
 * `get_credentials(username=None, password=None)` Blocking version of the above
 * `add_event_handler(event, callback)` Add an event handler
 * `disconnect()` Disconnect the client
 * `async_run_client()` Run the client
 * `async_get_credentials_and_run(sessions, username=None, password=None)` Authenticate and run the client
#### Properties
 * `appliances` A `Dict[str, GeAppliance]` of all known appliances keyed on the appliances' JIDs.
#### Events
* `EVENT_ADD_APPLIANCE` - Triggered immediately after a new appliance is added, before the initial update request has
even been sent. The `GeAppliance` object is passed to the callback.
* `EVENT_APPLIANCE_INITIAL_UPDATE` - Triggered when an appliance's type changes, at which point we know at least a 
little about the appliance. The `GeAppliance` object is passed to the callback.
* `EVENT_APPLIANCE_STATE_CHANGE` - Triggered when an appliance message with a new state, different from the existing, cached
state is received.  A tuple `(appliance, state_changes)` is passed to the callback, where `appliance` is the 
`GeAppliance` object with the updated state and `state_changes` is a dictionary `{erd_key: new_value}` of the changed
state.
* `EVENT_APPLIANCE_UPDATE_RECEIVED` - Triggered after processing an ERD update message whether or not the state changed
* `EVENT_CONNECTED` - Triggered when the API connects, after adding basic subscriptions
* `EVENT_DISCONNECTED` - Triggered when the API disconnects
* `EVENT_GOT_APPLIANCE_LIST` - Triggered when we get the list of appliances

### GeXmppClient(xmpp_credentials, event_loop=None, **kwargs)
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
#### Events
In addition to the standard `slixmpp` events, the `GeClient` object has support for the following:
* `EVENT_ADD_APPLIANCE` - Triggered immediately after a new appliance is added, before the initial update request has
even been sent. The `GeAppliance` object is passed to the callback.
* `EVENT_APPLIANCE_INITIAL_UPDATE` - Triggered when an appliance's type changes, at which point we know at least a 
little about the appliance. The `GeAppliance` object is passed to the callback.
* `EVENT_APPLIANCE_STATE_CHANGE` - Triggered when an appliance message with a new state, different from the existing, cached
state is received.  A tuple `(appliance, state_changes)` is passed to the callback, where `appliance` is the 
`GeAppliance` object with the updated state and `state_changes` is a dictionary `{erd_key: new_value}` of the changed
state.

### GeAppliance(mac_addr, client)
Representation of a single appliance
 * `mac_addr: Union[str, slixmpp.JID]` The appliance's MAC address, which is what GE uses as unique identifiers 
 * `client: GeBaseClient` The client used to communicate with the device
#### Useful Methods
 * `decode_erd_value(erd_code: ErdCodeType, erd_value: str)` Decode a raw ERD property value.
 * `encode_erd_value(erd_code: ErdCodeType, erd_value: str)` Decode a raw ERD property value.
 * `get_erd_value(erd_code: ErdCodeType)` Get the cached value of ERD code `erd_code`.  If `erd_code` is a string, this
 function will attempt to convert it to an `ErdCode` object first.
 * `async_request_update()` Request the appliance send an update of all properties
 * `set_available()` Mark the appliance as available
 * `async_set_erd_value(erd_code: ErdType, value)` Tell the device to set the property represented by `erd_code` to `value` 
 * `set_unavailable()` Mark the appliance as unavailable
 * `update_erd_value(erd_code: ErdType, value)` Update the local property cache value for `erd_code` to `value`, where
 value is the not yet decoded hex string sent from the API. Returns `True` if that is a change in state, `False` otherwise.
 * `update_erd_values(self, erd_values: Dict[ErdCodeType, str])` Update multiple values in the local property cache.
 Returns a dictionary of changed states or an empty `dict` if nothing actually changed.
#### Properties
 * `appliance_type: Optional[ErdApplianceType]` The type of appliance, `None` if unknown
 * `available: bool` `True` if the appliance is available, otherwise `False`
 * `mac_addr` The appliance's MAC address (used as the appliance ID)
 

### Useful `Enum` types
* `ErdCode` `Enum` of known ERD property codes
* `ErdApplianceType` Values for `ErdCode.APPLIANCE_TYPE`
* `ErdMeasurementUnits` Values for `ErdCode.TEMPERATURE_UNIT`
* `ErdOvenCookMode` Possible oven cook modes, used for `OvenCookSetting` among other things
* `ErdOvenState` Values for `ErdCode.LOWER_OVEN_CURRENT_STATE` and `ErdCode.UPPER_OVEN_CURRENT_STATE` 

### Other types
* `OvenCookSetting` A `namedtuple` of an `ErdOvenCookMode` and an `int` temperature
* `OvenConfiguration` A `namedtuple` of boolean properties representing an oven's physical configuration



## API Overview

The GE SmartHQ app communicates with devices through (at least) three different APIs: XMPP, HTTP REST, and what they 
seem to call MQTT (though that's not really accurate).  All of them are based around sending (pseudo-)HTTP requests
back and forth.  Device properties are represented by hex codes (represented by `ErdCode` objects in `gekitchen`), and 
values are sent as hexadecimal strings without leading `"0x"`, then json encoded as a dictionary.  One thing that is
important to note is that not all appliances support every API.

1. REST - We can access or set most device properties via HTTP REST.  Unfortunately, relying on this means we need to
 result to constantly polling the devices, which is less than desirable, especially, e.g., for ovens that where we want
 to know exactly when a timer finishes. This API is not directly supported.
2. Websocket "MQTT" - The WSS "MQTT" API is basically a wrapper around the REST API with the ability to subscribe to a
 device, meaning that we can treat it as (in Home Assistant lingo) IoT Cloud Push instead of IoT Cloud Polling.  In 
 `gekitchen`, support for the websocket API is provided by the `GeWebsocketClient` class. 
2. XMPP - As far as I can tell, there seems to be little, if any, benefit to the XMPP API except that it will notify
 the client if a new device becomes available.  I suspect that this can be achieved with websocket API as well via
 subscriptions, but have not yet tested.  Support for the XMPP API is provided by the `GeXmppClient` class, based on
  [`slixmpp`](https://slixmpp.readthedocs.io/), which it requires as an optional dependency.  

### XMPP API
The device informs the client of a state change by sending a `PUBLISH` message like this, informing us that the value of
property 0x5205 (`ErdCode.LOWER_OVEN_KITCHEN_TIMER` in `gekitchen`) is now "002d" (45 minutes):

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
In `gekitchen`, that would handled by the `GeAppliance.set_erd_value` method:
```python
appliance.async_set_erd_value(ErdCode.LOWER_OVEN_KITCHEN_TIMER, timedelta(minutes=45))
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
