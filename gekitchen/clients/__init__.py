"""GE Client implementations"""

import logging
from .base_client import GeBaseClient
from .websocket_client import GeWebsocketClient

_LOGGER = logging.getLogger(__name__)

try:
    from .xmpp_client import GeXmppClient
except ImportError:
    _LOGGER.info("XMPP client not avaible.  You may need to install slximpp.")
