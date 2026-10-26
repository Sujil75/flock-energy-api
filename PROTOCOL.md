# Flock Energy Portal — Protocol Discoveries

This document records the upstream behavior observed while inspecting and testing the Flock Energy legacy portal. It distinguishes confirmed observations from behavior that remains unverified.

## 1. Portal and inspection

- **Portal:** `https://urja-ops.flockenergy.tech`
- **Browser used for inspection:** Mozilla Firefox
- **Inspection tools:** Browser Developer Tools, Network tab, Fetch/XHR filtering, and persisted network logs.
- **Authentication:** The portal requires login for the requests used by this adapter. Credentials and session-cookie values are intentionally excluded from this document.

## 2. Authentication and session handling

### Login request

- **Page and request path:** `/login`
- **Method:** `POST`
- **Payload fields used by the adapter:** `email` and `password`
- **Request headers used by the adapter:** `Origin` and `Referer`
- **Transport status observed on successful login:** `200 OK`
- **Successful JSON response observed:**

```json
{
  "type": "redirect",
  "status": 303,
  "location": "/meters"
}
```

The `status` value above is part of the JSON response. It is not the HTTP status code; the observed HTTP response status was `200`.

### Failed login response observed

A failed login returned HTTP `200` with a JSON body containing:

```json
{
  "type": "failure",
  "status": 401,
  "data": "[{\"email\":1,\"error\":2},\"\",\"Invalid email or password.\"]"
}
```

The `401` here is the JSON response's `status` field, not the HTTP response status. The adapter must inspect the JSON result as well as the HTTP status to determine whether login succeeded.

### Session cookie

- **Observed cookie name:** `__Secure-better-auth.session_token`
- The `requests.Session` object retains cookies between the login request and subsequent upstream requests.
- The adapter checks for the expected cookie before marking the client as authenticated.
- Cookie values, passwords, and other authentication secrets must not be committed, printed, or returned by the API.

### Security and remaining uncertainty

- No explicit CSRF field or CSRF-related request header was identified in the inspected login request. This does not prove that the portal has no CSRF protection.
- Session expiration, cookie refresh, and the portal's exact session lifetime have not been tested.
- Re-authentication after an upstream session expires has not been verified.
- A successful login response and presence of a cookie do not independently prove that the cookie will authorize every endpoint; upstream requests must still handle authorization failures.

## 3. Meter listing

- **Portal page:** `/meters`
- **Upstream endpoint:** `GET /portal/meters/search`
- **Observed request:** `/portal/meters/search?q=&page=1`
- **Query parameters:**
  - `q`: search string; observed as empty.
  - `page`: page number; observed as `1`.
- **Observed HTTP status:** `200 OK`
- **Observed content type:** `application/json`
- **Authentication:** The browser request included the session cookie.
- **UI observation:** 403 meters and 21 pages were displayed at the time of inspection. These are observations from that session, not guaranteed totals.

### Observed meter-list item

```json
{
  "meterId": "J100000",
  "serialNo": "SE33962",
  "make": "HPL",
  "phaseType": "single",
  "installStatus": "Decommissioned",
  "dtCode": "DT-001"
}
```

The adapter normalizes these fields to `meter_id`, `serial_number`, `make`, `phase_type`, `installation_status`, and `dt_code`.

**Response-envelope limitation:** The supplied observation establishes the item fields but does not fully document every possible response envelope or the upstream pagination metadata. The adapter currently supports a direct list or an object with a `data` list. That assumption should be revisited if the portal response format changes.

## 4. Meter details — SvelteKit page data

### Endpoint confirmed by browser request

- **Method:** `GET`
- **Path pattern:** `/meters/{meter_id}/__data.json`
- **Observed request:** `/meters/J100004/__data.json?x-sveltekit-invalidated=001`
- **Observed content type:** `application/json`
- **Authentication:** The browser request included the session cookie.
- **Referer observed in the copied request:** `https://urja-ops.flockenergy.tech/meters`

**Important:** The working filename has two leading underscores: `__data.json`. The earlier `_data.json` path (one leading underscore) returned `404` when requested by the adapter.

### Observed response shape

The response is a SvelteKit page-data object containing a `type` field and a `nodes` array. For the observed meter, the relevant data was located at `nodes[2]["data"]`. Within that array, index `3` held a JSON-encoded string with the installed-meter fields.

A shortened representation of the relevant structure:

```json
{
  "type": "data",
  "nodes": [
    {"type": "skip"},
    {"type": "skip"},
    {
      "type": "data",
      "data": [
        {"meterId": 1, "detail": 2, "hierarchy": 4},
        "J100004",
        {"classData": 3},
        "{\"installed_meter\":{\"MeterId\":\"J100004\",\"SerialNo\":\"SE65293\",\"Make\":\"Genus\",\"PhaseType\":\"single\",\"InstallationStatus\":\"Faulty\",\"InstallationType\":\"CT Operated\"}}"
      ],
      "uses": {"params": ["id"]}
    }
  ]
}
```

The full observed data array also included hierarchy values:

- Zone: `Jaipur Zone 2 (Z-02)`
- Circle: `Circle 5 (C-05)`
- Division: `Division 5 (D-05)`
- Subdivision: `Subdivision 5 (SD-05)`
- Substation: `Substation 5 (SS-05)`
- Feeder: `Feeder 5 (F-005)`
- Distribution transformer: `Bani Park DT 5 (DT-005)`

