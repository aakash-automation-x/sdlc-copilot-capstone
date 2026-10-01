# Implementation Plan

## Overview

This implementation plan breaks down the vehicle retrieval feature (FR-001, AC-001, AC-002) from the approved architecture into a prioritized, dependency-ordered task list. The feature requires a three-layer FastAPI endpoint (Router ? Service ? Data) to retrieve vehicle details by integer ID with proper HTTP status handling (200 for success, 404 for not found).

**Scope:** FR-001 (System shall retrieve vehicle details by ID) with AC-001 (HTTP 200 + all 6 attributes) and AC-002 (HTTP 404 + error message).

**Delivery Phases:**
- **Phase 1 (Layers):** TASK-001 through TASK-004 — Build core data, service, and router components (interdependent; implement sequentially)
- **Phase 2 (Polish):** TASK-005, TASK-006, TASK-009 — Add validation, dependency updates, and logging (parallel after Phase 1)
- **Phase 3 (Verify):** TASK-007, TASK-008, TASK-010 — Write comprehensive tests and documentation (parallel after Phase 1)

**Parallelization:** Phase 2 and Phase 3 tasks can develop in parallel once Phase 1 is complete. Recommendations: Start Phase 2 while Phase 1 is in test integration, run Phase 3 parallel with Phase 2 review cycles.

## Source References
- **Architecture:** rtifacts/architecture.md (Router ? Service ? Data three-layer design)
- **Requirements:** rtifacts/requirements.md (FR-001, AC-001, AC-002)
- **Design Review:** rtifacts/design-review.md (DR-001, DR-003 resolved; DR-004, DR-005, DR-009 actionable)

## Assumptions and Constraints
- Vehicle IDs are integers (confirmed in DR-003; router and data layer enforce int type)
- Data file location: data/vehicles.json (created and populated in Step 3)
- Current codebase organization preserved: Router in pp/main.py, Service in pp/api/api.py, Models in pp/db/models.py
- No database migrations or schema changes required (JSON file-based persistence)
- FastAPI >= 0.100.0 and Pydantic >= 2.0 assumed based on DR-009 findings

## Task List

### TASK-001: Update Vehicle Pydantic Model

- **Priority:** High
- **FR/NFR:** FR-001 (all attributes required by AC-001)
- **Architecture section:** "Key Components and Responsibilities" ? Vehicle Model
- **Depends on:** None
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Ensure the Vehicle Pydantic model in pp/db/models.py includes all six required attributes: id (int), make (str), model (str), year (int), price (float), transmission (str), fuel_type (str). Add type hints, field validation (e.g., positive integers for year/price), and docstrings.
- **Expected output:** Updated pp/db/models.py with complete Vehicle model class and field validators
- **Validation:** Inspect model definition; verify all six fields present with correct types; run simple instantiation test

---

### TASK-002: Implement Data Layer (fetch_vehicle Function)

- **Priority:** High
- **FR/NFR:** FR-001, AC-001, AC-002 (core retrieval logic)
- **Architecture section:** "Data Layer (JSON File I/O)" ? Component diagram and responsibilities
- **Depends on:** TASK-001 (Vehicle model must exist)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Implement etch_vehicle(vehicle_id: int) -> Vehicle | None in pp/db/models.py or separate pp/db/data.py. Function loads data/vehicles.json, searches by integer vehicle_id, and returns a Vehicle instance or None. Error handling: catch JSON parse errors, log them, and raise exception (do not silently fail).
- **Expected output:** Data layer function in pp/db/models.py or pp/db/data.py; handles file I/O and search logic
- **Validation:** Unit test: load vehicles.json, call fetch_vehicle(1), verify Vehicle object returned; call fetch_vehicle(999), verify None returned

---

### TASK-003: Implement Service Layer (get_vehicle Function)

- **Priority:** High
- **FR/NFR:** FR-001, AC-002 (HTTP 404 error handling)
- **Architecture section:** "Service Layer (Business Logic)" ? Component diagram and responsibilities
- **Depends on:** TASK-002 (data layer must exist)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Implement get_vehicle(vehicle_id: int) -> Vehicle in pp/api/api.py. Function calls data layer's fetch_vehicle(vehicle_id), converts None ? HTTPException(status_code=404, detail="Vehicle not found"), and returns Vehicle instance on success. Use FastAPI's exception handling.
- **Expected output:** Service function in pp/api/api.py with 404 error conversion
- **Validation:** Unit test: call get_vehicle(1), verify Vehicle returned; call get_vehicle(999), verify HTTPException(404) raised

