# Implementation Plan — Car Portal: Get Vehicle Details

**Prepared by:** Planner Agent (Step 4 of 8)
**Date:** 2026-09-24
**Status:** Ready for Implementation

---

## Overview

This plan breaks the approved architecture into a nine-task, dependency-ordered implementation list for the Implementation Agent. The feature under delivery is a single REST endpoint:

```
GET /vehicles/{vehicle_id}  →  200 VehicleResponse | 404 {"detail": "Vehicle not found"}
```

The three-layer FastAPI architecture (Router → Service → Data) is already correctly structured in the working tree. Four targeted changes are required; the remainder of the tasks are verification passes to confirm the existing code matches the approved design before the test suite runs.

---

## Source Artifact References

| Artifact | Path | Key Content |
|---|---|---|
| Requirements | `artifacts/requirements.md` | FR-001, AC-001, AC-002, AC-003 |
| Architecture | `artifacts/architecture.md` | Three-layer design, DD-001 through DD-005 |
| Design Review | `artifacts/design-review.md` | DR-001 through DR-009, FA-001 through FA-004 |
| Router layer | `app/main.py` | `GET /vehicles/{vehicle_id}` route (line 49–54) |
| Service layer | `app/api/api.py` | `get_vehicle_by_id()` (line 6–7) |
| Data layer | `app/db/models.py` | `Vehicle` ORM + `VehicleResponse` Pydantic schema |
| DB session provider | `app/db/database.py` | `get_db()` generator, SQLite/PostgreSQL dual support |
| Test suite | `test/test_vehicle.py` | Three test functions covering AC-001, AC-002, AC-003 |
| Dependencies | `requirements.txt` | Currently outdated; FA-001 fixes this |

---

## Planning Assumptions and Constraints

| ID | Assumption / Constraint |
|---|---|
| PA-001 | **TASK-001 is a hard prerequisite for all other tasks.** The current `requirements.txt` pins (fastapi==0.46.0, uvicorn==0.11.1, pytest==5.3.2, requests==2.22.0) are incompatible with Python 3.14 and with the Pydantic v2 syntax already used in the codebase. No install, import, or test run will succeed until TASK-001 is complete. |
| PA-002 | The three-layer architecture (router `app/main.py`, service `app/api/api.py`, data `app/db/models.py` + `app/db/database.py`) is already correctly structured. Verification tasks (TASK-002 through TASK-005) confirm conformance; they require a code fix only if a gap is discovered. |
| PA-003 | The `vehicles` table must exist and be pre-populated before the application is started in any non-test environment (architecture A-001). No seeding script is in scope for this story. The test suite creates an in-memory SQLite database automatically via `Base.metadata.create_all`. |
| PA-004 | No database migration tooling (Alembic) is in scope. See OQ-002. |
| PA-005 | Python >=3.10 is required. The active interpreter is Python 3.14 (confirmed from `__pycache__` bytecode naming). |
| PA-006 | No changes to authentication, authorisation, listing, or any CRUD operation other than GET by ID are in scope (C-002, C-003). |

---

## Task List

### TASK-001: Update requirements.txt to modern, Python 3.14-compatible pins

- **Priority:** High
- **Depends on:** None
- **Blocked by:** None
- **FR/NFR trace:** DR-001, DR-002, DR-003, DD-001, DD-002, FA-001
- **Description:** Replace the outdated dependency pins in `requirements.txt` with versions that support Python 3.14 and Pydantic v2. The exact target versions are:
  - `fastapi==0.115.0`
  - `pydantic>=2.0.0,<3.0.0`
  - `uvicorn>=0.24.0`
  - `sqlalchemy>=1.4.0,<2.0.0`
  - `pytest>=7.0.0`
  - `requests>=2.28.0`
  - Retain: `psycopg2-binary` (no version change required)
- **Expected output:** `requirements.txt` updated; old pins removed.
- **Validation:** Run `pip install -r requirements.txt --dry-run` (or equivalent) and confirm no dependency conflict errors. The file should contain exactly the seven entries above.

---

### TASK-002: Verify router layer — FR-001, AC-002, AC-003

- **Priority:** Medium
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** FR-001, AC-001, AC-002, AC-003
- **Description:** Inspect `app/main.py` and confirm the following, applying fixes only if a gap is found:
  1. `GET /vehicles/{vehicle_id}` route is defined with `response_model=VehicleResponse`.
  2. `db: Session = Depends(get_db)` is injected correctly.
  3. `api.get_vehicle_by_id(vehicle_id, db)` is called and the result checked against `None`.
  4. `HTTPException(status_code=404, detail="Vehicle not found")` is raised when the vehicle is not found (AC-002).
  5. FastAPI's automatic JSON serialisation via `VehicleResponse` ensures `Content-Type: application/json` (AC-003).
  6. No `id` field is present in the response (architecture goal — ID excluded).
