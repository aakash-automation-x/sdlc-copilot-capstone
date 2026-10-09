# Design Review

## Review Summary

The proposed architecture for FR-001 (`GET /vehicles/{vehicle_id}`) is sound in its three-layer
separation, dependency-injection pattern, and test-isolation strategy. However, a cross-cutting
audit of the actual codebase against the architecture document reveals four blocking issues that
must be resolved before coding begins:

1. `requirements.txt` is missing `sqlalchemy` and `psycopg2-binary` — the entire ORM code path
   cannot be installed or executed without these packages.
2. `fastapi==0.46.0` bundles Pydantic v1, which does not support `from_attributes=True`. The
   architecture specifies Pydantic v2 syntax; `requirements.txt` must be updated to match.
3. The existing Pydantic `Vehicle` class in `models.py` carries incompatible fields
   (`name`, `category`, `link`) and will shadow the incoming SQLAlchemy ORM `Vehicle` class
   unless it is removed before implementation begins.
4. Both `app/db/database.py` and `test/test_vehicle.py` are absent from the source tree
   (compiled `.pyc` artefacts exist, confirming they were once present). The architecture must
   make explicit that these are new files to be created, not modifications to existing files.

All Critical and High findings have agreed decisions recorded below. Once those decisions are
applied, the architecture is ready for the Planner Agent (Step 4).

## Review Inputs

- `artifacts/architecture.md` — commit `6ca3de8`
- `artifacts/requirements.md` — commit `65ab0f7`
- Live codebase files inspected: `app/main.py`, `app/api/api.py`, `app/db/models.py`,
  `requirements.txt`, `test/test.py`; absent source files confirmed by `.pyc` evidence:
  `app/db/database.py`, `test/test_vehicle.py`

## Findings

