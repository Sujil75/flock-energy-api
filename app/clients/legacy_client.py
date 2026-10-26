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

        response = self.session.get(login_url, timeout=15)
        response.raise_for_status()

        response = self.session.post(
            login_url,
            data={
                "email": settings.portal_username,
                "password": settings.portal_password,
            },
            headers={
                "Referer": login_url,
                "Origin": self.base_url,
            },
            timeout=15,
            allow_redirects=True,
        )
        response.raise_for_status()

        if not self.session.cookies.get("__Secure-better-auth.session_token"):
            raise RuntimeError("Login did not establish a session cookie")

        self.authenticated = True

    def get_data(self, path: str, headers: dict[str, str] | None = None) -> dict | list:
        if not self.authenticated:
            self.login()

        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.get(
            url, 
            headers=headers,
            timeout=30
        )
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
            f"/meters/{meter_id}/__data.json?x-sveltekit-invalidated=001",
            headers={"Referer": f"{self.base_url}/meters"},
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