# Architecture � Vehicle Retrieval Endpoint (FR-001)

## Overview

The Car Portal architecture for vehicle retrieval follows a **three-layer** design: **Router ? Service ? Data**. 
HTTP requests arrive at a FastAPI endpoint (GET /vehicles/{vehicle_id}), pass through business logic in a service layer, 
and are resolved by querying vehicle data from JSON files. Non-existent vehicles return HTTP 404 with an error message; 
existing vehicles return HTTP 200 with all attributes (make, model, year, price, transmission, fuel_type).

## Architectural Goals and Drivers

| Goal | Driver |
|---|---|
| **Single responsibility** | Separate routing, business logic, and data I/O into distinct layers |
| **Testability** | Each layer can be tested independently |
| **Maintainability** | Clear data flow from HTTP to JSON persistence |
| **Error handling** | Explicit 404 responses for missing vehicles (AC-002) |
| **Traceability** | Every component traces to FR-001 or one of its acceptance criteria |

**Functional Requirements Addressed:**
- FR-001: System shall retrieve vehicle details by ID from the database
  - AC-001: Retrieve existing vehicle ? HTTP 200 with all attributes
  - AC-002: Retrieve non-existent vehicle ? HTTP 404 with error message

## Recommended Architecture

The system implements a **layered architecture** with three well-defined responsibilities:

1. **Router Layer (FastAPI):** Exposes the HTTP endpoint, validates input, and delegates to the Service layer.
2. **Service Layer (Business Logic):** Implements the retrieval logic, delegates to the Data layer, and constructs HTTP responses.
3. **Data Layer (JSON I/O):** Reads vehicle records from JSON files and returns structured data or signals missing records.

This structure preserves the current codebase organization (routes in \pp/main.py\, logic in \pp/api/api.py\, models in \pp/db/models.py\) while formalizing responsibilities.

## Component Diagram

\\\
+-----------------------------------------------------------------+
�                     FastAPI Application                         �
+-----------------------------------------------------------------+
                              �
                              � HTTP GET /vehicles/{vehicle_id}
                              ?
+-----------------------------------------------------------------+
�                   Router Layer (Endpoint)                        �
�  +----------------------------------------------------------+   �
�  � @app.get("/vehicles/{vehicle_id}")                       �   �
�  �  � Validate vehicle_id path parameter                    �   �
�  �  � Call service.get_vehicle(vehicle_id)                  �   �
�  �  � Return 200/404 response                               �   �
�  +----------------------------------------------------------+   �
�                   File: app/main.py                             �
+-----------------------------------------------------------------+
                              �
                              � Call service.get_vehicle(vehicle_id)
                              ?
+-----------------------------------------------------------------+
�              Service Layer (Business Logic)                      �
�  +----------------------------------------------------------+   �
�  � def get_vehicle(vehicle_id):                             �   �
�  �  � Call data_layer.fetch_vehicle(vehicle_id)             �   �
�  �  � Handle None ? raise 404 error                         �   �
�  �  � Return Vehicle model instance                         �   �
�  +----------------------------------------------------------+   �
�                   File: app/api/api.py                          �
+-----------------------------------------------------------------+
                              �
                              � Call data_layer.fetch_vehicle(vehicle_id)
                              ?
+-----------------------------------------------------------------+
�               Data Layer (JSON File I/O)                         �
�  +----------------------------------------------------------+   �
�  � def fetch_vehicle(vehicle_id):                           �   �
�  �  � Load data/vehicles.json                               �   �
�  �  � Search for record by vehicle_id                       �   �
�  �  � Return Vehicle | None                                 �   �
�  +----------------------------------------------------------+   �
�                   File: app/db/models.py + data/vehicles.json   �
+-----------------------------------------------------------------+
\\\

## Key Components and Responsibilities