| ID | Severity | Area | Finding | Impact | Recommendation | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DR-001 | Critical | Deployment / CI-CD | `requirements.txt` contains neither `sqlalchemy` nor `psycopg2-binary`. Current pins: `fastapi==0.46.0`, `uvicorn==0.11.1`, `pytest==5.3.2`, `requests==2.22.0` only. | A clean install from `requirements.txt` produces an environment where `from sqlalchemy import …` fails. Every ORM import, test, and production startup call fails immediately. Relates to NFR-001. | Add `sqlalchemy>=2.0.0` and `psycopg2-binary>=2.9.0` to `requirements.txt`. Update `fastapi`, `uvicorn`, `pydantic`, and `pytest` to versions consistent with Decision 2. | Update `requirements.txt` to include `sqlalchemy>=2.0.0`, `psycopg2-binary>=2.9.0`, `pydantic>=2.0.0`, `fastapi>=0.100.0`, `uvicorn>=0.20.0`, `pytest>=7.4.0`, `requests>=2.28.0`. Implementation Agent owns this change. | Resolved |
| DR-002 | High | Technology choices | Architecture specifies `VehicleResponse` with `from_attributes=True`, which is Pydantic v2 syntax. `fastapi==0.46.0` pins Pydantic v1, where the equivalent config key is `orm_mode = True`. Using `from_attributes=True` under Pydantic v1 silently has no effect, breaking ORM-to-schema serialisation. | `VehicleResponse.from_orm(vehicle)` returns empty or raises `ValidationError` under Pydantic v1 when `orm_mode` is not set, making every `GET /vehicles/{vehicle_id}` response incorrect. Relates to FR-001, NFR-001. | Pick a Pydantic version (v1 or v2) and apply it consistently in `requirements.txt`, `models.py`, and the architecture document. The development environment evidence (`.pyc` files compiled with Python 3.14 and pytest 9.1.1) confirms a modern runtime is in use; Pydantic v2 is the correct target. | Standardise on **Pydantic v2** (`pydantic>=2.0.0`). Use `from_attributes=True` in `VehicleResponse` as the architecture specifies. Requires `fastapi>=0.100.0` (DR-001 covers the `requirements.txt` update). Architecture technology-choices table updated to record this decision. | Resolved |
| DR-003 | High | Components / Data layer | The current `app/db/models.py` contains a single Pydantic `Vehicle` class with fields `id`, `name`, `make`, `model`, `year`, `price`, `transmission`, `fuel_type`, `category`, `link`. This class has a different field set and schema than FR-001 requires, and will shadow any SQLAlchemy ORM class also named `Vehicle` added to the same module. The architecture identifies this risk but does not close the decision. | If implementation adds the SQLAlchemy ORM `Vehicle` before or after the existing Pydantic `Vehicle`, one will shadow the other, causing ORM queries or response serialisation to resolve to the wrong type at runtime. Relates to FR-001. | Explicitly close the open question: delete the existing Pydantic `Vehicle` class from `models.py`. Retain `Answer` and `UserAnswer`. The SQLAlchemy ORM `Vehicle` and the `VehicleResponse` Pydantic schema are the two vehicle-related classes that belong in `models.py`. | **Decision: Delete the Pydantic `Vehicle` class** from `models.py`. Add SQLAlchemy ORM `Vehicle` (`__tablename__ = "vehicles"`, columns: `id`, `make`, `model`, `year`, `price`, `transmission`, `fuel_type`) and Pydantic `VehicleResponse` with `from_attributes=True`. Architecture Risks table and Open Questions updated to reflect this closed decision. | Resolved |
| DR-004 | High | Testability | `test/test_vehicle.py` source file is absent from the repository. A compiled `.pyc` in `test/__pycache__/` (`test_vehicle.cpython-314-pytest-9.1.1.pyc`) confirms the file existed previously but was not committed or was deleted. The architecture references this file as the in-memory SQLite test isolation pattern without noting it must be created. | The CI gate `pytest test/test_vehicle.py -v` will fail with a collection error, blocking deployment. Acceptance criterion AC-001 cannot be verified. | Add explicit task in the implementation plan to create `test/test_vehicle.py` with an in-memory SQLite engine, a `get_db` dependency override, an `autouse` fixture that creates/drops the schema and seeds one `Vehicle` row, and tests for the happy path (HTTP 200) and the not-found path (HTTP 404). | Create `test/test_vehicle.py` as a new file. Architecture Assumptions section updated to state explicitly that both `app/db/database.py` and `test/test_vehicle.py` are new files to be created during implementation. | Resolved |
| DR-005 | Medium | Components | `app/db/database.py` source file is absent (`.pyc` confirms prior existence). Similarly, `get_vehicle_by_id(vehicle_id, db)` in `app/api/api.py` does not exist yet. The architecture describes both as existing components, which could cause the Planner Agent to treat them as modifications rather than creations. | Implementation tasks may under-specify the work required. Missing `database.py` causes all ORM imports to fail at startup. | Architecture Assumptions section should explicitly list `database.py` and `get_vehicle_by_id` as items to be created, not modified. | Architecture updated to list both items as new artefacts. Planner Agent is the owner of creating explicit creation tasks. | Resolved |
| DR-006 | Medium | Deployment / CI-CD | The open question "Should `Base.metadata.create_all` be kept for production startup, or should Alembic migrations be introduced now?" is unresolved in the architecture. | Deferred ambiguity translates to an un-specified implementation task. A planner choosing the wrong option can introduce schema-management complexity outside the current feature scope. | Close the question: use `Base.metadata.create_all(bind=engine)` at startup for this iteration. Alembic is out of scope for FR-001 but must be logged as a follow-on task. | **Decision: Use `Base.metadata.create_all` for this feature.** Add Alembic introduction as a deferred item in the Open Questions section of the architecture. Architecture Deployment section updated. | Resolved |
| DR-007 | Medium | Deployment / CI-CD | No seed data strategy exists for the `vehicles` table in development or production environments. The in-memory SQLite test seeds one row via a fixture, but the actual PostgreSQL table will be empty after `create_all`. AC-001 cannot be manually verified without at least one vehicle row. | Manual and end-to-end acceptance testing of FR-001 is blocked until a vehicle row is inserted. Automated tests are unaffected because they use fixtures. | Clarify that populating the `vehicles` table is an operational concern outside FR-001 scope. Document a minimal SQL snippet or management command for inserting a test row. | **Decision: Seed data is out of scope for FR-001.** The `test/test_vehicle.py` fixture satisfies automated verification of AC-001. A one-line SQL insert example shall be documented in the implementation plan for local development use. Architecture Assumptions section updated. | Resolved |
| DR-008 | Medium | Security | The architecture's Deployment section does not mention HTTPS/TLS. The `DATABASE_URL` environment variable contains credentials and is transmitted over HTTP if TLS is not enforced. | Credentials exposed in transit if the app is accessed without TLS. Relates to OWASP A02 (Cryptographic Failures). | Add a note to the Deployment section stating that production deployments must terminate TLS at the load-balancer or reverse-proxy layer (e.g., Nginx, AWS ALB) and that plain HTTP must not be exposed externally. | Architecture Deployment section updated with TLS note. | Resolved |
| DR-009 | Low | Technology choices | NFR-001 mandates Python 3.8+. Python 3.8 reached end-of-life in October 2024. Running production workloads on an EOL Python version is a security risk (no security patches). The compiled `.pyc` files in the repository confirm Python 3.14 is in active use. | Security vulnerabilities introduced in Python ≤ 3.8 will not receive patches. | Update the architecture's technology table to recommend Python 3.11+ as the minimum runtime, while keeping the NFR-001 constraint as-is until the requirement is formally changed. | Architecture technology-choices table note added. NFR-001 is not changed (requires a requirements update in a subsequent pipeline run). | Resolved |
| DR-010 | Low | Maintainability | `read_vehicle(vehicle_id)` in `app/api/api.py` is dead code (not wired to any route). The architecture notes it should be removed but does not track this as an explicit implementation task. | Dead code is a maintenance burden and a latent security risk if accidentally activated (it reads from `cars.json` which does not contain the FR-001 field schema). | Add a discrete task in `impl-plan.md` to delete `read_vehicle` and its import of `Optional` and `Dict` from `typing` if no longer needed. | Add explicit dead-code removal task to implementation plan. | Resolved |
| DR-011 | Low | Observability | No `/health` or `/ready` endpoint is defined. Load balancers, container orchestrators, and monitoring systems typically require a health probe. | Deployment to container platforms (Docker, Kubernetes) or cloud load balancers will fail health checks or not be configurable without a health endpoint. | Add a `GET /health` endpoint returning `{"status": "ok"}` as a low-effort, low-risk addition. Out of scope for FR-001 but worth tracking for the next iteration. | Deferred to a future pipeline iteration. Recorded in Open Questions. | Deferred |
| DR-012 | Low | Scalability | SQLAlchemy default connection pool (`QueuePool`, `pool_size=5`, `max_overflow=10`) is not documented in the architecture. Tuning guidance is mentioned but no defaults are stated. | Under-configured pool limits may cause request queuing or `TimeoutError` under moderate load; over-configured pool may exhaust database connections. | Document the SQLAlchemy pool defaults in the architecture's Scalability section so operators have a starting point. | Architecture Scalability section updated with default pool parameters. | Resolved |

