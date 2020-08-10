"""Utility functions provided for documentation purposes"""

import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# These constants were lifted directly from the config.properties in the Android APK
# Yes, the encryption really was stored in the same file.  Yes, they really should be embarrassed.
CRYPT_KEY = "geKitchenAndroid".encode('ascii')

# Client id
CLIENT_ID_PRODUCTION = bytes.fromhex(
    "23BAE464CCEAB1BE85F83FB71362B458A0C11C246975D02768F66100B52A8DD3B7E557958C8F93623965A6648F11CA49"
)
CLIENT_ID_FIELD = bytes.fromhex(
    "47211A6E64A1860512D89CAB11995CCBE5148D5ADBEBC2A746918F5FC57E4F3C07A551217CE2BE8D533EDBC2068CC238"
)

# client secret
CLIENT_SECRET_PRODUCTION = bytes.fromhex(
    "833248D2530FC0593CDE6D880DB17574BE27B3DCEF148A98853511AD3D96A5BE2B9B52FCF654F1126C3BABC88076B3DE"
    "6C110BC2D8B4F50226DF1FF012E888F8F09EF93FEF6E451D364F74F6B39DD98F"
)
CLIENT_SECRET_FIELD = bytes.fromhex(
    "10461990F551C3DF1AB1CEA0ED0C3D5B0C339205B29E97F7C869F92280DD92DCBD1FBC9A35A7AC5FBB606662A67E1148"
    "B92CD0C588B8C22F48E46B44AA3FC582F09EF93FEF6E451D364F74F6B39DD98F"
)

# Redirect URI
REDIRECT_URI_PRODUCTION = bytes.fromhex(
    "4934CC358DA408C26F948248AF7DD434145E3BEEA860EFB81017F9E4E93A4CB44DA6E9B0218BD7E3759537FDDD0C03A35"
    "812860067FE1DD1A40831B101546DEF"
)
REDIRECT_URI_FIELD = bytes.fromhex(
    "B2290735A24D5F5FAF099822BECA736E5F43D83837E0D0A63B23500C86AEE6CB87E2327CF482BD5F2612911666F4DD138"
    "88B056E1A5E2509F828FD1CF64C1497"
)

# App ID
APP_ID_PRODUCTION = bytes.fromhex("4F73FCB16F54313979BCFB6DE1CB66794B5D28FA89B367C201A318C770976515")
APP_ID_FIELD = bytes.fromhex("4F73FCB16F54313979BCFB6DE1CB667995D405E80D40D247BC849B36AA7F0B5F")


def ge_decrypt(cypher_bytes: bytes) -> bytes:
    """Decrypt the obfuscated oauth2 parameters"""
    backend = default_backend()
    cipher = Cipher(algorithms.AES(CRYPT_KEY), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()

    plain_bytes = decryptor.update(cypher_bytes) + decryptor.finalize()

    return plain_bytes


print(ge_decrypt(APP_ID_PRODUCTION))
print(ge_decrypt(CLIENT_ID_PRODUCTION))
print(ge_decrypt(CLIENT_SECRET_PRODUCTION))
print(ge_decrypt(REDIRECT_URI_PRODUCTION))


def _decode_endpoints(crypt: str) -> str:
    """Decode a GE endpoint."""
    return base64.b64decode(crypt).decode('ascii')


_ACCOUNT_SERVER_PRODUCTION = _decode_endpoints("aHR0cHM6Ly9hY2NvdW50cy5icmlsbGlvbi5nZWFwcGxpYW5jZXMuY29tLw==")
_API_ENDPOINT_PRODUCTION = _decode_endpoints("aHR0cHM6Ly9hcGkuYnJpbGxpb24uZ2VhcHBsaWFuY2VzLmNvbS8=")
_CLOUD_SERVER_PRODUCTION = _decode_endpoints("aHR0cHM6Ly9zZWN1cmUuYnJpbGxpb24uZ2VhcHBsaWFuY2VzLmNvbS8=")
_DRS_ENDPOINT_PRODUCTION = _decode_endpoints("aHR0cHM6Ly9kcnMuYnJpbGxpb24uZ2VhcHBsaWFuY2VzLmNvbS8=")
_NEST_ENDPOINT_PRODUCTION = _decode_endpoints("aHR0cHM6Ly9uZXN0LmJyaWxsaW9uLmdlYXBwbGlhbmNlcy5jb20v")
_EXTRA_ENDPOINT_PRODUCTION = "https://wca-mobile-brand-content-prd.brillion.geappliances.com/"
