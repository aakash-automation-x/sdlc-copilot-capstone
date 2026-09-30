# Implementation Plan

## Overview

This plan delivers **FR-001: Retrieve Vehicle Details by ID** as a `GET /vehicles/{vehicle_id}` endpoint backed by a SQLAlchemy ORM integration and PostgreSQL. The feature extends the existing three-layer FastAPI monolith with a dedicated ORM code path while preserving legacy JSON flat-file endpoints.

**Scope:**
- Update production dependencies (`requirements.txt`)
- Create database session factory (`app/db/database.py`)
- Refactor data models (`app/db/models.py`): delete collision-prone Pydantic class, add SQLAlchemy ORM model + response schema
- Implement service function (`app/api/api.py`)
- Add HTTP route (`app/main.py`)
- Create test suite with in-memory SQLite (`test/test_vehicle.py`)
- Remove dead code (`app/api/api.py`)

**Delivery sequence:** Foundational work (dependencies, models, database session) precedes service layer and router, which precede testing and validation.

**Key blockers resolved:** All Critical and High findings from `design-review.md` have agreed decisions (DR-001 through DR-010).

## Source References

- **Architecture:** `artifacts/architecture.md` (commit `6ca3de8`)
- **Requirements:** `artifacts/requirements.md` (commit `65ab0f7`)
- **Design Review:** `artifacts/design-review.md` (all findings resolved)

## Assumptions and Constraints

- The `vehicles` table does not pre-exist in the target database and will be created by `Base.metadata.create_all(bind=engine)` at application startup (DR-006).
- Seed data is out of scope for FR-001 (DR-007); the table will be empty after schema creation. A one-line SQL insert example is provided in deployment notes for manual testing.
- `app/db/database.py` and `test/test_vehicle.py` source files are absent and must be created as new files, not modifications (DR-004, DR-005).
- The existing Pydantic `Vehicle` class in `models.py` must be deleted before the SQLAlchemy ORM class is added (DR-003).
- All code must conform to `code-quality.md` (OWASP, DRY, clarity) and test code to `tests.md` (coverage, structure, determinism).
- `DATABASE_URL` environment variable is available in all deployment environments; if absent, the application fails fast at startup.

## Task List

### TASK-001: Update requirements.txt with ORM and framework dependencies

- **Priority:** High
- **FR/NFR:** NFR-001
- **Architecture section:** Deployment, Technology Choices
- **Depends on:** None
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Update `requirements.txt` to replace legacy pinned versions with versions compatible with SQLAlchemy 2.0, Pydantic v2, and modern FastAPI. Add `sqlalchemy>=2.0.0` and `psycopg2-binary>=2.9.0` (both absent and required for ORM). Update existing pins: `fastapi>=0.100.0` (current: `0.46.0`), `pydantic>=2.0.0` (implicit in current fastapi), `uvicorn>=0.20.0` (current: `0.11.1`), `pytest>=7.4.0` (current: `5.3.2`), `requests>=2.28.0` (current: `2.22.0`). Verify clean install: `pip install -r requirements.txt` must succeed with no warnings.
- **Expected output:** Updated `requirements.txt` with all eight packages pinned to approved versions.
- **Validation:** `pip install -q -r requirements.txt && python -c "import sqlalchemy; import psycopg2; import fastapi; print('OK')"` succeeds.
- **Rationale:** Unblocks all downstream tasks; without this, ORM imports fail and tests cannot run. Resolves DR-001 and DR-002.

### TASK-002: Delete legacy Pydantic Vehicle class from models.py