| Component | Responsibility | Input | Output | Traces To |
|---|---|---|---|---|
| **Router (Endpoint)** | Accept HTTP GET request, validate path param as integer, delegate to service | `vehicle_id: int` (path param) | HTTP Response (200/404) | FR-001, AC-001, AC-002 |
| **Service (Business Logic)** | Retrieve vehicle by ID, handle not-found, return model | `vehicle_id: int` | `Vehicle` model or HTTPException(404) | FR-001 |
| **Data Layer (JSON I/O)** | Load data/vehicles.json, search by integer ID, return structured data | `vehicle_id: int` | `Vehicle dict` or `None` | AC-001, AC-002 |
| **Vehicle Model** | Define schema for vehicle attributes (make, model, year, price, transmission, fuel_type) | N/A | Pydantic model with all 6 required attributes | AC-001 |

## Data Flow

### Success Case (AC-001)

\\\
+----------+
�  Client  �
+----------+
     � GET /vehicles/v123
     ?
+----------------------------------------------+
� Router: Validate vehicle_id = "v123"         �
+----------------------------------------------+
     � Call service.get_vehicle("v123")
     ?
+----------------------------------------------+
� Service: Delegate to data layer              �
+----------------------------------------------+
     � Call data_layer.fetch_vehicle("v123")
     ?
+----------------------------------------------+
� Data Layer: Load vehicles.json               �
� Search: vehicles[].id == "v123" ? FOUND     �
� Return: {"id": "v123", "make": "Toyota", ..}�
+----------------------------------------------+
     � Construct Vehicle model
     ?
+----------------------------------------------+
� Service: Return Vehicle instance             �
+----------------------------------------------+
     � Serialize to JSON response
     ?
+----------------------------------------------+
� Router: HTTP 200 OK                          �
� {"id": "v123", "make": "Toyota",             �
�  "model": "Camry", "year": 2023, ...}        �
+----------------------------------------------+
     � Send to client
     ?
+----------+
�  Client  �
+----------+
\\\

### Error Case (AC-002)

\\\
+----------+
�  Client  �
+----------+
     � GET /vehicles/v999 (does not exist)
     ?
+----------------------------------------------+
� Router: Validate vehicle_id = "v999"         �
+----------------------------------------------+
     � Call service.get_vehicle("v999")
     ?
+----------------------------------------------+
� Service: Delegate to data layer              �
+----------------------------------------------+
     � Call data_layer.fetch_vehicle("v999")
     ?
+----------------------------------------------+
� Data Layer: Load vehicles.json               �
� Search: vehicles[].id == "v999" ? NOT FOUND  �
� Return: None                                 �
+----------------------------------------------+
     � Catch None, raise HTTPException(404)
     ?
+----------------------------------------------+
� Service: Propagate exception                 �
+----------------------------------------------+
     � Exception caught by FastAPI
     ?
+----------------------------------------------+
� Router: HTTP 404 Not Found                   �
� {"detail": "Vehicle not found"}              �
+----------------------------------------------+
     � Send to client
     ?
+----------+
�  Client  �
+----------+
\\\

## Technology Choices

| Decision | Choice | Rationale | Trade-offs |
|---|---|---|---|
| **Framework** | FastAPI | Type-safe, async-ready, built-in request validation, automatic OpenAPI docs | Requires Python 3.7+ |
| **Persistence** | JSON files (data/vehicles.json) | Aligns with current implementation; no DB server overhead; file-based, easily version-controlled | Not suitable for >10K records or concurrent writes; no transactions; requires in-memory search |
| **Data Models** | Pydantic | Runtime validation, type hints, JSON serialization/deserialization; tight FastAPI integration | Extra dependency; slight runtime overhead |
| **Error Handling** | HTTPException with 404 status | Standard HTTP semantics; FastAPI's exception handlers automatically convert to JSON responses | Limited error detail; client must parse HTTP status code |
| **Deployment** | uvicorn (ASGI server) | Lightweight, standard for FastAPI; supports async handlers | Single-process by default; requires reverse proxy for production scale |

## SDLC Pipeline Components

