# Flock Energy Portal — Protocol Discoveries

## 1. Browser and Inspection Setup

- **Browser:** Mozilla Firefox
- **Developer Tools:** Opened using `Ctrl + Shift + I`
- **Network inspection:** Enabled `Persist Logs` to retain requests during navigation.
- **Network filter:** Fetch/XHR
- **Portal URL:** https://urja-ops.flockenergy.tech
- **Authentication:** Logged in using the assignment-provided credentials. Secret values are excluded from this document.

## 2. Login and Authentication

### Login Request

- **Login page:** `/login`
- **HTTP method:** `POST`
- **Request payload:** Username and password fields.
- **Content type:** Pending verification from the request headers.
- **Authentication result:** Successfully logged in to the portal.

### Login Payload and CSRF Inspection

| Item | Observation |
|---|---|
| Username field | Present in the request payload |
| Password field | Present in the request payload |
| CSRF token field | Not observed |
| CSRF-related request header | Not observed |
| Session cookie | Observed |
| Session cookie name | `_secure-better-auth.session_token` |

No explicit CSRF token field or related request header was identified during inspection. This does not establish that the portal lacks CSRF protection.

### Session Management

The authenticated consumption request included the `_secure-better-auth.session_token` cookie in its `Cookie` request header.

- **Cookie creation:** The login response's `Set-Cookie` header requires verification.
- **Session expiration:** Not yet tested.
- **Cookie refresh or replacement:** Not yet verified.
- **Automatic re-authentication:** Required for the adapter and pending implementation.

Session cookies, passwords, and other authentication secrets must not be committed to the repository or exposed in logs or API responses.

## 3. Meter Listing

### Discovered Endpoint

- **Page URL:** `https://urja-ops.flockenergy.tech/meters`
- **HTTP method:** `GET`
- **Endpoint path:** `/portal/meters/search`
- **Observed request:** `/portal/meters/search?q=&page=1`
- **Observed query parameters:**
  - `q`: Search query; observed as empty.
  - `page`: Page number; observed as `1`.
- **HTTP status:** `200 OK`
- **Response content type:** `application/json`
- **Authentication:** Request included the session cookie.
- **Total meters displayed:** 403.
- **Pagination displayed:** 21 pages.

### Visible Meter Fields

| Field | Description |
|---|---|
| Meter | Meter identifier |
| Serial | Meter serial number |
| Make | Manufacturer |
| Phase | Phase type |
| Status | Installation status |
| DT | Associated distribution transformer |

### Response Structure

The request returns JSON. The complete response schema, exact field names, and pagination metadata require inspection of the response body.

The endpoint appears to support searching and pagination through the `q` and `page` query parameters.

## 4. Meter Details

### Example Meter

- **Meter ID:** `J100004`
- **Page URL:** `https://urja-ops.flockenergy.tech/meters/J100004`
- **Data displayed:** Meter identifier, serial number, manufacturer, phase type, installation status, installation type, geographic coordinates, and consumption history.
- **Meter ID in page URL:** `J100004`

### Observed Meter Metadata

| Field | Observed value |
|---|---|
| MeterId | `J100004` |
| SerialNo | `SE65293` |
| Make | `Genus` |
| PhaseType | `single` |
| InstallationStatus | `Faulty` |
| InstallationType | `CT Operated` |

The exact network request supplying all meter metadata has not yet been conclusively identified.

## 5. Consumption History

### Discovered Endpoint

- **Host:** `urja-ops.flockenergy.tech`
- **HTTP method:** `GET`
- **Endpoint pattern:** `/portal/meters/{meter_id}/energy`
- **Observed request path:** `/portal/meters/J100004/energy`
- **Observed full URL:** `https://urja-ops.flockenergy.tech/portal/meters/J100004/energy`
- **HTTP status:** `200 OK`
- **Response content type:** `application/json`
- **Authentication:** The request included the `_secure-better-auth.session_token` cookie.

### Response Structure

The response contains a JSON `data` array with consumption readings.

| Field | Description | Observed example |
|---|---|---|
| `timestamp` | Date and time of the reading | `"23/06/2026 23:30"` |
| `kwh` | Energy reading in kilowatt-hours | `"20403.4"` |
| `kvah` | Apparent energy reading in kilovolt-ampere-hours | `"22035.67"` |
| `volt` | Voltage reading | `"239"` |

The observed measurement values are strings, so the adapter must validate and convert them to appropriate numeric types.

### Data Normalization Requirements

- Convert valid numeric measurement strings into numeric values.
- Parse timestamps into a consistent datetime representation.
- Verify the timestamp timezone before assigning timezone information.
- Handle missing, malformed, and inconsistent values.
- Investigate support for date-range filtering and pagination.
- Preserve the original response when necessary for debugging, without logging sensitive information.

### HTML Parsing

The consumption readings are available through a JSON endpoint. Parsing the visible consumption table is unnecessary if the endpoint remains accessible and supplies all required fields.

## 6. Geographic Data (`geo`)

### Discovered Endpoint