- **Expected output:** `app/main.py` confirmed correct; no changes required unless a gap is found.
- **Validation:** Code review against architecture Router Layer table. Covered by TASK-009 integration tests.

---

### TASK-003: Verify service layer — FR-001

- **Priority:** Medium
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** FR-001, DD-001
- **Description:** Inspect `app/api/api.py` and confirm that `get_vehicle_by_id` issues the correct ORM query:
  ```python
  db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
  ```
  Confirm the function returns the `Vehicle` ORM instance or `None` — no business transformation applied at this layer. Apply fixes only if the query deviates from the specification.
- **Expected output:** `app/api/api.py` confirmed correct; no changes required unless a gap is found.
- **Validation:** Code review against architecture Service Layer table. Covered by TASK-009 integration tests.

---

### TASK-004: Verify data layer — Vehicle ORM model and VehicleResponse schema

- **Priority:** Medium
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** FR-001, AC-001, DD-001, DD-005
- **Description:** Inspect `app/db/models.py` and confirm:
  1. `Vehicle` SQLAlchemy model maps to the `vehicles` table with all seven columns: `id` (PK), `make`, `model`, `year`, `price` (Numeric 12,2), `transmission`, `fuel_type`.
  2. `VehicleResponse` Pydantic v2 model exposes exactly the six required attributes — `make`, `model`, `year`, `price` (float), `transmission`, `fuel_type` — and does **not** expose `id`.
  3. `model_config = ConfigDict(from_attributes=True)` is present (required for ORM-to-Pydantic coercion).
  Apply fixes only if a gap is found.
- **Expected output:** `app/db/models.py` confirmed correct; no changes required unless a gap is found.
- **Validation:** Code review against architecture Data Layer table. Covered by TASK-009 integration tests (AC-001 verifies all six fields are returned; also asserts `"id" not in data`).

---

### TASK-005: Verify DB session provider

- **Priority:** Medium
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** FR-001, DD-002
- **Description:** Inspect `app/db/database.py` and confirm:
  1. `DATABASE_URL` is read from the environment variable, defaulting to `sqlite:///./carportal.db`.
  2. `check_same_thread=False` connect arg is applied only when the URL starts with `sqlite`.
  3. `get_db()` opens a session, yields it, and closes it in a `finally` block.
  4. `from sqlalchemy.orm import declarative_base` is used (requires SQLAlchemy >=1.4.0 — guaranteed by TASK-001).
  Apply fixes only if a gap is found.
- **Expected output:** `app/db/database.py` confirmed correct; no changes required unless a gap is found.
- **Validation:** Code review against architecture DB Session Provider table. Covered by TASK-009 integration tests.

---

### TASK-006: Add type annotations to get_vehicle_by_id (FA-002)

- **Priority:** Low
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** DR-007, FA-002
- **Description:** In `app/api/api.py`, update the signature of `get_vehicle_by_id` to include:
  - Parameter annotation: `db: Session` (import `Session` from `sqlalchemy.orm` if not already imported)
  - Return annotation: `-> Optional[Vehicle]` (import `Optional` from `typing` if not already imported)

  Before (line 6):
  ```python
  def get_vehicle_by_id(vehicle_id: int, db):
  ```
  After:
  ```python
  from typing import Optional
  from sqlalchemy.orm import Session

  def get_vehicle_by_id(vehicle_id: int, db: Session) -> Optional[Vehicle]:
  ```
- **Expected output:** `app/api/api.py` updated with complete type annotations on `get_vehicle_by_id`.
- **Validation:** Function signature visible in code review. Covered by TASK-009 test run (no regression).

---

### TASK-007: Replace payload.dict() with payload.model_dump() (FA-003)

- **Priority:** Low
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** DR-008, FA-003
- **Description:** In `app/main.py` line 39, replace the deprecated Pydantic v1 method call with the Pydantic v2 equivalent:

  Before:
  ```python
  payload = payload.dict()
  ```
  After:
  ```python
  payload = payload.model_dump()
  ```

  This is in the `/answer` route (`create_answer`), not in the vehicle route, but it lives in the same module and will generate `PydanticDeprecatedSince20` warnings once Pydantic v2 is installed via TASK-001.
- **Expected output:** `app/main.py` line 39 updated to `payload.model_dump()`.
- **Validation:** No `PydanticDeprecatedSince20` warnings during the TASK-009 test run. No regression on the vehicle endpoint.

---

### TASK-008: Update test docstring NFR-001 → AC-003 (FA-004)