| Type | Name | Purpose |
|---|---|---|
| **Agent** | Requirements Agent (Step 1) | Extracted and approved FR-001 and acceptance criteria |
| **Agent** | Architect Agent (Step 2) | Design this three-layer architecture (current step) |
| **Agent** | Design Review Agent (Step 3) | Review architecture decisions before implementation begins |
| **Agent** | Planner Agent (Step 4) | Break architecture into implementation tasks (TASK-###) |
| **Agent** | Implementation Agent (Step 5) | Code router, service, data layers + tests |
| **Agent** | Review Agent (Step 6) | Peer code review against this architecture |
| **Agent** | Verify Agent (Step 7) | Run pytest, validate traceability to FR-001 |
| **Agent** | PR Agent (Step 8) | Create pull request with CHANGELOG entry |
| **Skill** | design-architecture | Produced this document |
| **Skill** | sdlc-traceability | Maintains FR-001 ? architecture ? implementation mapping |
| **Skill** | implement-task | Guides implementation of TASK-### from impl-plan.md |
| **Instruction** | code-quality.instructions.md | Enforces secure, DRY code in all Python files |
| **Instruction** | fastapi-backend.instructions.md | Routes, business logic, JSON I/O boundaries |
| **Instruction** | tests.instructions.md | Test structure for endpoint, service, data layers |

## Security Considerations

### Input Validation
- **vehicle_id path parameter:** FastAPI validates as a string; no special characters or SQL injection risk (JSON file, not a database).
- **Pydantic models:** Automatically validate incoming/outgoing data types and constraints.

### Error Handling
- **Explicit 404 responses:** Return structured error messages without leaking internal paths or implementation details.
- **No sensitive data in logs:** Do not log full vehicle records or stack traces to stdout.

### OWASP Top 10 Mitigations
- **A01:2021 � Broken Access Control:** No authentication/authorization required for this release (out of scope). Future versions should add API key or JWT validation.
- **A03:2021 � Injection:** JSON file format and Pydantic validation prevent injection attacks.
- **A04:2021 � Insecure Design:** Data layer is isolated; no direct JSON file writes from untrusted input.
- **A09:2021 � Using Components with Known Vulnerabilities:** Dependency versions pinned in \
equirements.txt\; security updates checked via \pip audit\.

## Reliability and Observability

### Failure Handling
- **Missing vehicles (AC-002):** Service layer catches None from data layer and raises \HTTPException(status_code=404)\. FastAPI's exception handler returns JSON to client.
- **Malformed JSON:** Data layer should log and raise exception; Router returns 500 on unrecoverable JSON parse errors.
- **File system errors:** If \data/vehicles.json\ is missing or unreadable, data layer raises exception (propagated as 500 to client).

### Logging
- **Service layer logs:** Record retrieval attempts (vehicle_id), cache hits/misses (if caching is added), and errors.
- **Data layer logs:** Record file reads, JSON parse errors, record count.
- **Router logs:** Structured logging of request/response (method, path, status, latency).

### Monitoring
- **Metrics to track (future):** Request latency, error rate (4xx/5xx), cache hit ratio, file I/O latency.
- **Alerting (future):** Alert if error rate exceeds 5%, if p99 latency exceeds 500ms, if data/vehicles.json is unreadable.

## Scalability and Performance

### Bottlenecks
- **Linear search:** Data layer iterates through all vehicles to find match. **Acceptable for <5K records.**
- **File I/O:** Every request reads \data/vehicles.json\ from disk. **Acceptable for <100 req/sec.**
- **JSON parsing:** Pydantic parses entire file structure. **Acceptable for current scope.**

### Scaling Strategy (Future)
1. **Caching:** In-memory vehicle index (dict keyed by vehicle_id) refreshed on startup or on file change.
2. **Database:** Migrate to PostgreSQL with indexed queries when records exceed 10K.
3. **Async file I/O:** Use \iofiles\ to avoid blocking the event loop during file reads (future optimization).

### Performance Targets (Current)
- **Success response:** <100ms (disk read + JSON parse + model instantiation)
- **404 response:** <100ms (disk read + JSON parse + linear search + error construction)

## Deployment

### Build and Package
- **Environment:** Python 3.9+
- **Dependencies:** \pip install -r requirements.txt\
- **Entry point:** \uvicorn app.main:app --reload\ (development) or \uvicorn app.main:app --host 0.0.0.0 --port 8000\ (production-like)

### CI/CD
- **Test:** \pytest test/test.py\ validates endpoint behavior, service logic, error responses.
- **Lint:** \lake8\ and \lack\ enforce code quality.
- **Type check:** \mypy\ validates type hints.
- **Security:** \andit\ checks for OWASP violations; \pip audit\ checks dependencies.

### Versioning
- Data/vehicles.json tracked in Git; changes reviewed in PRs.
- No migrations needed (JSON-based).
- Schema changes coordinated with Pydantic model updates.

## Assumptions and Constraints

- **Assumption:** `data/vehicles.json` exists and is readable at startup. ✅ **RESOLVED:** File migrated from cars.json with complete schema.
- **Assumption:** Vehicle records have a stable unique identifier (`id` field). ✅ **RESOLVED:** Integer IDs (1–10) confirmed.
- **Assumption:** The `vehicle_id` path parameter is an integer. ✅ **RESOLVED:** Path parameter type is `int`.
- **Constraint:** JSON file persistence limits concurrency; no simultaneous writes supported.
- **Constraint:** No authentication/authorization for vehicle retrieval (this release).
- **Constraint:** No pagination or filtering; must retrieve complete vehicle record by exact ID match.
- **Constraint:** No external API integrations; all data sourced from local JSON file.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **File corruption (vehicles.json)** | Low | High (all endpoints fail) | Version control + backup; validate JSON structure on load; add file integrity check (checksum) |
| **Concurrent write corruption** | Low | High (data loss) | Document single-writer constraint; add write lock (future: DB transaction) |
| **Large file performance degradation** | Medium | Medium (slow responses) | Monitor file size; implement caching or migrate to DB at >10K records |
| **Path traversal attack (vehicle_id)** | Very Low | Medium (depends on file structure) | FastAPI validates path param as string; no \../\ or special chars interpreted as file paths |
| **Malformed JSON in vehicles.json** | Low | High (500 errors on every request) | Pre-validate JSON structure; add test that loads vehicles.json on startup |

## Resolved Design Decisions (Design Review Approval - 2026-10-01)

✅ **DR-001 Resolved:** Data file location confirmed as `data/vehicles.json` with complete schema (id: int, make, model, year, price, transmission, fuel_type). All 10 vehicle records migrated from cars.json.

✅ **DR-003 Resolved:** Vehicle ID type confirmed as `int`. Router layer accepts integer path parameters; Service layer compares integer IDs; Data layer searches vehicles.json by integer ID.

✅ **Three-layer architecture approved:** Router → Service → Data separation of concerns validated and ready for implementation.

## Open Questions (Deferred to Future Releases)

1. **Caching strategy:** Should we cache vehicle records in-memory to reduce file I/O? If yes, cache invalidation strategy?
2. **Concurrent write safety:** How to enforce single-writer constraint on data/vehicles.json?
3. **Future authentication:** Router middleware or Service layer when authentication is added?
4. **Error response format:** Include extended error details in 404 responses?
5. **Observability baseline:** Logging level and format (JSON, plain text) expected?

---

## Traceability Matrix

| Artifact | Link | Notes |
|---|---|---|
| Functional Requirements | artifacts/requirements.md (FR-001, AC-001, AC-002) | Architecture designed to satisfy all acceptance criteria |
| User Story | userstory.md | "As a car shopper, I want to retrieve vehicle details by ID" |
| Implementation Plan | (pending) artifacts/impl-plan.md | Planner Agent will decompose this architecture into TASK-### items |
| Design Review | (pending) artifacts/design-review.md | Design Review Agent will validate component boundaries and error handling |
| Code | app/main.py, app/api/api.py, app/db/models.py | Implementation follows this three-layer structure |
| Tests | test/test.py | Tests validate AC-001 and AC-002 against this design |
| CHANGELOG | (pending) artifacts/CHANGELOG.md | PR will reference FR-001 and this architecture design |

---

**Document Version:** 1.0  
**Status:** ✅ Approved by Design Review Agent (Step 3) — Ready for Implementation Planning (Step 4)  
**Generated:** 2026-10-01  
**Architecture Type:** Layered (Router → Service → Data)
