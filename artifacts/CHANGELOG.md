# Changelog

All notable changes to this project are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-09-23

### Added

- **`GET /vehicles/{vehicle_id}` endpoint** (FR-001) — Retrieves vehicle details by ID from a
  PostgreSQL database (via SQLAlchemy ORM), returning `make`, `model`, `year`, `price`,
  `transmission`, and `fuel_type`. Returns HTTP 404 when the vehicle ID does not exist.
- `app/db/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, and `get_db` dependency
  with `try/finally` session lifecycle management.
- `test/test_vehicle.py` — Two pytest tests covering the happy path (all 6 AC-001 fields
  asserted) and the Not Found path (HTTP 404), using an in-memory SQLite database with
  `StaticPool` for test isolation.

### Changed

- `app/db/models.py` — Added `Vehicle` SQLAlchemy ORM model (`vehicles` table) and
  `VehicleResponse` Pydantic schema (Pydantic v2 `ConfigDict(from_attributes=True)`).
- `app/api/api.py` — Added `get_vehicle_by_id(vehicle_id, db)` function.
- `app/main.py` — Added `GET /vehicles/{vehicle_id}` route with FastAPI dependency injection
  and HTTP 404 guard. Existing routes unchanged.
- `requirements.txt` — Added `sqlalchemy>=1.3.0,<2.0.0` and `psycopg2-binary`.

### SDLC Artifacts Added

- `artifacts/requirements.md` — FR-001, AC-001
- `artifacts/architecture.md` — System design, component diagram, column schema
- `artifacts/design-review.md` — 6 design decisions (DR-001 to DR-006)
- `artifacts/impl-plan.md` — 8 dependency-ordered implementation tasks
- `artifacts/ORCHESTRATION_LOG.md` — Full 8-step pipeline execution log

### Traceability

| User Story | Requirement | Acceptance Criterion | Endpoint | Test |
|------------|-------------|----------------------|----------|------|
| `userstory.md` | FR-001 | AC-001 | `GET /vehicles/{vehicle_id}` | `test_get_vehicle_by_id_success`, `test_get_vehicle_by_id_not_found` |