## Agreed Design Decisions

| Decision | Rationale | Owner |
| --- | --- | --- |
| Update `requirements.txt`: add `sqlalchemy>=2.0.0`, `psycopg2-binary>=2.9.0`; update `fastapi>=0.100.0`, `pydantic>=2.0.0`, `uvicorn>=0.20.0`, `pytest>=7.4.0`, `requests>=2.28.0` | The current `requirements.txt` makes a clean install non-functional for ORM work. Development environment evidence confirms a modern runtime is already in use. Closes DR-001 and DR-002. | Implementation Agent |
| Standardise on Pydantic v2: use `from_attributes=True` in `VehicleResponse` | Consistent with the architecture document and the active development environment. Avoids split-brain between documented and actual behaviour. Closes DR-002. | Implementation Agent |
| Delete the existing Pydantic `Vehicle` class from `models.py`; add SQLAlchemy ORM `Vehicle` and Pydantic `VehicleResponse` | Eliminates the naming collision that would cause ORM queries or schema serialisation to resolve to the wrong class. The deleted class is not referenced by any live route. Closes DR-003. | Implementation Agent |
| Create `app/db/database.py` as a new file (not a modification) | Source file is absent. Planner Agent must create an explicit creation task. Closes DR-004 and DR-005. | Planner Agent |
| Create `test/test_vehicle.py` as a new file with in-memory SQLite, `get_db` override, autouse fixture, happy-path and not-found tests | Source file is absent; CI gate depends on it. Closes DR-004. | Implementation Agent |
| Use `Base.metadata.create_all` at startup; defer Alembic to a future iteration | Alembic adds tooling complexity beyond the scope of FR-001. `create_all` is safe when the table does not pre-exist. Closes DR-006. | Planner Agent |
| Seed data is out of scope for FR-001; document a one-line SQL insert example for local development | Automated tests use fixtures. Manual testing requires a single row; a documented insert command is sufficient. Closes DR-007. | Planner Agent |
| Track `read_vehicle` dead-code removal as an explicit implementation task | Prevents accidental reactivation of the JSON flat-file path and keeps the codebase clean. Closes DR-010. | Planner Agent |

