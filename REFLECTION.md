# What I Learned from This Project: My REFLECTION

## 1. `pydantic_settings`

- Normally, Pydantic is used for data validation, whereas `pydantic_settings` is used to manage application settings and load values from environment variables and configured sources such as a `.env` file.
- Pydantic itself does not automatically load `.env` files without additional configuration.
- By using `BaseSettings` and `SettingsConfigDict` from `pydantic_settings`, I learned how to configure environment variable loading and validate the resulting settings.
- In this project, I defined the portal base URL, email, and password in the `.env` file and accessed them throughout the application by importing `settings` from `app.config`.
- This helped me understand how to separate configuration from application logic and avoid hardcoding sensitive values in the source code.
- I can reuse this approach in future backend projects, including AI-related applications that require API keys, database URLs, model configurations, or other environment-specific settings.

## 2. Session Requests

- Before this project, I knew how to consume APIs, but I had not worked with maintaining an authenticated session while accessing a legacy portal.
- Normally, independent HTTP requests do not automatically share cookies or other session state. A session allows requests made through the same session object to retain and reuse cookies when applicable.
- In this project, I used `requests.Session()` and stored it in `self.session` inside `LegacyPortalClient`.
- This allowed the login request to establish a session cookie that could be reused for subsequent requests to the portal.
- I learned that session cookies are scoped according to their domain and path attributes, along with other cookie rules, rather than simply being shared with every URL.
- I also learned that having a cookie does not necessarily guarantee that the session is still valid. The server can reject an expired or unauthorized session.
- This concept will be useful in future projects involving authenticated APIs, external services, and backend integrations.

## 3. HTTP Request Timeouts

- I learned why setting a timeout is important when making HTTP requests to an upstream server.
- A timeout prevents a request from waiting indefinitely for the server to respond. In the `requests` library, timeout values are specified in seconds.
- In this project, I used timeouts for login and data-retrieval requests to prevent the application from waiting indefinitely for the legacy portal.
- I also learned that a timeout is not necessarily a total execution-time limit for the entire operation; connection and read timeouts have their own behavior.
- I will use appropriate timeouts in future API integrations to make applications more predictable and resilient.

## 4. Reverse-Engineering a Legacy API

- One of the main challenges was understanding how the existing Flock Energy portal communicated with its backend.
- Although I had previously consumed APIs, discovering undocumented endpoints and understanding their request and response formats was new to me.
- I used the browser's Developer Tools and Network tab to inspect requests made when navigating the portal.
- I discovered endpoints for meter listing, meter details, energy readings, and geographic coordinates.
- I learned how query parameters such as `q` and `page` were used for meter searching and pagination.
- I also learned that browser-visible data does not always come from a single endpoint. Different sections of a page can obtain their data through separate background requests.
- This experience taught me to investigate actual network traffic instead of guessing endpoint paths or response structures.
- I can apply this approach when integrating with existing services whose documentation is incomplete, provided that inspecting and using those endpoints is authorized.

## 5. Authentication and Session Cookies

- Authentication was one of the more challenging parts of this project because the portal's login behavior was different from what I initially expected.
- I initially sent the login form using a `username` field. By inspecting the actual response, I discovered that the portal expected an `email` field along with the password.
- I learned that an HTTP response status of `200 OK` does not necessarily mean that the application-level operation succeeded.
- In this portal, a successful login returned a JSON object containing a redirect instruction, while an unsuccessful login could return a JSON failure object with an embedded `401` status.
- I also discovered the correct session cookie name, `__Secure-better-auth.session_token`, and used it when checking whether the login established the expected session.
- Another important discovery was that the meter-details endpoint used `__data.json`, with two leading underscores, rather than `_data.json`. The incorrect path returned `404 Not Found`.
- These issues taught me to inspect response bodies, cookies, request headers, and exact URLs before changing code.
- I also learned that credentials and session-cookie values must remain confidential and should never be printed in application logs or committed to a repository.

## 6. FastAPI and REST API Design

- I used FastAPI to build a REST API adapter around the existing portal instead of exposing the legacy endpoints directly to API consumers.
- I learned how to create API routes using `APIRouter` and register them with the main FastAPI application.
- I implemented endpoints for listing meters, retrieving individual meter details, retrieving energy readings, and retrieving geographic coordinates.
- I also learned how query parameters, path parameters, and response models help define a consistent API contract.
- I used HTTP status codes to distinguish different types of errors, including invalid input, invalid pagination, and failures when communicating with the upstream portal.
- This project helped me understand how FastAPI can serve as an integration layer between an existing service and other applications.
- I intend to reuse this architecture in future backend and AI-related projects where I need to connect multiple services through a consistent API.

## 7. Pydantic Schemas and Data Validation

- I learned how Pydantic models can define the expected structure and data types of API responses.
- In this project, I created schemas for meter details, energy readings, and geographic coordinates.
- The legacy portal returned some numeric values as strings. For example, energy readings and geographic coordinates were represented as strings even though their values were numeric.
- I learned how to convert these values to appropriate numeric types before returning them through my API.
- I also used response models in FastAPI to describe and validate the structure of the responses.
- This helped me understand the difference between receiving raw external data and defining a predictable contract for API consumers.
- I can apply this knowledge when developing APIs that consume external services, validate incoming data, or communicate with AI models and other backend components.

## 8. Data Normalization

