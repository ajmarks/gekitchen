# gekitchen
Python SDK for GE smart appliances

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

### Within an existing event loop
```python
import asyncio
from gekitchen import do_full_login_flow, GeClient

USERNAME = 'me@email.com'
PASSWORD = '$7r0nkP@s$w0rD'

xmpp_credentials = do_full_login_flow(USERNAME, PASSWORD)
evt_loop = asyncio.get_event_loop()

client = GeClient(xmpp_credentials, event_loop=evt_loop)
client.connect()

evt_loop.run_until_complete(client.process_in_running_loop(60))
```