- **Priority:** Low
- **Depends on:** TASK-001
- **Blocked by:** None
- **FR/NFR trace:** DR-009, FA-004, AC-003
- **Description:** In `test/test_vehicle.py`, update the docstring of `test_get_vehicle_content_type` to replace the undefined `NFR-001` reference with the now-formal `AC-003` identifier.

  Before (line 75):
  ```python
  """NFR-001 / AC-003: response Content-Type is application/json."""
  ```
  After:
  ```python
  """AC-003: response Content-Type is application/json."""
  ```
- **Expected output:** `test/test_vehicle.py` docstring updated; traceability reference is correct.
- **Validation:** Docstring visible in code review. No regression in TASK-009 test run.

---

### TASK-009: Run the full test suite and confirm all tests pass

- **Priority:** High
- **Depends on:** TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008
- **Blocked by:** None
- **FR/NFR trace:** FR-001, AC-001, AC-002, AC-003
- **Description:** From the project root, run:
  ```
  pytest test/test_vehicle.py -v
  ```
  All three tests must pass:
  - `test_get_vehicle_by_id_success` — verifies FR-001 / AC-001 (all six attributes, no `id`)
  - `test_get_vehicle_by_id_not_found` — verifies AC-002 (HTTP 404 + correct body)
  - `test_get_vehicle_content_type` — verifies AC-003 (Content-Type: application/json)

  If any test fails, diagnose and fix the root cause before proceeding. Do not mark this task complete until the output shows `3 passed`.
- **Expected output:** `pytest` output showing `3 passed, 0 failed, 0 errors`.
- **Validation:** Green test suite output. This is the final gate before the Review Agent (Step 6).

---

## Parallelization Opportunities

TASK-001 must complete first. Once it is done, **TASK-002 through TASK-008 are fully independent of each other** and can be executed in parallel (or in any order) by the Implementation Agent. TASK-009 depends on all seven and must run last.

```
TASK-001 (blocker)
     │
     ├── TASK-002  ─┐
     ├── TASK-003  ─┤
     ├── TASK-004  ─┤
     ├── TASK-005  ─┼──→  TASK-009 (final gate)
     ├── TASK-006  ─┤
     ├── TASK-007  ─┤
     └── TASK-008  ─┘
```

Recommended execution order if running serially: TASK-001 → TASK-006 → TASK-007 → TASK-008 → TASK-002 → TASK-003 → TASK-004 → TASK-005 → TASK-009 (code changes first, then verification, then tests).

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RI-001 | Installing FastAPI 0.115.0 may pull a transitively incompatible version of a sub-dependency (e.g. `starlette`, `anyio`) that breaks `from starlette.testclient import TestClient`. | Low | Medium | If import errors appear after TASK-001, inspect `pip install -r requirements.txt` output for conflicting sub-dependency pins and add explicit pins as needed. |
| RI-002 | SQLAlchemy 1.4.x plus Python 3.14 may emit deprecation warnings (SQLAlchemy 1.4 is the legacy series). These are warnings only and will not fail the tests, but they could obscure other output. | Medium | Low | Acceptable for MVP. If noise is excessive, add `-W ignore::DeprecationWarning` to the pytest invocation. Upgrading to SQLAlchemy 2.x is a future story. |
| RI-003 | No seeding mechanism is in scope (A-001). Running the app against a fresh PostgreSQL database will return 404 for every vehicle ID until the `vehicles` table is populated externally. | Low | Medium | Document this clearly in deployment notes. The test suite uses an in-memory SQLite fixture and is unaffected. |

---

## Open Questions

| ID | Question | Owner | Priority | Carried From |
|---|---|---|---|---|
| OQ-002 | Is there an Alembic migration or a seeding script for the `vehicles` table, or must it be created and populated manually before the application is run in production? No migration tooling was found in the working tree. | Product / DevOps | Medium | `artifacts/architecture.md` OQ-002 |
| OQ-003 | Should the `id` field ever be exposed in the response (e.g., for client-side navigation)? Current design deliberately excludes it from `VehicleResponse`. | Product / Requirements Agent | Low | `artifacts/architecture.md` OQ-003 |

---

## Requirement Traceability Summary

| Task | FR-001 | AC-001 | AC-002 | AC-003 | DR / FA Reference |
|---|---|---|---|---|---|
| TASK-001 | Indirect (enables all) | — | — | — | DR-001, DR-002, DR-003, FA-001 |
| TASK-002 | Direct | Direct | Direct | Direct | — |
| TASK-003 | Direct | — | — | — | — |
| TASK-004 | Direct | Direct | — | — | — |
| TASK-005 | Indirect | — | — | — | DD-002 |
| TASK-006 | Indirect | — | — | — | DR-007, FA-002 |
| TASK-007 | Indirect | — | — | — | DR-008, FA-003 |
| TASK-008 | — | — | — | Direct | DR-009, FA-004 |
| TASK-009 | Direct | Direct | Direct | Direct | All |