### Observed meter metadata

| Upstream field | Observed value |
|---|---|
| `MeterId` | `J100004` |
| `SerialNo` | `SE65293` |
| `Make` | `Genus` |
| `PhaseType` | `single` |
| `InstallationStatus` | `Faulty` |
| `InstallationType` | `CT Operated` |

The adapter extracts these values and returns normalized fields: `meter_id`, `serial_number`, `make`, `phase_type`, `installation_status`, `installation_type`, and a normalized `hierarchy` object.

### Implementation caveat

The `nodes[2]["data"]` and numeric-index mapping reflects the response observed during inspection. SvelteKit page-data structures are framework-specific and may change. The adapter should fail clearly on unexpected structures rather than silently returning incorrect fields.

## 5. Consumption history

- **Method:** `GET`
- **Endpoint pattern:** `/portal/meters/{meter_id}/energy`
- **Observed request:** `/portal/meters/J100004/energy`
- **Observed HTTP status:** `200 OK`
- **Observed content type:** `application/json`
- **Authentication:** The request included the session cookie.

The response contains a `data` array of readings. An observed reading was:

```json
{
  "timestamp": "23/06/2026 23:30",
  "kwh": "20403.4",
  "kvah": "22035.67",
  "volt": "239"
}
```

### Normalization

The adapter converts valid numeric strings to numeric values:

- `kwh` → floating-point number
- `kvah` → floating-point number
- `volt` → floating-point number

The timestamp is currently retained as a string in the format observed from the portal. Its timezone and date-format stability have not been verified. Date-range filtering and upstream pagination have not been confirmed.

The endpoint supplies JSON, so HTML table parsing is not required for these readings while this endpoint remains available.

## 6. Geographic data

- **Method:** `GET`
- **Endpoint pattern:** `/portal/meters/{meter_id}/geo`
- **Observed request:** `/portal/meters/J100004/geo`
- **Observed HTTP status:** `200 OK`
- **Observed content type:** `application/json`
- **Authentication:** The request included the session cookie.

The response contains a `data` object. Observed values:

```json
{
  "data": {
    "latitude": "26.907425164505934",
    "longitude": "75.72503661059095"
  }
}
```

The adapter converts latitude and longitude strings to numeric values. Additional geographic metadata has not been established by the observed response.

## 7. Adapter API and data flow

The adapter exposes these routes:

| Method | Adapter endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/meters?q=&page=1` | Search/list meters |
| `GET` | `/api/v1/meters/{meter_id}` | Normalized meter details and hierarchy |
| `GET` | `/api/v1/meters/{meter_id}/energy` | Normalized energy readings |
| `GET` | `/api/v1/meters/{meter_id}/location` | Normalized coordinates |

The implementation separates responsibilities:

1. `app/clients/legacy_client.py` handles login, session cookies, and upstream HTTP requests.
2. `app/schemas/normalizers.py` extracts and normalizes upstream response fields.
3. `app/schemas/meters.py` defines Pydantic schemas for the adapter's normalized response contracts.
4. `app/api/meters.py` exposes the REST endpoints and maps errors to HTTP responses.

The adapter does not currently persist upstream meter data in a database.

## 8. Error handling and limitations

- Adapter-side invalid meter identifiers are intended to produce HTTP `400`.
- Invalid query parameters such as a page number below `1` are rejected by FastAPI with HTTP `422`.
- Upstream failures are generally translated to HTTP `502` by route handlers.
- The upstream portal's HTTP `401`, `403`, and `404` responses have been observed during development in different circumstances. A `404` occurred when the adapter used `_data.json`; the browser's working request used `__data.json`.
- The exact upstream status and response body should be captured safely in diagnostics during development, without exposing credentials or cookie values.
- The current login check verifies the expected cookie exists after a successful-looking response. It does not independently verify that the session remains authorized for every subsequent request.
- Meter-detail normalization depends on the observed SvelteKit response structure.
- The full upstream pagination envelope for meter listing has not been fully documented.
- Session expiry, automatic re-login, date-range filtering, and long-term endpoint stability remain unverified.

## 9. Security requirements

- Store portal credentials in environment variables; do not hardcode them.
- Keep `.env` out of version control.
- Never log or return passwords, cookie values, or session tokens.
- Use HTTPS for upstream requests.
- Validate path parameters and query parameters.
- Do not expose the upstream session cookie to API consumers.
- Only expose meter data to callers authorized by the deployment's access-control policy. The current adapter's portal authentication is upstream authentication and does not, by itself, authenticate API consumers.

## 10. Verification summary

| Upstream request | Observed result | Confirmed finding |
|---|---|---|
| `GET /portal/meters/search?q=&page=1` | `200` | JSON meter listing; item field names observed |
| `GET /portal/meters/J100004/energy` | `200` | JSON energy readings |
| `GET /portal/meters/J100004/geo` | `200` | JSON coordinates |
| `GET /meters/J100004/__data.json?x-sveltekit-invalidated=001` | `200` | SvelteKit page data containing meter metadata and hierarchy |
| `POST /login` with valid credentials | HTTP `200`, JSON redirect result | Session cookie `__Secure-better-auth.session_token` observed |
| `POST /login` with invalid credentials | HTTP `200`, JSON failure result with embedded status `401` | Login success must be determined from the JSON result, not HTTP status alone |

These findings reflect the observed portal behavior during this project. They are not a guarantee that undocumented internal endpoints will remain stable.