---

### TASK-004: Implement Router Layer (GET /vehicles/{vehicle_id} Endpoint)

- **Priority:** High
- **FR/NFR:** FR-001, AC-001 (HTTP 200 success), AC-002 (HTTP 404 error)
- **Architecture section:** "Router Layer (FastAPI)" ? Component diagram and responsibilities; addresses DR-004 finding (endpoint does NOT exist yet)
- **Depends on:** TASK-003 (service layer must exist)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Implement @app.get("/vehicles/{vehicle_id}") endpoint in pp/main.py. Endpoint accepts integer path parameter, calls service.get_vehicle(vehicle_id), and returns fastapi.Response with 200 or 404 status. FastAPI automatically serializes Vehicle model to JSON and converts HTTPException to response.
- **Expected output:** Router endpoint in pp/main.py with proper path parameter type
- **Validation:** Integration test: GET /vehicles/1 ? 200 + vehicle JSON; GET /vehicles/999 ? 404 + error message

---

### TASK-005: Add Input Validation (Path Parameter)

- **Priority:** Medium
- **FR/NFR:** N/A (addresses DR-005 finding: input validation)
- **Architecture section:** "Router Layer (FastAPI)" ? validation responsibility
- **Depends on:** TASK-004 (endpoint must exist)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Enhance the /vehicles/{vehicle_id} endpoint with explicit FastAPI Path(...) validation to ensure vehicle_id is a positive integer (gt=0). Add FastAPI Path constraints: rom fastapi import Path; vehicle_id: int = Path(..., gt=0). Update endpoint docstring with validation rules.
- **Expected output:** Updated endpoint in pp/main.py with Path validation
- **Validation:** Integration test: GET /vehicles/0 ? 422 (validation error); GET /vehicles/-1 ? 422; GET /vehicles/abc ? 422; GET /vehicles/1 ? 200/404

---

### TASK-006: Update Dependencies (requirements.txt)

- **Priority:** Medium
- **FR/NFR:** N/A (addresses DR-009 finding: dependency versions)
- **Architecture section:** "Technology Choices" (implicit)
- **Depends on:** None
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Ensure equirements.txt specifies minimum versions: FastAPI >= 0.100.0, uvicorn >= 0.20.0, pydantic >= 2.0. Verify existing code (Pydantic models, FastAPI decorators) is compatible with these versions. Test with pip install -r requirements.txt and pytest test/test.py to confirm no regressions.
- **Expected output:** Updated equirements.txt with version constraints; validation report
- **Validation:** Run pip install -r requirements.txt; run pytest test/test.py; verify no deprecation warnings

---

### TASK-007: Add Structured Logging and Error Handling

- **Priority:** Medium
- **FR/NFR:** N/A (addresses non-functional logging strategy)
- **Architecture section:** "Error handling" goal
- **Depends on:** TASK-002, TASK-003 (logic layers must exist)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Add structured logging to data and service layers. Log vehicle retrieval attempts (vehicle_id, timestamp), cache hits/misses, JSON parse errors, and 404 responses. Use Python logging module with level INFO for requests, ERROR for exceptions. Log to stdout (uvicorn captures). Do NOT log sensitive data (e.g., request IP).
- **Expected output:** Logging added to pp/api/api.py and pp/db/models.py or pp/db/data.py
- **Validation:** Run endpoint; inspect logs for retrieval and error messages; verify no secrets logged

---

### TASK-008: Create Unit Tests for Service & Data Layers

- **Priority:** High
- **FR/NFR:** FR-001, AC-001, AC-002 (functionality testing)
- **Architecture section:** "Testability" architectural goal
- **Depends on:** TASK-002, TASK-003 (functions must exist)
- **Blocked by:** None
- **Target agent:** Verify Agent
- **Description:** Write pytest tests in 	est/test.py or new 	est/test_service.py:
  - 	est_fetch_vehicle_success(): Verify fetch_vehicle(1) returns Vehicle with correct attributes
  - 	est_fetch_vehicle_not_found(): Verify fetch_vehicle(999) returns None
  - 	est_get_vehicle_success(): Verify get_vehicle(1) returns Vehicle
  - 	est_get_vehicle_not_found(): Verify get_vehicle(999) raises HTTPException(404)
  
  Test data: Use actual data/vehicles.json or mock fixture with sample vehicle records.
- **Expected output:** Test file with 4+ passing tests covering data and service layers
- **Validation:** Run pytest test/test.py -v; achieve 100% pass rate for these tests

---