- **Priority:** High
- **FR/NFR:** FR-001
- **Architecture section:** Components and Responsibilities (Data layer), Assumptions and Constraints
- **Depends on:** None
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Open `app/db/models.py` and delete the Pydantic `Vehicle` class (fields: `id`, `name`, `make`, `model`, `year`, `price`, `transmission`, `fuel_type`, `category`, `link`). Retain `Answer` and `UserAnswer` classes if present. This class is not wired to any live route, conflicts with the incoming SQLAlchemy ORM model, and must be removed before that model is added to prevent shadowing at module scope.
- **Expected output:** `app/db/models.py` with Pydantic `Vehicle` class removed; `Answer` and `UserAnswer` unchanged.
- **Validation:** Grep confirms no reference to a Pydantic `Vehicle` class remains in the file. SQLAlchemy imports (e.g., `Column`, `String`, `Integer`) do not fail.
- **Rationale:** Resolves the naming collision identified in DR-003. Must complete before TASK-003 adds the ORM model.

### TASK-003: Create SQLAlchemy ORM Vehicle model and VehicleResponse schema in models.py

- **Priority:** High
- **FR/NFR:** FR-001, NFR-001
- **Architecture section:** Components and Responsibilities (Data layer), Key Components
- **Depends on:** TASK-002
- **Blocked by:** TASK-001 (requires `sqlalchemy>=2.0.0` and `pydantic>=2.0.0` available)
- **Target agent:** Implementation Agent
- **Description:** Add SQLAlchemy ORM `Vehicle` model and Pydantic `VehicleResponse` schema to `app/db/models.py`. ORM model: class name `Vehicle`, `__tablename__ = "vehicles"`, columns: `id` (Integer primary key), `make` (String), `model` (String), `year` (Integer), `price` (String), `transmission` (String), `fuel_type` (String) — all non-nullable. Pydantic schema: class name `VehicleResponse`, fields matching ORM columns, config `from_attributes=True` (Pydantic v2 syntax for ORM mode).
- **Expected output:** `app/db/models.py` with both classes defined; no syntax errors; `from app.db.models import Vehicle, VehicleResponse` succeeds.
- **Validation:** Python import succeeds: `python -c "from app.db.models import Vehicle, VehicleResponse; print(Vehicle, VehicleResponse)"`.
- **Rationale:** Implements the data model layer required by FR-001. Must follow TASK-002 (delete collision) and TASK-001 (dependencies available).

### TASK-004: Create database.py session factory with get_db generator

- **Priority:** High
- **FR/NFR:** NFR-001
- **Architecture section:** Components and Responsibilities (Session factory), Key Components, Data Flow
- **Depends on:** TASK-001
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Create `app/db/database.py` as a new file. Implement: SQLAlchemy `create_engine` reading `DATABASE_URL` environment variable (default `sqlite:///./carportal.db`), `SessionLocal = sessionmaker(bind=engine)`, `Base = declarative_base()`, and `get_db` generator function using `try/finally` to ensure session cleanup. The `get_db` function yields a `SessionLocal()` instance and closes it in the finally block. This file provides the dependency-injection entry point for FastAPI routes via `Depends(get_db)`.
- **Expected output:** New file `app/db/database.py` with engine, SessionLocal, Base, and get_db defined. No syntax errors.
- **Validation:** `python -c "from app.db.database import engine, SessionLocal, Base, get_db; print('OK')"` succeeds. Manual verification: engine can connect to the database (or SQLite file if using default).
- **Rationale:** Implements the session factory required by the architecture. Must be created before routes can use `Depends(get_db)`. Closes DR-004 and DR-005.

### TASK-005: Add get_vehicle_by_id service function to api.py

- **Priority:** High
- **FR/NFR:** FR-001
- **Architecture section:** Components and Responsibilities (Service layer), Data Flow
- **Depends on:** TASK-003, TASK-004
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Add function `get_vehicle_by_id(vehicle_id: int, db: Session) -> VehicleResponse | None` to `app/api/api.py`. Query the database: `db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()`. If a row is found, return it as a `VehicleResponse` (Pydantic conversion via `from_attributes=True`); otherwise return `None`. The service layer does not raise HTTP exceptions — that is the router's responsibility. Import `Vehicle` and `VehicleResponse` from `app.db.models` and `Session` from `sqlalchemy.orm`.
- **Expected output:** `app/api/api.py` with `get_vehicle_by_id` function added; imports updated.
- **Validation:** `python -c "from app.api.api import get_vehicle_by_id; import inspect; sig = inspect.signature(get_vehicle_by_id); print(sig)"` returns `(vehicle_id: int, db: Session) -> VehicleResponse | None`.
- **Rationale:** Implements the business logic layer for FR-001. Called by the router layer. Depends on the ORM model (TASK-003) and session factory (TASK-004).

