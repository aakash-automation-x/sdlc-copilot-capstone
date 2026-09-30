# Architecture

## Overview

The system is a three-layer FastAPI monolith that exposes vehicle data through a RESTful
HTTP API. The `GET /vehicles/{vehicle_id}` feature (FR-001) is delivered by extending the
existing router, service, and data layers with a new SQLAlchemy ORM-backed code path.
PostgreSQL serves as the production database (NFR-001); SQLite in-memory is used during
automated tests for isolation and speed.

## Architectural Goals and Drivers

| ID | Statement | Architectural impact |
| --- | --- | --- |
| FR-001 | Expose `GET /vehicles/{vehicle_id}` returning make, model, year, price, transmission, fuel_type | Requires a new route, service function, ORM model, Pydantic response schema, and database session dependency |
| NFR-001 | Python 3.8+, FastAPI, PostgreSQL, SQLAlchemy | Constrains language, framework, database engine, and ORM layer; no other technology may be substituted without explicit approval |

## Recommended Architecture

Extend the existing three-layer FastAPI monolith with a dedicated ORM code path for the
new vehicle endpoint. The existing JSON flat-file code paths (legacy endpoints) remain
untouched. The new path introduces:

- A `vehicles` table in PostgreSQL managed by SQLAlchemy.
- A `database.py` session factory (`get_db`) yielding `SessionLocal` instances via
  FastAPI's `Depends` mechanism.
- A SQLAlchemy ORM `Vehicle` model in `models.py`.
- A `VehicleResponse` Pydantic schema (response serialisation).
- A `get_vehicle_by_id(vehicle_id, db)` service function in `api.py`.
- A `GET /vehicles/{vehicle_id}` route in `main.py` wiring the above together.

## Component Diagram

```mermaid
graph TD
    Client["HTTP Client"]
    Router["Router Layer\napp/main.py"]
    Service["Service Layer\napp/api/api.py"]
    ORM["ORM Model\napp/db/models.py\n(Vehicle SQLAlchemy + VehicleResponse Pydantic)"]
    DB["Database Session Factory\napp/db/database.py\n(get_db / SessionLocal)"]
    PG["PostgreSQL\nvehicles table"]

    Client -->|GET /vehicles/{vehicle_id}| Router
    Router -->|get_vehicle_by_id(vehicle_id, db)| Service
    Router -->|Depends(get_db)| DB
    DB -->|yields Session| Router
    Service -->|db.query(Vehicle).filter(...)| ORM
    ORM -->|SQL SELECT| PG
    PG -->|Row| ORM
    ORM -->|VehicleResponse| Service
    Service -->|VehicleResponse JSON| Router
    Router -->|HTTP 200 / 404| Client
```

## Key Components and Responsibilities

