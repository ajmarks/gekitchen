"""HTTP authentication flow to get XMPP loggin credentials"""

try:
    import re2 as re
except ImportError:
    import re
import logging
import requests
from lxml import etree
from gekitchen.const import (
    API_URL,
    LOGIN_URL,
    OAUTH2_APP_ID,
    OAUTH2_CLIENT_ID,
    OAUTH2_CLIENT_SECRET,
    OAUTH2_REDIRECT_URI,
)
from gekitchen.exc import GeAuthError

from typing import Dict
from urllib.parse import urlparse, parse_qs

_LOGGER = logging.getLogger(__name__)


def get_oauth2_token(session: requests.Session, username: str, password: str):
    """Hackily get an oauth2 token until I can be bothered to do this correctly"""
    params = {
        'client_id': OAUTH2_CLIENT_ID,
        'response_type': 'code',
        'access_type': 'offline',
        'redirect_uri': OAUTH2_REDIRECT_URI,
    }

    r1 = session.get(f'{LOGIN_URL}/oauth2/auth', params=params)

    email_regex = (
        r'^\s*(\w+(?:(?:-\w+)|(?:\.\w+)|(?:\+\w+))*\@'
        r'[A-Za-z0-9]+(?:(?:\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9][A-Za-z0-9]+)\s*$'
    )
    clean_username = re.sub(email_regex, r'\1', username)

    etr = etree.HTML(r1.text)
    post_data = {
        i.attrib['name']: i.attrib['value']
        for i in etr.xpath("//form[@id = 'frmsignin']//input")
        if 'value' in i.keys()
    }
    post_data['username'] = clean_username
    post_data['password'] = password

    r2 = session.post(f'{LOGIN_URL}/oauth2/g_authenticate', data=post_data, allow_redirects=False)
    code = parse_qs(urlparse(r2.headers['Location']).query)['code'][0]

    r3 = session.post(
        f'{LOGIN_URL}/oauth2/token',
        data={
            'code': code,
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
            'redirect_uri': OAUTH2_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }, auth=(OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET)
    )
    oauth_token = r3.json()
    try:
        session.headers.update({'Authorization': 'Bearer ' + oauth_token['access_token']})
    except KeyError:
        # TODO: make this better
        raise GeAuthError(f'Failed to get a token: {oauth_token}')
    return oauth_token


def get_mobile_device_token(session: requests.Session) -> str:
    """Get a mobile device token"""
    mdt_data = {
        'kind': 'mdt#login',
        'app': OAUTH2_APP_ID,
        'os': 'google_android'
    }
    r = session.post(f'{API_URL}/v1/mdt', json=mdt_data)
    results = r.json()
    try:
        return r.json()['mdt']
    except KeyError:
        raise GeAuthError(f'Failed to get a mobile device token: {results}')


def get_ge_token(session: requests.Session, mobile_device_token: str) -> str:
    """Get the GE token that we can use to get XMPP credentials"""
    params = {
        'client_id': OAUTH2_CLIENT_ID,
        'client_secret': OAUTH2_CLIENT_SECRET,
        'mdt': mobile_device_token
    }
    r = session.post(f'{LOGIN_URL}/oauth2/getoken', params=params)
    results = r.json()
    try:
        return results['access_token']
    except KeyError:
        raise GeAuthError(f'Failed to get a GE token: {results}')


def get_xmpp_credentials(ge_token: str) -> Dict:
    """Get XMPP credentials"""
    r = requests.get(
        f'{API_URL}/v1/mdt/credentials',
        headers={'Authorization': f'Bearer {ge_token}'}
    )
    return r.json()


def do_full_login_flow(username: str, password: str) -> Dict:
    """Perform a complete login flow, returning XMPP credentials."""
    login_session = requests.session()

    _LOGGER.debug('Getting oauth2 token')
    get_oauth2_token(login_session, username, password)

    _LOGGER.debug('Getting mobile device token')
    mdt = get_mobile_device_token(login_session)

    _LOGGER.debug('Getting GE token')
    ge_token = get_ge_token(login_session, mdt)

    _LOGGER.debug('Getting XMPP credentials')
    xmpp_credentials = get_xmpp_credentials(ge_token)

    return xmpp_credentials