### TASK-006: Add GET /vehicles/{vehicle_id} route to main.py

- **Priority:** High
- **FR/NFR:** FR-001
- **Architecture section:** Components and Responsibilities (Router layer), Data Flow
- **Depends on:** TASK-005, TASK-004
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Add a new route to `app/main.py`: `@app.get("/vehicles/{vehicle_id}")` where `vehicle_id` is a path parameter (FastAPI auto-validates as integer). Inject `db: Session = Depends(get_db)` and call `get_vehicle_by_id(vehicle_id, db)`. If the result is not `None`, return it (HTTP 200, automatic JSON serialization via Pydantic). If `None`, raise `HTTPException(status_code=404, detail="Vehicle not found")`. Verify no route conflicts with legacy endpoints (`/user`, `/question`, `/alternatives`, `/answer`, `/result`).
- **Expected output:** `app/main.py` updated with the new route; import `HTTPException` from `fastapi`, import `Depends` from `fastapi`, import `Session` from `sqlalchemy.orm`, import `get_db` from `app.db.database`, import `get_vehicle_by_id` and `VehicleResponse` from `app.api.api`.
- **Validation:** Start the server: `uvicorn app.main:app --reload`. Verify docs at `/docs` show the new endpoint. Manual curl test (with a vehicle in the database): `curl http://127.0.0.1:8000/vehicles/1` returns HTTP 200 with JSON. Unknown ID: returns HTTP 404.
- **Rationale:** Implements the HTTP router layer for FR-001. Must follow the service function (TASK-005) and session factory (TASK-004).

### TASK-007: Remove dead-code read_vehicle function from api.py

- **Priority:** Medium
- **FR/NFR:** N/A (code cleanup; reduces maintenance burden per DR-010)
- **Architecture section:** Assumptions and Constraints, Risks and Mitigations
- **Depends on:** TASK-005 (the live ORM path is fully implemented)
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Delete the `read_vehicle(vehicle_id)` function from `app/api/api.py`. This function reads from `data/cars.json` using JSON flat-file lookups and is not wired to any HTTP route; it is dead code. Check whether `Optional`, `Dict`, or other imports from `typing` are used only by `read_vehicle`; if so, remove those imports as well. Ensure no other function in `api.py` calls `read_vehicle` before deletion.
- **Expected output:** `app/api/api.py` with `read_vehicle` function removed; unused imports cleaned up.
- **Validation:** `grep -n "read_vehicle" app/api/api.py` returns no matches. `grep -r "read_vehicle" app/ test/` returns no matches.
- **Rationale:** Prevents accidental reactivation of the JSON flat-file vehicle lookup, which is inconsistent with the ORM path. Keeps the codebase clean. Resolves DR-010.

### TASK-008: Create test/test_vehicle.py with ORM test suite

