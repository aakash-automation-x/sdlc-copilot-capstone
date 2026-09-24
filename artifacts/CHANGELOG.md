# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- GET /vehicles/{vehicle_id} endpoint returns all six vehicle attributes (make, model, year, price, transmission, fuel_type) — FR-001
- HTTP 404 response with {"detail": "Vehicle not found"} for missing vehicle IDs — AC-002
- Content-Type: application/json response header — AC-003

### Changed
- Updated requirements.txt to Python 3.14-compatible dependency pins: fastapi==0.115.0, pydantic>=2.0.0,<3.0.0, sqlalchemy>=1.4.0,<2.0.0, uvicorn>=0.24.0, pytest>=7.0.0, requests>=2.28.0 — DD-001, DD-002
- Added type annotations to get_vehicle_by_id() — DR-007
- Replaced deprecated payload.dict() with payload.model_dump() — DR-008
- Updated test docstring traceability reference NFR-001 → AC-003 — DR-009
