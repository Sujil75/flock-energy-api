from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@patch("app.api.meters.LegacyPortalClient")
def test_list_meters(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.get_meter_list.return_value = [
        {
            "meterId": "J100000",
            "serialNo": "SE33962",
            "make": "HPL",
            "phaseType": "single",
            "installStatus": "Decommissioned",
            "dtCode": "DT-001",
        }
    ]

    response = client.get("/api/v1/meters?q=&page=1")

    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["meter_id"] == "J100000"
    assert body["data"][0]["serial_number"] == "SE33962"
    assert body["data"][0]["make"] == "HPL"


@patch("app.api.meters.LegacyPortalClient")
def test_list_meters_rejects_invalid_page(mock_client_class):
    response = client.get("/api/v1/meters?page=0")

    assert response.status_code == 422
    mock_client_class.assert_not_called()


@patch("app.api.meters.LegacyPortalClient")
def test_meter_details_upstream_failure(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.get_meter_details.side_effect = RuntimeError("Upstream failure")

    response = client.get("/api/v1/meters/J100004")

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Failed to retrieve meter details from the legacy portal"
    )


@patch("app.api.meters.LegacyPortalClient")
def test_meter_energy_returns_normalized_readings(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.get_meter_energy.return_value = {
        "data": [
            {
                "timestamp": "23/06/2026 23:30",
                "kwh": "20403.4",
                "kvah": "22035.67",
                "volt": "239",
            }
        ]
    }

    response = client.get("/api/v1/meters/J100004/energy")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["kwh"] == 20403.4
    assert body[0]["kvah"] == 22035.67
    assert body[0]["volt"] == 239.0


@patch("app.api.meters.LegacyPortalClient")
def test_meter_location_returns_coordinates(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.get_meter_location.return_value = {
        "data": {
            "latitude": "26.907425164505934",
            "longitude": "75.72503661059095",
        }
    }

    response = client.get("/api/v1/meters/J100004/location")

    assert response.status_code == 200
    body = response.json()
    assert body["latitude"] == 26.907425164505934
    assert body["longitude"] == 75.72503661059095

@patch("app.api.meters.LegacyPortalClient")
def test_invalid_meter_id_returns_400(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.get_meter_details.side_effect = ValueError("Invalid meter ID")

    response = client.get("/api/v1/meters/invalid%20meter")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid meter ID"
