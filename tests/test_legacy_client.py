from unittest.mock import patch, Mock
import pytest
from app.clients.legacy_client import LegacyPortalClient

@pytest.fixture
def client():
    with patch("app.clients.legacy_client.settings") as check_settings:
        check_settings.portal_base_url = "https://urja-ops.flockenergy.tech"
        check_settings.portal_username = "test-user"
        check_settings.portal_password = "test-password"

        instance = LegacyPortalClient()
        yield instance
        instance.session.close()  

def test_meter_list_rejects_invalid_page(client):
    with pytest.raises(ValueError):
        client.get_meter_list(page=0)


def test_meter_id_validation(client):
    assert client._validate_meter_id("J100004") == "J100004"

    with pytest.raises(ValueError):
        client._validate_meter_id("../login")


def test_meter_energy_uses_expected_path(client):
    with patch.object(client, "get_data", return_value={"data": []}) as check_get:
        client.get_meter_energy("J100004")

    check_get.assert_called_once_with("/portal/meters/J100004/energy")


def test_meter_location_uses_expected_path(client):
    with patch.object(client, "get_data", return_value={"data": {}}) as check_get:
        client.get_meter_location("J100004")

    check_get.assert_called_once_with("/portal/meters/J100004/geo")      

def test_login_accepts_redirect_response(client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "type": "redirect",
        "status": 303,
        "location": "/meters",
    }

    client.session.cookies.set(
        "_secure-better-auth.session_token",
        "test-session-token",
    )

    with patch.object(
        client.session,
        "post",
        return_value=mock_response,
    ) as mock_post:
        client.login()

    mock_post.assert_called_once()
    assert client.authenticated is True

def test_login_does_not_mark_authenticated_without_cookie(client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "type": "redirect",
        "status": 303,
        "location": "/meters",
    }

    with patch.object(
        client.session,
        "post",
        return_value=mock_response,
    ):
        with pytest.raises(RuntimeError, match="session cookie"):
            client.login()

    assert client.authenticated is False