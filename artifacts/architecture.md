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
| Language | Python 3.8+ | Mandated by NFR-001; matches existing codebase | Minimum version 3.8 limits some newer typing syntax |
| Web framework | FastAPI | Mandated by NFR-001; provides automatic OpenAPI docs, async support, Pydantic integration, and dependency injection | Smaller ecosystem than Django; async not used in current sync handlers |
| ORM | SQLAlchemy | Mandated by NFR-001; industry standard Python ORM; portable across DB backends | Adds abstraction overhead; requires migration tooling (e.g. Alembic) for schema changes |
| Production database | PostgreSQL | Mandated by NFR-001; ACID-compliant, production-grade, supported by SQLAlchemy | Requires a running PostgreSQL instance; not bundled with the app |
| Test database | SQLite (in-memory) | No server required; fast; isolated per test via dependency override; matches existing project test pattern | SQLite dialect differences may hide PostgreSQL-specific bugs |
| Response schema | Pydantic `VehicleResponse` with `from_attributes=True` | Decouples ORM internals from API surface; enables field-level validation and OpenAPI schema generation | Must stay in sync with ORM model column names |
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
- The bottleneck under load is the PostgreSQL connection pool. SQLAlchemy's default pool
  size should be tuned to match the deployment environment's database connection limits.

## Deployment

- **Runtime:** Python 3.8+ with dependencies listed in `requirements.txt`.
- **Server:** `uvicorn app.main:app --reload` for development; a production deployment
  should use `gunicorn -k uvicorn.workers.UvicornWorker` with multiple workers.
- **Database:** Set `DATABASE_URL` to the PostgreSQL connection string before starting
  the server. Example: `postgresql://user:password@host:5432/carportal`.
- **Schema management:** Run `Base.metadata.create_all(bind=engine)` at startup (current
  approach) or use Alembic migrations (recommended for production schema evolution).
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
  as non-nullable columns in the `vehicles` table; the existing Pydantic-only `Vehicle`
  class in `models.py` with optional fields is not the live response schema.
- The existing dead-code `read_vehicle` function in `api.py` (JSON flat-file path) is not
  wired to any route and will not be activated as part of this feature. It may be removed
  in a follow-on cleanup task.
- The three existing legacy endpoints (`/user`, `/question`, `/alternatives`, `/answer`,
  `/result`) that read from `data/*.json` files are not modified by this feature.
- Authentication and authorisation are out of scope for this endpoint (confirmed in
  requirements out-of-scope section).
- The `DATABASE_URL` environment variable is available in every environment where the
  application runs.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| `models.py` naming collision: a second Pydantic class named `Vehicle` shadows the SQLAlchemy ORM `Vehicle` at module scope | High (already present) | High — ORM queries fail if the wrong class is imported | Rename the existing Pydantic `Vehicle` class or remove it; keep only the SQLAlchemy ORM `Vehicle` and the `VehicleResponse` Pydantic schema |
| `DATABASE_URL` not set in production environment | Medium | High — application fails to start or connects to wrong DB | Document required env vars; fail fast at startup with a clear error if `DATABASE_URL` is missing |
| Schema drift between ORM model and actual DB table | Low | Medium — column mismatches cause runtime errors | Introduce Alembic migrations before production deployment |
| SQLite/PostgreSQL dialect differences mask bugs in tests | Low | Medium — tests pass but production fails on PostgreSQL-specific behaviour | Add an integration test stage that runs against a real PostgreSQL instance in CI |
| `read_vehicle` dead code reactivated accidentally | Low | Medium — inconsistent data source for vehicle lookups | Remove dead code as a tracked clean-up task in `impl-plan.md` |

## Open Questions

- Should `Base.metadata.create_all` be kept for production startup, or should Alembic
  migrations be introduced now? (Alembic is safer but adds tooling complexity.)
- Should the `vehicles` table be pre-populated with seed data, and if so, by what
  mechanism (migration script, fixture, or manual insert)?
- Is a `Dockerfile` or container specification required before the first deployment?
- Should the existing Pydantic `Vehicle` class in `models.py` be deleted or retained for
  any other purpose? (Current assessment: delete it to resolve the naming collision.)
