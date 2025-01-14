# jupyterlite-simple-cors-proxy
Simple CORS proxy for making http requests from JupyterLite

## Installation

```bash
pip install jupyterlite-simple-cors-proxy
```

## Usage

```python
from jupyterlite_simple_cors_proxy.proxy import cors_proxy_get, robust_get_request, furl, xurl

# Set up
url = "https://api.example.com/data"
# Optional params
params = {"key": "value"}

# Get a cross-origin proxied url
cross_origin_url = xurl(url) # xurl(url, params)

# Get a file like object
# (Make the request, then create a file like object
# from the response)
file_ob = furl(url) # furl(url, params)

# Make a request
response = cors_proxy_get(url, params)

# Use like requests
print(response.text)
data = response.json()
raw = response.content
```

The `robust_get_request()` will first try a simple request, then a proxied request: `robust_get_request(url, params)`

## Features

- Simple CORS proxy wrapper
- Requests response object
- Support for URL parameters