### TASK-009: Create Integration Tests for Endpoint

- **Priority:** High
- **FR/NFR:** FR-001, AC-001, AC-002 (complete AC coverage)
- **Architecture section:** "Data Flow" (success and error cases)
- **Depends on:** TASK-004, TASK-005 (endpoint and validation must exist)
- **Blocked by:** None
- **Target agent:** Verify Agent
- **Description:** Write pytest tests with TestClient for FastAPI in 	est/test.py:
  - 	est_get_vehicle_endpoint_success(): GET /vehicles/1 ? 200, verify response includes all 6 attributes (id, make, model, year, price, transmission, fuel_type)
  - 	est_get_vehicle_endpoint_not_found(): GET /vehicles/999 ? 404, verify error message present
  - 	est_get_vehicle_endpoint_invalid_id(): GET /vehicles/abc ? 422; GET /vehicles/0 ? 422; GET /vehicles/-1 ? 422
  
  Trace each test to AC-001 and AC-002.
- **Expected output:** Integration tests in 	est/test.py with TestClient; all passing
- **Validation:** Run pytest test/test.py -v; confirm all tests pass; verify response JSON structure against AC-001 requirements

---

### TASK-010: Documentation & Verification

- **Priority:** Medium
- **FR/NFR:** N/A (traceability and maintainability)
- **Architecture section:** "Traceability" goal
- **Depends on:** TASK-004, TASK-008, TASK-009 (implementation and tests must be complete)
- **Blocked by:** None
- **Target agent:** Verify Agent
- **Description:** Add API endpoint documentation to pp/main.py (docstring for endpoint), update README.md with endpoint details (path, method, parameters, response schema, status codes, examples). Add inline code comments explaining the three-layer flow in each file (app/main.py, app/api/api.py, app/db/models.py). Verify traceability: FR-001 ? {AC-001, AC-002} ? {TASK-001 through TASK-009} ? source code. Create a brief traceability summary in artifact or code comment.
- **Expected output:** Updated README.md, endpoint docstring, code comments, traceability summary
- **Validation:** Verify README documents endpoint syntax, response schema, and status codes; confirm docstring and code comments are clear; run semantic grep to confirm all FRs and ACs mentioned in code

---

## Parallelization Opportunities

**After Phase 1 is complete (TASK-001–TASK-004):**

1. **TASK-005, TASK-006, TASK-009 can run in parallel:** Input validation, dependency updates, and logging are independent implementation concerns.
2. **TASK-007, TASK-008 can run in parallel:** Unit and integration tests can be written concurrently; both depend on Phase 1 but not on each other.
3. **Phase 2 and Phase 3 can run in parallel:** All Phase 2 (polish) and Phase 3 (verify) tasks can start once Phase 1 layer components are reviewed and approved by the Implementation Agent.

**Critical path:** TASK-001 ? TASK-002 ? TASK-003 ? TASK-004 ? parallel {Phase 2, Phase 3} ? TASK-010 (final documentation).

## Blocked Tasks

| Task | Blocked by | Unblock Criteria |
|---|---|---|
| None | None | All tasks have upstream dependencies satisfied or are independent. No external blockers identified. |

All dependencies are within the team's control (implemented in prior tasks). No Jira tickets, stakeholder approvals, or external integrations are required.

## Risks and Open Questions

1. **Risk: JSON file read performance at scale** — Current implementation loads entire data/vehicles.json on every request. For production > 10K vehicles, consider caching or pagination. **Mitigation:** Document as FR-002 future enhancement; implement caching in Phase 2 if performance tests show latency.
2. **Risk: Integer vehicle ID uniqueness** — Assuming data/vehicles.json has unique integer IDs. **Mitigation:** Add validation in data layer (log warning if duplicate IDs found); document assumption in README.
3. **Question: Error response format** — AC-002 specifies "error message"; confirm JSON structure (e.g., {"detail": "Vehicle not found"}). **Answer:** Use FastAPI default HTTPException serialization (detail field).
4. **Question: Attribute order in response JSON** — AC-001 specifies "all 6 attributes"; no order requirement. **Answer:** Pydantic model serialization determines order (respect Pydantic default or specify via model_config).

## Recommended First Task for Implementation Agent

**TASK-001 – Update Vehicle Pydantic Model**

This task is the foundation for all downstream work. With the Vehicle model complete, TASK-002 (data layer), TASK-003 (service layer), and TASK-004 (router) can proceed without further rework. It has no dependencies, is low-risk, and will be verified immediately by import tests in subsequent tasks.