- One of the important concepts I learned was data normalization at the application level.
- The legacy portal used field names such as `MeterId`, `SerialNo`, and `PhaseType`, whereas my API uses consistent names such as `meter_id`, `serial_number`, and `phase_type`.
- I created functions in `app/schemas/normalizers.py` to extract the required fields, convert values where appropriate, and prepare normalized responses.
- I learned that normalization is especially important when integrating with an existing system whose response format was not designed around my API contract.
- The meter-details response was particularly challenging because the SvelteKit page-data response contained a `nodes` array, nested data, and a JSON-encoded string containing meter metadata.
- I initially encountered a `404` because I used the wrong endpoint path, followed by a normalization error because I was reading the response at the wrong level.
- By inspecting the actual response and updating the normalizer, I was able to extract the meter metadata and hierarchy correctly.
- This taught me to base parsing logic on observed response structures rather than assumptions.
- I also learned that framework-generated response structures can change, so the normalizer should detect unexpected structures instead of silently producing incorrect data.

## 9. Project Architecture and Separation of Responsibilities

- I learned the importance of separating responsibilities instead of putting all the logic into one file.
- In this project, `app/clients/legacy_client.py` handles communication with the legacy portal, including authentication and HTTP requests.
- `app/api/meters.py` defines the public API endpoints and connects the client to the normalizers.
- `app/schemas/meters.py` defines the Pydantic models used for the API response contracts.
- `app/schemas/normalizers.py` transforms the legacy portal's responses into the format expected by my API.
- `app/config.py` manages application configuration.
- I also learned that a file such as `app/models.py` is not automatically needed just because it exists. Its purpose depends on the application's requirements and whether it contains models that are actually used.
- This structure made the application easier to understand, test, and maintain.
- I will try to follow the same separation of responsibilities in future projects, adapting the architecture to the size and requirements of each application.

## 10. Automated Testing and Mocking

- Testing was another area where I gained practical experience.
- I used Pytest to run automated tests for the legacy client, normalizers, and API endpoints.
- I learned how to use mocks to simulate upstream responses without repeatedly calling the live portal.
- This allowed me to test successful responses, invalid input, normalization behavior, and upstream failures independently of the external service.
- I also learned that tests must reflect the actual implementation. For example, when I added a preliminary GET request to the login flow, the tests needed to mock both the GET and POST requests.
- I used test failures to identify mismatches between my assumptions and the actual behavior of the code.
- In addition to mocked tests, I tested the endpoints against the live portal. This exposed problems that mocked tests alone could not reveal, such as the incorrect login field name, the session-cookie mismatch, and the wrong meter-details endpoint path.
- This experience taught me that automated tests and live integration tests serve different purposes and complement each other.
- I intend to continue writing tests for future projects rather than relying only on manual testing.

## 11. Error Handling and Debugging

- I learned how exceptions raised by the HTTP client can be handled at the API layer and translated into appropriate HTTP responses.
- In this project, I encountered errors such as `401 Unauthorized`, `403 Forbidden`, and `404 Not Found` while investigating authentication and endpoint behavior.
- I also encountered application-level failures where the HTTP status was successful but the JSON response indicated that the login had failed.
- Initially, the API returned a generic error message that did not reveal the underlying problem. Temporary diagnostic output helped me identify the actual exception.
- I learned to use diagnostic information during development while avoiding the exposure of passwords, cookie values, and other secrets.
- I also learned that a successful test suite does not guarantee that an external integration works correctly. Mocked responses can validate my code's behavior, but live requests are necessary to verify compatibility with the actual service.
- This experience improved my debugging approach because I learned to investigate the source of an error before changing the implementation.

## 12. OpenAPI and API Documentation

- I learned that FastAPI can automatically generate an OpenAPI specification from registered routes, parameters, and response models.
- I used the interactive Swagger UI at `/docs` to test the endpoints and inspect their responses.
- I also exported the OpenAPI specification to `openapi.json` so the API contract could be included with the project.
- I learned that the generated specification must be updated after changing routes or response schemas; otherwise, the exported file may not represent the latest implementation.
- I also worked on `README.md` and `PROTOCOL.md` to document setup instructions, endpoint behavior, authentication, and the observed upstream response formats.
- This helped me understand that documentation is part of delivering a usable API, not just an additional task at the end.

## 13. Using AI During Development

- This project was a valuable learning experience for me, even though I used AI for several parts of the implementation, especially when working with unfamiliar topics.
- I used AI for guidance, code generation, explanations, and debugging. However, I also ran tests, inspected browser requests, tested the live endpoints, and used the actual responses to identify problems.
- Some topics were completely new to me, and I needed help understanding how the different components worked together.
- I found the experience exciting because I was not only implementing an assignment but also learning concepts that I had not previously used in a project.
- I learned that AI can be useful for exploring unfamiliar technologies, understanding errors, and accelerating development, but its suggestions still need to be checked against the actual behavior of the application.
- I do not consider using AI to mean that there is nothing left to learn. Instead, this project showed me which concepts I need to understand more deeply and gave me practical examples to revisit.
- I want to become more independent in applying these concepts, identifying problems, evaluating suggested solutions, and explaining the decisions behind my code.

## 14. How I Will Apply These Learnings in Future Projects

- I want to reuse environment-based configuration and secret management in future backend applications.
- I will use HTTP sessions appropriately when an integration requires cookies or other persistent request state.
- I will pay more attention to timeouts, error handling, and authentication failures when calling external services.
- I will inspect actual requests and responses before implementing integrations with undocumented or unfamiliar APIs.
- I will use Pydantic models and normalization functions to maintain consistent API contracts when working with external data.
- I will continue writing automated tests with mocks and validating integrations against live services when appropriate.
- I want to apply these concepts in future FastAPI, AI backend, and service-integration projects.
- Many of the topics I learned in this project were new to me, but I believe each will be useful in some way in my future work.
- Overall, this project gave me practical exposure to several backend development concepts and the confidence to explore unfamiliar technologies. Even when I needed AI assistance, I was motivated by the process of investigating problems, implementing solutions, and seeing the application work.
- I would like to apply and strengthen these learnings in future projects so that I can become more confident, capable, and independent as a developer.