- **Priority:** High
- **FR/NFR:** FR-001, AC-001
- **Architecture section:** Components and Responsibilities (Test database), Deployment, Key Components
- **Depends on:** TASK-003, TASK-004
- **Blocked by:** TASK-001 (requires `pytest>=7.4.0`)
- **Target agent:** Implementation Agent
- **Description:** Create `test/test_vehicle.py` as a new file. Implement an in-memory SQLite test database with dependency override: use `create_engine("sqlite:///:memory:")`, override `get_db` to use the in-memory engine, create an `autouse` fixture that calls `Base.metadata.create_all(bind=engine)` and `Base.metadata.drop_all(bind=engine)` (setup/teardown per test). Seed one test `Vehicle` row per test execution. Write two test cases: (1) happy path — `GET /vehicles/{vehicle_id}` with a known ID returns HTTP 200 with all six fields (`make`, `model`, `year`, `price`, `transmission`, `fuel_type`); (2) not-found path — `GET /vehicles/{unknown_id}` returns HTTP 404. Use `TestClient` from `starlette.testclient` to invoke the app. All tests deterministic (no random data, fixed IDs, no file I/O).
- **Expected output:** New file `test/test_vehicle.py` with at least two test functions and an autouse fixture; no external dependencies or database required to run.
- **Validation:** `pytest test/test_vehicle.py -v` passes both test cases. Verify test coverage: `pytest test/test_vehicle.py --cov=app.api --cov=app.db --cov=app.main` reports coverage of the new route and service function.
- **Rationale:** Verifies AC-001 (the acceptance criterion for FR-001). Follows the pattern established in `test/test.py` (TestClient + dependency override). Must follow model and session factory tasks (TASK-003, TASK-004) so the fixture can seed the in-memory database. Closes DR-004.

### TASK-009: Verify all tests pass (gated suite)

- **Priority:** High
- **FR/NFR:** FR-001, NFR-001
- **Architecture section:** Deployment (CI/CD)
- **Depends on:** TASK-008
- **Blocked by:** None
- **Target agent:** Verify Agent
- **Description:** Run the gated test suite: `pytest test/test_vehicle.py -v`. This is the deployment gate specified in `architecture.md` Deployment section. All tests must pass. If any test fails, investigate root cause, fix the issue, and re-run until all tests pass. Do not skip or suppress test failures.
- **Expected output:** All tests in `test/test_vehicle.py` pass; pytest summary shows `passed=X, failed=0`.
- **Validation:** Exit code 0 from `pytest test/test_vehicle.py -v`. No skipped tests. Coverage report (optional): `pytest test/test_vehicle.py --cov=app.api --cov=app.db --cov=app.main`.
- **Rationale:** Confirms FR-001 and AC-001 are implemented correctly and meet acceptance criteria. This is a gate; deployment cannot proceed if this task fails.

### TASK-010: Verify app starts and serves the new endpoint

- **Priority:** High
- **FR/NFR:** FR-001, NFR-001
- **Architecture section:** Deployment, Technology Choices
- **Depends on:** TASK-006, TASK-004
- **Blocked by:** TASK-001 (dependencies available), Database server available (PostgreSQL for production or SQLite default)
- **Target agent:** Verify Agent
- **Description:** Start the application: `uvicorn app.main:app --reload`. Verify no errors in startup logs. Verify the application initializes the database schema: `Base.metadata.create_all(bind=engine)` is called during startup and creates the `vehicles` table in PostgreSQL (or SQLite if using default). Verify the OpenAPI documentation includes the new endpoint at `/docs`. Verify the endpoint responds to an HTTP GET request (even if the response is 404 or 200 depends on whether test data exists).
- **Expected output:** Application starts cleanly. Server logs show no errors. `/docs` includes `GET /vehicles/{vehicle_id}` in the API spec. A manual request to the endpoint (e.g., `curl http://127.0.0.1:8000/vehicles/1`) returns HTTP 200 or 404 (not 500 or 422 for valid ID).
- **Validation:** Uvicorn process starts without errors. HTTP request to `/docs` returns 200. HTTP request to `/vehicles/1` returns 200, 404, or appropriate error (not 500). Logs show no import errors or connection failures. For PostgreSQL: verify table exists with `\dt vehicles` in psql.
- **Rationale:** Confirms the full stack (models, database, service, router) works end-to-end. Must follow route and session factory implementations. Validates the deployment assumption that `DATABASE_URL` is set correctly.

### TASK-011: Ensure app starts with Base.metadata.create_all at startup

