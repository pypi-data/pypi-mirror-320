import pytest
import asyncio
import pytest_asyncio
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
#from kiota_bundle.default_request_adapter import DefaultRequestAdapter
from kiota_abstractions.authentication import AnonymousAuthenticationProvider
from os import getenv
import sys
if (sys.path[1] != "/workspaces/volvo_connected/src"):
    sys.path.insert(1, "/workspaces/volvo_connected/src")

from volvo_connected import (
  StaticAccessTokenProvider,
  VolvoAuthenticationProvider,
  VolvoConnectedClient,
#   DefaultRequestAdapter
)

def get_client() -> VolvoConnectedClient:
    vcc: str = getenv("VOLVO_VCC_API_KEY");
    token: str = getenv("VOLVO_TOKEN");
    auth_provider = VolvoAuthenticationProvider(vcc, StaticAccessTokenProvider(token))
    return VolvoConnectedClient(HttpxRequestAdapter(auth_provider))

def test_no_request_adapter():
    with pytest.raises(TypeError):
        VolvoConnectedClient(None)

@pytest.mark.asyncio
async def test_get_vehicles():
    # Arrange
    client = get_client()

    # Act
    vehicles = await client.vehicles.get()

    # Assert
    assert vehicles is not None
    assert vehicles.data is not None 
    assert vehicles.data[0].vin is not None

@pytest.mark.asyncio
async def test_get_vehicle():
    # Arrange
    client = get_client()

    # Act
    vehicle = await client.vehicles.by_vin(getenv("VOLVO_VIN")).get()

    # Assert
    assert vehicle is not None
    assert vehicle.data is not None
    assert vehicle.data.vin is not None
    assert vehicle.data.images.exterior_image_url is not None
    assert vehicle.data.images.internal_image_url is not None
    assert vehicle.data.descriptions.model is not None

@pytest.mark.asyncio
async def test_get_windows():
    # Arrange
    client = get_client()

    # Act
    windows = await client.vehicles.by_vin(getenv("VOLVO_VIN")).windows.get()

    # Assert
    assert windows is not None
    assert windows.data is not None
    assert windows.data.front_left_window is not None
    assert windows.data.front_left_window.value is not None

@pytest.mark.asyncio
async def test_get_doors():
    # Arrange
    client = get_client()

    # Act
    doors = await client.vehicles.by_vin(getenv("VOLVO_VIN")).doors.get()

    # Assert
    assert doors is not None
    assert doors.data is not None
    assert doors.data.front_left_door is not None
    assert doors.data.front_left_door.value is not None

@pytest.mark.asyncio
async def test_get_engine_status():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).engine_status.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.engine_status is not None
    assert result.data.engine_status.value is not None

@pytest.mark.asyncio
async def test_get_engine():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).engine.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.engine_coolant_level_warning.value is not None
    assert result.data.oil_level_warning.value is not None

@pytest.mark.asyncio
async def test_get_warnings():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).warnings.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.brake_light_center_warning is not None
    assert result.data.brake_light_center_warning.value is not None

@pytest.mark.asyncio
async def test_get_tyres():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).tyres.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.front_left is not None
    assert result.data.front_left.value is not None

@pytest.mark.asyncio
async def test_get_statistics():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).statistics.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.average_speed_automatic is not None
    assert result.data.average_speed_automatic.value is not None
    assert result.data.average_speed is not None
    assert result.data.average_speed.value is not None

@pytest.mark.asyncio
async def test_get_odometer():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).odometer.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.odometer is not None
    assert result.data.odometer.value is not None

@pytest.mark.asyncio
async def test_get_fuel():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).fuel.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.battery_charge_level is not None
    assert result.data.battery_charge_level.value is not None

@pytest.mark.asyncio
async def test_get_commands():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).commands.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data[0].command is not None
    assert result.data[0].href is not None

@pytest.mark.asyncio
async def test_get_command_accessibility():
    # Arrange
    client = get_client()

    # Act
    result = await client.vehicles.by_vin(getenv("VOLVO_VIN")).command_accessibility.get()

    # Assert
    assert result is not None
    assert result.data is not None
    assert result.data.availability_status or result.data.unavailable_reason is not None

# if you want to run these tests with just F5, uncomment this
#asyncio.run(test_get_vehicles())