- **HTTP method:** `GET`
- **Endpoint pattern:** `/portal/meters/{meter_id}/geo`
- **Observed request path:** `/portal/meters/J100004/geo`
- **Full URL:** `https://urja-ops.flockenergy.tech/portal/meters/J100004/geo`
- **HTTP status:** `200 OK`
- **Response content type:** `application/json`
- **Authentication:** The request included the `_secure-better-auth.session_token` cookie.

### Response Structure

The response contains a `data` object with geographic coordinates.

| Field | Description | Observed value |
|---|---|---|
| `latitude` | Geographic latitude | `"26.907425164505934"` |
| `longitude` | Geographic longitude | `"75.72503661059095"` |

### Adapter Requirements

- Parse the JSON response.
- Validate latitude and longitude.
- Convert valid coordinate strings to numeric values.
- Handle missing or malformed coordinates.
- Associate the response with the requested meter ID.

### Observation

The geographic endpoint is meter-specific, with the meter ID embedded in the request path. The observed response provides coordinates but does not establish whether additional geographic metadata is available elsewhere.

## 7. Meter Metadata — SvelteKit Page Data

### Discovered Endpoint

- **HTTP method:** `GET`
- **Endpoint pattern:** `/meters/{meter_id}/_data.json`
- **First observed meter:** `J100004`
- **Second observed meter:** `J100011`
- **Example request:** `/meters/J100011/_data.json?x-sveltekit-invalidated=001`
- **HTTP status:** `200 OK`
- **Response content type:** `application/json`
- **Authentication:** Session cookie included in the request.

### Response Structure

The response contains a `type` field and a `nodes` array. A relevant node contains a nested `data` object with the selected meter's metadata.

Observed fields include:

- `MeterId`
- `SerialNo`
- `Make`
- `PhaseType`
- `InstallationStatus`
- `InstallationType`

The response also contains the electrical network hierarchy, including zone, circle, division, subdivision, substation, feeder, and distribution transformer.

### Verification

The endpoint was inspected for two different meters. The response contained different meter identifiers and metadata corresponding to the selected meter.

This confirms that the page-data response is meter-specific.

### Implementation Considerations

- Treat this as a SvelteKit page-data endpoint, not necessarily a stable public REST API.
- Verify whether its response structure is suitable for programmatic use.
- Extract only the required fields and normalize them into the adapter's own response schema.
- Do not rely on the framework-specific query parameter as a business-level meter identifier.
- Preserve session cookies securely when making authenticated requests.

## 8. Session Behavior and Security

### Confirmed Observations

- The portal requires authentication to access the pages inspected.
- The `_secure-better-auth.session_token` cookie was observed in an authenticated consumption request.
- The cookie value must remain confidential.
- No explicit CSRF token field or related request header was identified during login inspection.

### Pending Verification

- Whether the login response explicitly sets or updates the session cookie.
- Session expiration and re-authentication behavior.
- Responses to expired or invalid sessions.
- Whether all observed endpoints require the same authentication mechanism.
- Whether additional CSRF protections are implemented.

### Adapter Security Requirements

- Keep portal credentials and session cookies server-side.
- Never expose upstream session cookies through the REST API.
- Use HTTPS for upstream and client communication.
- Avoid logging passwords, cookie values, or other sensitive authentication material.
- Detect authentication failures and re-authenticate when appropriate.
- Validate meter identifiers and handle upstream errors safely.
- Avoid exposing meter data to unauthorized API consumers.

## 9. Network Inspection Summary

| Request | Status | Response type | Finding |
|---|---|---|---|
| `/portal/meters/search?q=&page=1` | 200 | JSON | Meter listing |
| `/portal/meters/J100004/energy` | 200 | JSON | Consumption history |
| `geo` | 200 | JSON | Geographic data, including coordinates |
| `_data.json?...` | 200 | JSON | Page-related data; exact role pending verification |

The paths for `geo` and `_data.json` must be recorded from their respective request headers before they are used in the implementation.

## 10. Observations, Limitations, and Implementation Implications

### Confirmed Findings

- The portal supports browser-based authentication.
- The login request uses HTTP POST and includes username and password fields.
- An authenticated session cookie is used in subsequent requests.
- Meter listing data is retrieved through a JSON request with search and pagination parameters.
- Consumption history is retrieved through a meter-specific JSON endpoint.
- Geographic data is available through a background JSON request.
- The meter detail page triggers multiple background JSON requests.

### Outstanding Investigation

- Exact login content type and payload field names.
- Complete meter-listing response schema and pagination metadata.
- Exact paths and schemas for `geo` and `_data.json`.
- Source of the meter detail metadata.
- Session expiration and automatic re-authentication behavior.
- Date-range filtering and pagination support for consumption history.
- Stability and authorized programmatic use of the observed endpoints.

### Implementation Implications

The adapter should separate session management, HTTP requests, response parsing, data normalization, and REST API routes.

It should expose consistent JSON responses, validate data, handle missing meters and malformed responses, and recover safely from expired authentication.

All implementation decisions should be based on observed protocol behavior rather than assumed endpoint structures.