# Volvo Connected Vehicle API

This is an unofficial Python client for the [Volvo Connected Vehicle API](https://developer.volvocars.com/apis/connected-vehicle/v2/overview/). It is based on the [official API documentation](https://developer.volvocars.com/apis/connected-vehicle/v2/specification/).

![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)

Source: [svrooij/py_volvo_connected](https://github.com/svrooij/py_volvo_connected)

## Installation

```bash
pip install volvo-connected
```

## Usage

```python
from kiota_bundle.default_request_adapter import DefaultRequestAdapter
from volvo_connected import (
  StaticAccessTokenProvider,
  VolvoAuthenticationProvider,
  VolvoConnectedClient
)

# Create an access token provider using a static access token
access_token_provider = StaticAccessTokenProvider("YOUR_ACCESS_TOKEN")

# Or explore the DynamicAccessTokenProvider that allows you to auto refresh the token

# Create an authentication provider using your VCC API key and the access token provider
auth_provider = VolvoAuthenticationProvider("YOUR_VCC_API_KEY", access_token_provider)

# Create a request adapter
request_adapter = DefaultRequestAdapter(auth_provider)

# Create a client
client = VolvoConnectedClient(request_adapter)
```

### Get all vehicles

```python
vehicles = await client.vehicles.get()
```

### Get vehicle by VIN

```python
vehicle = await client.vehicles.by_vin("YV4952NA4F120DEMO").get()
```

### Get Fuel or Battery level

```python
fuel_resp = await client.vehicles.by_vin("YV4952NA4F120DEMO").fuel.get()

fuel_resp.data.fuel_amount.value
# or
fuel_resp.data.battery_charge_level.value
```

### All other endpoints

This client is genereted based on the (adjusted) OpenAPI specification. And everything is strong typed, so go ahead and explore the API.