- **Priority:** High
- **FR/NFR:** NFR-001
- **Architecture section:** Deployment (Schema management), Assumptions and Constraints
- **Depends on:** TASK-004, TASK-003
- **Blocked by:** None
- **Target agent:** Implementation Agent
- **Description:** Modify `app/main.py` (or `app/db/database.py` if more appropriate) to call `Base.metadata.create_all(bind=engine)` during application initialization, before any routes are registered or the server starts. This ensures the `vehicles` table is created on first startup if it does not exist. Verify this call is idempotent (safe to call multiple times without error). Example location: in `app/main.py` after `app = FastAPI()`, add `Base.metadata.create_all(bind=engine)` before route definitions.
- **Expected output:** Application startup code modified to call `create_all`; table is created on first run.
- **Validation:** Fresh SQLite file: start app, check `sqlite3 carportal.db ".tables"` shows `vehicles`. Fresh PostgreSQL database: start app, check `psql -d carportal -c "\dt vehicles"` shows the table. Restart app: no errors; table is not dropped or recreated.
- **Rationale:** Implements the schema-creation strategy agreed in DR-006. Must follow model and database tasks. Makes deployment self-healing for first startup.

### TASK-012: Integration test with real database (optional post-launch)

- **Priority:** Low
- **FR/NFR:** NFR-001
- **Architecture section:** Deployment, Risks and Mitigations
- **Depends on:** TASK-009, TASK-010
- **Blocked by:** None (optional; noted in architecture Risks)
- **Target agent:** Verify Agent (future iteration)
- **Description:** Create an optional integration test that runs against a real PostgreSQL instance (not in-memory SQLite) to verify no dialect-specific bugs exist. This is deferred to a follow-on task and is not required for FR-001 acceptance. Noted in architecture risks: "SQLite/PostgreSQL dialect differences mask bugs in tests" (Low likelihood, Medium impact).
- **Expected output:** Documented as a future iteration; no implementation in this run.
- **Validation:** N/A for this iteration.
- **Rationale:** Risk mitigation for long-term reliability; not required to close FR-001. Defer unless user requests.

## Parallelization Opportunities

1. **TASK-002 and TASK-004 can run in parallel** after TASK-001 completes: deleting the legacy Pydantic class does not depend on the session factory, and vice versa.
2. **TASK-003 (ORM model) and TASK-004 (session factory) can run in parallel** after TASK-001 and TASK-002 complete: both depend on dependencies being available and the collision being resolved, but they do not depend on each other directly.
3. **TASK-007 (dead-code removal) can run in parallel with TASK-005** after TASK-005 is complete: the live ORM function is in place, so removing the dead function cannot break anything.

**Recommended parallelization sequence:**
1. TASK-001 alone
2. TASK-002, TASK-004 in parallel (both depend on TASK-001)
3. TASK-003 after TASK-002 (depends on collision resolution)
4. TASK-005, TASK-006, TASK-007 after TASK-003 and TASK-004 (TASK-005 and TASK-006 depend on models and session; TASK-007 is independent once TASK-005 is done)
5. TASK-008, TASK-009, TASK-010, TASK-011 sequentially (all depend on earlier tasks)

## Blocked Tasks

| Task | Blocked by | Unblock criteria |
| --- | --- | --- |
| TASK-003 | TASK-001 | `sqlalchemy>=2.0.0` and `pydantic>=2.0.0` must be available in environment |
| TASK-003 | TASK-002 | Existing Pydantic `Vehicle` class must be deleted to prevent naming collision |
| TASK-005 | TASK-001 | `sqlalchemy>=2.0.0` must be available |
| TASK-005 | TASK-003, TASK-004 | ORM model and session factory must be defined before service function can use them |
| TASK-006 | TASK-001 | All dependencies must be available |
| TASK-006 | TASK-005, TASK-004 | Service function and session factory must exist before route can call them |
| TASK-008 | TASK-001 | `pytest>=7.4.0` must be available |
| TASK-008 | TASK-003, TASK-004 | ORM model and session factory must exist for fixture to seed test database |
| TASK-009 | TASK-008 | Test file must exist and be runnable |
| TASK-010 | TASK-001 | All dependencies must be available to start the app |
| TASK-010 | TASK-006, TASK-004 | Route and session factory must be implemented |
| TASK-011 | TASK-004, TASK-003 | Session factory and ORM model must exist before `create_all` is called |

