# Changelog

All notable changes to the Car Portal project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — Feature-Complete FR-001

### Added
- **FR-001:** Vehicle retrieval endpoint (GET /vehicles/{vehicle_id})
  - AC-001: Returns HTTP 200 with all 6 vehicle attributes (id, make, model, year, price, transmission, fuel_type)
  - AC-002: Returns HTTP 404 with error message for missing vehicles
  - Input validation: Path parameter must be positive integer (gt=0)
- **Logging:** Structured logging for retrieval attempts and errors (app/api/api.py)
- **Tests:** 21+ comprehensive tests covering success, error, and edge cases
- **Documentation:** API endpoint documentation and traceability matrix in README.md

### Changed
- **Dependencies (TASK-006):** Updated to modern versions
  - FastAPI >= 0.100.0 (was 0.46.0)
  - uvicorn >= 0.20.0 (was 0.11.1)
  - pytest >= 7.0 (was 5.3.2)

### Fixed
- **DR-001:** Data file mismatch — Created data/vehicles.json with correct schema
- **DR-003:** Vehicle ID type — Standardized on integer IDs across all layers
- **DR-004:** Missing endpoint — Wired GET /vehicles/{vehicle_id} in app/main.py
- **DR-005:** Validation constraints — Added Path(gt=0) to reject invalid IDs
- **DR-009:** Outdated dependencies — Updated to current stable versions

### Technical Details
- **Commits:** 0b111b6 (Phase 1), 0777116 (Phases 2-3)
- **Files changed:** app/main.py, app/api/api.py, app/db/models.py, test/test.py, requirements.txt, README.md, data/vehicles.json (created)
- **Test coverage:** 21/22 passing (1 pre-existing unrelated failure)
- **Type hints:** Full Pydantic v2 compatibility
- **Architecture:** Three-layer separation (Router/Service/Data)
