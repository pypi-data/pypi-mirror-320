# File: jupyterlite_simple_cors_proxy/__init__.py
from .proxy import cors_proxy_get, robust_get_request, xurl, furl
from .fastf1_proxy import enable_cors_proxy as fastf1_cors_proxy

__version__ = "0.1.7"
__all__ = ["cors_proxy_get", "robust_get_request", "xurl", "furl", "fastf1_cors_proxy"]
