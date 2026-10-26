# Flock Energy API Adapter

A REST API adapter built with FastAPI that exposes normalized endpoints for meter data from the legacy Flock Energy portal.

## Features

- Authenticates with the legacy portal and maintains a session using `requests.Session`.
- Retrieves meter lists with search and pagination.
- Retrieves individual meter details and network hierarchy.
- Retrieves meter energy readings and location coordinates.
- Normalizes legacy response fields into a consistent API structure.
- Documents endpoints using OpenAPI and Swagger UI.
- Includes automated tests for client behavior and validation.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Requests
- Pytest

## Project Structure

```text
flock-energy-api/
├── app/
│   ├── api/
│   │   └── meters.py
│   ├── clients/
│   │   └── legacy_client.py
│   ├── schemas/
│   │   ├── meters.py
│   │   └── normalizers.py
│   ├── config.py
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_legacy_client.py
├── openapi.json
├── PROTOCOL.md
├── README.md
├── REFLECTION.md
├── requirements.txt
└── .gitignore
```

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
PORTAL_BASE_URL=https://urja-ops.flockenergy.tech
PORTAL_USERNAME=your_portal_email
PORTAL_PASSWORD=your_portal_password
```

Do not commit `.env` or any credentials, cookies, or session tokens.

### 4. Start the API

From the project root:

```powershell
fastapi dev app/main.py
```

The local API is available at `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/meters?q=&page=1` | Search and paginate meters |
| GET | `/api/v1/meters/{meter_id}` | Get meter details and hierarchy |
| GET | `/api/v1/meters/{meter_id}/energy` | Get energy readings |
| GET | `/api/v1/meters/{meter_id}/location` | Get meter coordinates |

### Interactive documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Running Tests

Run the automated test suite from the project root:

```powershell
python -m pytest -v
```

## Configuration and Limitations

- The adapter depends on the legacy portal being available and accepting the configured credentials.
- The portal's internal response formats may change and require updates to the client or normalizers.
- Meter details currently depend on the structure returned by the portal's SvelteKit `__data.json` endpoint.
- Upstream errors are translated into HTTP error responses by the adapter.

## Project Documentation

- `PROTOCOL.md` documents the legacy portal's authentication and endpoint behavior.
- `REFLECTION.md` records implementation decisions, challenges, and lessons learned.
- `openapi.json` contains the exported OpenAPI specification.
