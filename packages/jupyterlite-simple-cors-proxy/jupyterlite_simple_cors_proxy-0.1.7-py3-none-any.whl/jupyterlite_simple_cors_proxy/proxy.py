# File: simple_cors_proxy/proxy.py
from urllib.parse import urlencode, quote
import requests
import io

import platform
PLATFORM = platform.system().lower()

def xurl(url, params=None, force=False):
    """Generate a proxied URL."""
    if PLATFORM=="emscripten" or force:
        if params:
            url = f"{url}?{urlencode(params)}"
        url = f"https://corsproxy.io/{quote(url)}"

    return url

def furl(url, params=None, force=False):
    """Return file like object after calling the proxied URL."""
    r = cors_proxy_get(url, params, force)

    # Return a file-like object from the JSON string
    return io.BytesIO(r.content)


def cors_proxy_get(url, params=None, force=False):
    """
    CORS proxy for GET resources with requests-like response.

    Args:
        url (str): The URL to fetch
        params (dict, optional): Query parameters to include

    Returns:
        A requests response object.
    """
    proxy_url = xurl(url, params, force)

    # Do a simple requests get and
    # just pass through the entire response object
    return requests.get(proxy_url)


def robust_get_request(url, params=None):
    """
    Try to make a simple request else fall back to a proxy.
    """
    try:
        r = requests.get(url, params=params)
    except:
        r = cors_proxy_get(url, params=params)
    return r
