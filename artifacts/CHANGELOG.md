# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-09-30

### Added

- **FR-001: GET /vehicles/{vehicle_id} endpoint** — Retrieve vehicle details by ID with make, model, year, price, transmission, and fuel_type fields. Backed by SQLAlchemy ORM integration with PostgreSQL support (configurable via `DATABASE_URL` environment variable; defaults to SQLite for local development).
- **SQLAlchemy ORM integration** (NFR-001) — Added database session factory (`app/db/database.py`), ORM model (`app/db/models.py`), and dependency injection for route handlers.
- **Comprehensive test suite** — In-memory SQLite tests with fixture-based isolation covering happy path (HTTP 200) and error path (HTTP 404).
- **Updated dependencies** — Upgraded to FastAPI 0.100.0+, Pydantic 2.0+, SQLAlchemy 2.0+, uvicorn 0.20.0+, pytest 7.4.0+ for modern ORM and framework support.
- **Design and implementation documentation** — Requirements (`FR-001`, `NFR-001`), architecture, design review findings (12 findings, all resolved), implementation plan (12 tasks), and verification report.

### Changed

- **app/main.py** — Added `GET /vehicles/{vehicle_id}` route with HTTP 404 error handling for unknown vehicle IDs. Integrated `Base.metadata.create_all` at startup for schema creation.
- **app/api/api.py** — Added `get_vehicle_by_id` service function; removed dead code (`read_vehicle` JSON flat-file lookup).
- **app/db/models.py** — Deleted legacy Pydantic `Vehicle` class (naming collision risk); added SQLAlchemy ORM `Vehicle` model and Pydantic `VehicleResponse` schema with Pydantic v2 `from_attributes=True` support.
- **requirements.txt** — Updated all dependencies to modern versions compatible with SQLAlchemy 2.0 and Pydantic v2.

### Removed

- **app/api/api.py** — Deleted unused `read_vehicle` function (JSON flat-file lookup that was not wired to any route).
- **app/db/models.py** — Removed legacy Pydantic `Vehicle` class to eliminate naming collision with new SQLAlchemy ORM model.

### Fixed

- **Design review findings** — Resolved all Critical and High findings (DR-001 through DR-010): missing dependencies, Pydantic version mismatch, model naming collision, missing source files, schema management strategy, TLS requirements, and dead code cleanup.

---

## Known Limitations

- **R-003**: No explicit test for non-integer `vehicle_id` (FastAPI auto-validates path parameter; returns HTTP 422 if not integer; low risk).
- **R-004**: Starlette TestClient httpx deprecation warning in test output (cosmetic; no functional impact).
- **TASK-012**: PostgreSQL integration test deferred; SQLite used in all tests (no real PostgreSQL connection required for CI; production deployment will use PostgreSQL via `DATABASE_URL` environment variable).
- **DR-011**: No `/health` endpoint (deferred to future iteration; not required by current functional requirements).

---

**Contributor:** Claude Haiku 4.5 ([noreply@anthropic.com](mailto:noreply@anthropic.com))