| Component | Responsibility | FR/NFR |
| --- | --- | --- |
| `app/main.py` (Router layer) | Define `GET /vehicles/{vehicle_id}` route; inject `db` session via `Depends(get_db)`; map service result to HTTP 200 response or raise HTTP 404 | FR-001 |
| `app/api/api.py` (Service layer) | Implement `get_vehicle_by_id(vehicle_id, db)`: query the ORM, return `VehicleResponse` or `None`; raise no HTTP exceptions (that is the router's concern) | FR-001 |
| `app/db/models.py` (Data layer) | Define `Vehicle` SQLAlchemy ORM model (`__tablename__ = "vehicles"`, columns: id, make, model, year, price, transmission, fuel_type); define `VehicleResponse` Pydantic schema with `from_attributes=True` | FR-001, NFR-001 |
| `app/db/database.py` (Session factory) | Create SQLAlchemy engine from `DATABASE_URL` env var (default `sqlite:///./carportal.db`); define `SessionLocal`; expose `get_db` generator for FastAPI `Depends` | NFR-001 |
| PostgreSQL (Production DB) | Persist vehicle records in the `vehicles` table; enforce primary key constraint on `id` | NFR-001 |
| SQLite in-memory (Test DB) | Replace PostgreSQL via `get_db` override in `test/test_vehicle.py`; created and dropped per test; no file I/O | NFR-001 |

## Data Flow

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant Router as app/main.py
    participant DB as app/db/database.py
    participant Service as app/api/api.py
    participant Model as app/db/models.py
    participant PG as PostgreSQL

    Client->>Router: GET /vehicles/{vehicle_id}
    Router->>DB: Depends(get_db) — open SessionLocal
    DB-->>Router: db session
    Router->>Service: get_vehicle_by_id(vehicle_id, db)
    Service->>Model: db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    Model->>PG: SELECT * FROM vehicles WHERE id = ?
    PG-->>Model: row or None
    Model-->>Service: Vehicle ORM instance or None
    alt Vehicle found
        Service-->>Router: VehicleResponse (Pydantic)
        Router-->>Client: HTTP 200 JSON {make, model, year, price, transmission, fuel_type}
    else Not found
        Service-->>Router: None
        Router-->>Client: HTTP 404 {detail: "Vehicle not found"}
    end
    Router->>DB: close SessionLocal (finally block in get_db)
```

## Technology Choices

| Decision | Choice | Rationale | Trade-offs |
| --- | --- | --- | --- |
| Language | Python 3.8+ (runtime: 3.11+ recommended) | Mandated by NFR-001; matches existing codebase. Python 3.8 reached EOL October 2024; 3.11+ is required for security support. See DR-009. | NFR-001 cannot be changed without a requirements update; minimum version constraint will be revisited in a future pipeline run |
| Web framework | FastAPI `>=0.100.0` | Mandated by NFR-001; provides automatic OpenAPI docs, async support, Pydantic v2 integration, and dependency injection. `fastapi==0.46.0` (previously pinned) uses Pydantic v1 and is incompatible with `from_attributes=True`; see DR-002. | Smaller ecosystem than Django; async not used in current sync handlers |
| ORM | SQLAlchemy `>=2.0.0` | Mandated by NFR-001; industry standard Python ORM; portable across DB backends. Must be added to `requirements.txt` — was absent (DR-001). | Adds abstraction overhead; Alembic for schema migrations deferred to a follow-on task (DR-006) |
| Pydantic | `pydantic>=2.0.0` | Provides `from_attributes=True` on `VehicleResponse` for ORM-to-schema serialisation. Pydantic v1 (bundled with `fastapi==0.46.0`) does not support this syntax; see DR-002. | Breaking changes from v1; existing Pydantic models in `models.py` must use v2-compatible syntax |
| PostgreSQL driver | `psycopg2-binary>=2.9.0` | Required for SQLAlchemy to connect to PostgreSQL. Was absent from `requirements.txt` (DR-001). | `psycopg2-binary` bundles the C extension; use `psycopg2` for production builds where system libraries are available |
| Production database | PostgreSQL | Mandated by NFR-001; ACID-compliant, production-grade, supported by SQLAlchemy | Requires a running PostgreSQL instance; not bundled with the app |
| Test database | SQLite (in-memory) | No server required; fast; isolated per test via dependency override; matches existing project test pattern | SQLite dialect differences may hide PostgreSQL-specific bugs |
| Response schema | Pydantic `VehicleResponse` with `from_attributes=True` | Decouples ORM internals from API surface; enables field-level validation and OpenAPI schema generation. Requires `pydantic>=2.0.0`. | Must stay in sync with ORM model column names |
| Configuration | `DATABASE_URL` environment variable | Follows 12-factor app; avoids hard-coded credentials | Requires correct env var setup in every deployment environment |

## SDLC Pipeline Components

| Type | Name | Purpose |
| --- | --- | --- |
| Agent | Architect Agent (Step 2) | Produces this document from approved requirements |
| Agent | Design Review Agent (Step 3) | Reviews this document for completeness, correctness, and risk |
| Agent | Planner Agent (Step 4) | Breaks architecture into discrete implementation tasks in `impl-plan.md` |
| Agent | Implementation Agent (Step 5) | Writes production code and tests per `impl-plan.md` tasks |
| Agent | Review Agent (Step 6) | Reviews implemented code against architecture and quality rules |
| Agent | Verify Agent (Step 7) | Runs tests and confirms all FR/NFR acceptance criteria are met |
| Agent | PR Agent (Step 8) | Opens pull request and writes `CHANGELOG.md` |
| Skill | `design-architecture` | Owns the full architect workflow (this document was produced by it) |
| Skill | `sdlc-traceability` | Maintains stable FR/NFR/TASK IDs across all artifacts |
| Rule | `code-quality.md` | Enforces OWASP-safe, DRY, clear-code standards on all `.py` files |
| Rule | `tests.md` | Enforces coverage, structure, and determinism rules on test files |
| Rule | `sdlc-artifacts.md` | Enforces document structure, traceability, and writing quality on `artifacts/**/*.md` |

## Security Considerations

- **Input validation:** FastAPI validates `vehicle_id` as an integer at the route boundary
  before it reaches the service layer; non-integer path segments return HTTP 422
  automatically.
- **SQL injection:** SQLAlchemy ORM uses parameterised queries exclusively; no raw SQL
  string interpolation is used (FR-001 code path). The `read_vehicle` dead-code JSON path
  must not be re-activated without removing it or replacing it with the ORM path.
- **Secrets management:** The database connection string is read from the `DATABASE_URL`
  environment variable and never hard-coded or logged (NFR-001).
- **Authentication/authorisation:** Out of scope per approved requirements. No auth
  mechanism is introduced on this endpoint.
- **Error messages:** HTTP 404 returns a generic `"Vehicle not found"` message and does
  not leak internal schema, table names, or SQL details.

## Reliability and Observability

- **Session lifecycle:** `get_db` uses a `try/finally` generator so that `SessionLocal`
  is always closed even when an exception is raised in the route handler.
- **404 handling:** The service function returns `None` for an unknown ID; the router
  converts this to HTTP 404. This is the only expected runtime error for this endpoint.
- **Logging:** FastAPI's default Uvicorn access log records every request and HTTP status
  code. Structured application-level logging is not mandated by the current requirements
  but should be added before production deployment.
- **Database connectivity failures:** If the database is unavailable, SQLAlchemy raises a
  connection error that propagates as HTTP 500. No retry or circuit-breaker logic is
  required by the current requirements; this is noted as an open risk.

## Scalability and Performance

- The `GET /vehicles/{vehicle_id}` endpoint is a primary-key lookup on the `vehicles`
  table, giving O(1) query complexity when the table has a B-tree index on `id` (default
  PostgreSQL primary key behaviour).
- The Uvicorn + FastAPI stack supports multiple worker processes via Gunicorn or similar
  process managers to handle concurrent requests.
- No caching, pagination, or rate-limiting is required by FR-001 or NFR-001 and is
  explicitly out of scope.
- The bottleneck under load is the PostgreSQL connection pool. SQLAlchemy's `QueuePool`
  defaults to `pool_size=5` and `max_overflow=10` (15 total connections maximum). These
  values should be tuned to match the deployment environment's database connection limits
  before production traffic ramps up. See DR-012.

## Deployment

- **Runtime:** Python 3.11+ recommended (Python 3.8 is the NFR-001 minimum but reached
  EOL in October 2024; see DR-009). Dependencies listed in `requirements.txt`.
- **Dependency update required (DR-001, DR-002):** Before deploying, update
  `requirements.txt` to include `sqlalchemy>=2.0.0`, `psycopg2-binary>=2.9.0`,
  `pydantic>=2.0.0`, `fastapi>=0.100.0`, `uvicorn>=0.20.0`, `pytest>=7.4.0`,
  `requests>=2.28.0`. The previously pinned `fastapi==0.46.0` is incompatible with
  Pydantic v2 and must be replaced.
- **Server:** `uvicorn app.main:app --reload` for development; a production deployment
  should use `gunicorn -k uvicorn.workers.UvicornWorker` with multiple workers.
- **TLS:** Production deployments must terminate TLS at the load-balancer or reverse-proxy
  layer (e.g., Nginx, AWS ALB). Plain HTTP must not be exposed externally (OWASP A02).
- **Database:** Set `DATABASE_URL` to the PostgreSQL connection string before starting
  the server. Example: `postgresql://user:password@host:5432/carportal`.
- **Schema management (DR-006):** Use `Base.metadata.create_all(bind=engine)` at startup
  for this feature. Alembic migrations are deferred to a follow-on task when schema
  evolution is first required.
- **Seed data (DR-007):** The `vehicles` table will be empty after `create_all`. For local
  development, insert a test row with:
  `INSERT INTO vehicles (make, model, year, price, transmission, fuel_type) VALUES ('Toyota', 'Corolla', 2022, '25000', 'automatic', 'petrol');`
  Populating the production database is an operational concern outside FR-001 scope.
- **CI/CD:** The pipeline gates deployment on `pytest test/test_vehicle.py -v` passing.
  The `DATABASE_URL` is not required for the test suite because the test overrides `get_db`
  with an in-memory SQLite engine.
- **Containerisation:** No container specification is mandated by the current requirements;
  a `Dockerfile` can be added as a follow-on task.

## Assumptions and Constraints

- The `vehicles` table does not pre-exist in the database; it will be created by
  `Base.metadata.create_all(bind=engine)` on first startup.
- The `id` column is an integer primary key auto-assigned by the database.
- All six required fields (make, model, year, price, transmission, fuel_type) are stored
  as non-nullable columns in the `vehicles` table.
- `app/db/database.py` does not currently exist in the source tree and must be created as
  a new file during implementation (DR-005). A compiled `.pyc` confirms prior existence
  but the source was not committed.
- `test/test_vehicle.py` does not currently exist in the source tree and must be created
  as a new file during implementation (DR-004). A compiled `.pyc` confirms prior existence
  but the source was not committed.
- The existing Pydantic `Vehicle` class in `models.py` (`name`, `category`, `link` fields)
  is not the live response schema and must be deleted before the SQLAlchemy ORM `Vehicle`
  class is added to resolve the naming collision (DR-003, closed decision).
- `get_vehicle_by_id(vehicle_id, db)` does not yet exist in `app/api/api.py` and must be
  added as a new function during implementation (DR-005).
- The existing dead-code `read_vehicle` function in `api.py` (JSON flat-file path) is not
  wired to any route and must be removed as a tracked implementation task (DR-010).
- Seed data for the `vehicles` table is out of scope for FR-001; the table will be empty
  after `create_all`. Automated tests use fixtures; a one-line SQL insert example is
  provided in the Deployment section for local development use (DR-007).
- The three existing legacy endpoints (`/user`, `/question`, `/alternatives`, `/answer`,
  `/result`) that read from `data/*.json` files are not modified by this feature.
- Authentication and authorisation are out of scope for this endpoint (confirmed in
  requirements out-of-scope section).
- The `DATABASE_URL` environment variable is available in every environment where the
  application runs.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation | Status |
| --- | --- | --- | --- | --- |
| `models.py` naming collision: existing Pydantic `Vehicle` class shadows the SQLAlchemy ORM `Vehicle` | High | High — ORM queries fail if the wrong class is resolved | **Resolved (DR-003):** Delete the Pydantic `Vehicle` class from `models.py` before adding the ORM class | Closed |
| `requirements.txt` missing `sqlalchemy` and `psycopg2-binary`; `fastapi==0.46.0` incompatible with Pydantic v2 | High (confirmed) | Critical — clean install cannot run ORM code; `from_attributes=True` silently broken | **Resolved (DR-001, DR-002):** Update `requirements.txt` as specified in Deployment section | Closed |
| `app/db/database.py` and `test/test_vehicle.py` source files absent | High (confirmed) | High — app fails to start; CI gate fails | **Resolved (DR-004, DR-005):** Both files must be created as new artefacts during implementation | Closed |
| `DATABASE_URL` not set in production environment | Medium | High — application fails to start or connects to wrong DB | Document required env vars; fail fast at startup with a clear error if `DATABASE_URL` is missing | Open |
| Schema drift between ORM model and actual DB table | Low | Medium — column mismatches cause runtime errors | Alembic migrations deferred (DR-006); `create_all` acceptable for FR-001 scope | Open |
| SQLite/PostgreSQL dialect differences mask bugs in tests | Low | Medium — tests pass but production fails on PostgreSQL-specific behaviour | Add an integration test stage that runs against a real PostgreSQL instance in CI (future iteration) | Open |
| `read_vehicle` dead code reactivated accidentally | Low | Medium — inconsistent data source for vehicle lookups | Remove dead code as a tracked implementation task (DR-010) | Open |

## Open Questions

- Is a `Dockerfile` or container specification required before the first deployment?
  (No container requirement exists in approved requirements; deferred unless user requests.)
- Should Alembic migrations be introduced when the first schema change is needed after
  FR-001 ships, or proactively as a separate follow-on task? (`create_all` is used for
  this feature per DR-006 decision.)
- Should a `GET /health` endpoint be added to support container orchestration probes?
  (DR-011, deferred to a future pipeline iteration.)

The following questions from the prior draft are now closed:
- `Base.metadata.create_all` vs Alembic for this feature: **closed — use `create_all`** (DR-006).
- Pydantic `Vehicle` class deletion: **closed — delete it** (DR-003).
- Seed data strategy: **closed — out of scope; SQL insert example provided** (DR-007).