## Rejected or Deferred Findings

| ID | Finding | Rationale |
| --- | --- | --- |
| DR-011 | No `/health` endpoint | Out of scope for FR-001. No requirement exists. Deferred to a future feature iteration. |

## Required Architecture Updates

The following changes are applied to `artifacts/architecture.md` to reflect resolved findings:

1. **Technology choices table** — Add row for Pydantic specifying `pydantic>=2.0.0` and
   `from_attributes=True`. Add row for SQLAlchemy specifying `sqlalchemy>=2.0.0`. Add note to
   Python row recommending 3.11+ runtime even though NFR-001 states 3.8+ minimum.
2. **Deployment section** — Replace the open question about `Base.metadata.create_all` vs
   Alembic with a firm decision: use `create_all` for this feature; Alembic is deferred.
   Add `requirements.txt` update as an explicit deployment prerequisite. Add TLS note.
   Add SQLAlchemy default pool parameters (`pool_size=5`, `max_overflow=10`) to Scalability.
3. **Assumptions and Constraints** — Add: "`app/db/database.py` does not currently exist and
   must be created." Add: "`test/test_vehicle.py` does not currently exist and must be created."
   Add: "Seed data for the `vehicles` table is out of scope; the table will be empty after
   `create_all`."
4. **Risks and Mitigations table** — Change status of naming-collision row from open risk to
   resolved: "Resolved — delete Pydantic `Vehicle` class (DR-003)."
5. **Open Questions** — Remove the two questions that are now closed (Alembic, Pydantic Vehicle
   class). Retain the Docker/container question as still open. Add `/health` endpoint and Alembic
   introduction as deferred items.

## Open Questions

- Should a `Dockerfile` or container specification be added before the first deployment?
  (No container requirement exists in the current approved requirements; defer unless user
  requests it.)
- Should a `GET /health` endpoint be added to support container orchestration health probes?
  (DR-011, deferred to a future iteration.)
- Should Alembic migrations be introduced when the first schema change is needed after FR-001
  ships, or proactively as a separate follow-on task?

## Readiness Recommendation

Ready for planning — no unresolved Critical or High findings remain. All eight resolved findings
have agreed decisions. Proceed to the Planner Agent (Step 4) to break this architecture into
discrete implementation tasks in `artifacts/impl-plan.md`.
