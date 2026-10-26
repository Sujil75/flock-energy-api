import requests
from app.config import settings
from urllib.parse import urlencode
import re

class LegacyPortalClient:
    def __init__(self) -> None:
        self.base_url = settings.portal_base_url.rstrip("/")
        self.session = requests.Session()
        self.authenticated = False

    def _validate_meter_id(self, meter_id: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", meter_id):
            raise ValueError("Invalid Meter ID")

        return meter_id

    def login(self) -> None:
        login_url = f"{self.base_url}/login"

        response = self.session.post(
            login_url,
            data={
                "username": settings.portal_username,
                "password": settings.portal_password,
            },
            timeout=15,
        )
        response.raise_for_status()

        result = response.json()

        if result.get("type") != "redirect" or not result.get("location"):
            raise RuntimeError("Portal login did not return the expected redirect")

        if not self.session.cookies.get("_secure-better-auth.session_token"):
            raise RuntimeError("Login did not establish a session cookie")

        self.authenticated = True

    def get_data(self, path: str) -> dict | list:
        if not self.authenticated:
            self.login()

        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.get(url, timeout=15)
        response.raise_for_status()

        return response.json()

    def get_meter_list(self, query: str = "", page: int = 1) -> dict | list:
        if page < 1:
            raise ValueError("Page must be greater than or equal to 1")

        params = urlencode({
            "q": query,
            "page": page,
        })
        
        return self.get_data(
            f"/portal/meters/search?{params}"
        )

    def get_meter_details(self, meter_id: str) -> dict | list:
        meter_id = self._validate_meter_id(meter_id)

        return self.get_data(
            f"/meters/{meter_id}/_data.json?x-sveltekit-invalidated=001"
        )

    def get_meter_energy(self, meter_id: str) -> dict | list:
        meter_id = self._validate_meter_id(meter_id)

        return self.get_data(
            f"/portal/meters/{meter_id}/energy"
        )

    def get_meter_location(self, meter_id: str) -> dict | list:
        meter_id = self._validate_meter_id(meter_id)

        return self.get_data(
            f"/portal/meters/{meter_id}/geo"
        )