## Risks and Open Questions

### Risks

1. **`DATABASE_URL` not set in production** (Medium likelihood, High impact — noted in architecture): If the environment variable is not set, the application fails at startup. Mitigation: document required env vars in deployment notes; fail fast with a clear error message if `DATABASE_URL` is missing. (Open — developer/operator responsibility.)

2. **Schema drift between ORM model and actual DB table** (Low likelihood, Medium impact — noted in architecture): Column mismatches cause runtime errors. Mitigation: Alembic migrations deferred to a follow-on task (DR-006); `create_all` is acceptable for FR-001 scope. (Open — log for future iteration.)

3. **SQLite/PostgreSQL dialect differences mask bugs in tests** (Low likelihood, Medium impact — noted in architecture): Tests pass on SQLite but fail on PostgreSQL. Mitigation: add an integration test stage in CI that runs against a real PostgreSQL instance (TASK-012, deferred). (Open — noted in architecture Risks.)

4. **Incomplete TASK-011 (schema creation)**: If `Base.metadata.create_all` is not called during app startup, the database table will not be created and all requests will fail with a 500 error. Mitigation: ensure TASK-011 is completed and verified; this is a deployment prerequisite. (Open — Implementation Agent responsibility.)

### Open Questions

1. **Seed data for the `vehicles` table**: Where will the initial data come from? Answer (DR-007): Out of scope for FR-001. The table will be empty after `create_all`. For local development, a one-line SQL insert example is provided in deployment notes. For production, data population is an operational concern.

2. **Container specification**: Is a `Dockerfile` required before the first deployment? Answer: No container requirement exists in the current approved requirements; defer unless user requests it. (Open.)

3. **`/health` endpoint**: Should a `GET /health` endpoint be added for container orchestration probes? Answer (DR-011): Deferred to a future iteration. (Open.)

4. **Alembic migrations**: When should Alembic be introduced? Answer (DR-006): Defer to a future iteration when schema evolution is first required. (Open.)

## Recommended First Task for Implementation Agent

**TASK-001 — Update requirements.txt with ORM and framework dependencies**

This task unblocks all downstream work. Without it, the ORM, Pydantic v2, and modern FastAPI imports fail, preventing every other task from running. Estimated effort: **5 minutes**. No dependencies.

---

## Summary of Design Review Decisions Implemented

This plan directly reflects all agreed decisions from `artifacts/design-review.md`:

| Decision | Implemented by |
| --- | --- |
| DR-001: Update `requirements.txt` with `sqlalchemy`, `psycopg2-binary`, and version bumps | TASK-001 |
| DR-002: Standardise on Pydantic v2 (`from_attributes=True`) | TASK-001, TASK-003 |
| DR-003: Delete existing Pydantic `Vehicle` class; add ORM model + schema | TASK-002, TASK-003 |
| DR-004, DR-005: Create `app/db/database.py` and `test/test_vehicle.py` as new files | TASK-004, TASK-008 |
| DR-006: Use `Base.metadata.create_all` at startup (Alembic deferred) | TASK-011 |
| DR-007: Seed data out of scope; SQL insert example provided | TASK-010 (documentation note) |
| DR-008: TLS required in production (load-balancer/reverse-proxy) | TASK-010 (deployment note) |
| DR-009: Python 3.11+ recommended (NFR-001 minimum 3.8 unchanged) | TASK-001 |
| DR-010: Remove dead `read_vehicle` function | TASK-007 |
| DR-012: Document SQLAlchemy pool defaults (`pool_size=5`, `max_overflow=10`) | TASK-010 (deployment note) |

All Critical and High findings are resolved; Low findings are either resolved or deferred.
