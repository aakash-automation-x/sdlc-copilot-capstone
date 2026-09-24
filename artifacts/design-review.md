# Design Review — Car Portal: Get Vehicle Details

**Review date:** 2026-09-24
**Reviewer:** Design Review Agent (Step 3 of 8)
**Status:** Complete — see readiness recommendation at the end.

---

## Review Summary

The architecture for `GET /vehicles/{vehicle_id}` is sound in its layered structure, data flow, and HTTP contract. All six required attributes are accounted for, the 404 path is correctly designed, and the three-layer separation is appropriate for the scope. However, **three High findings block a clean production implementation**:

1. The pinned `fastapi==0.46.0` is incompatible with the Pydantic v2 syntax already used in the code.
2. The SQLAlchemy version constraint (`>=1.3.0`) permits an install of 1.3.x, where the `declarative_base` import path used in the code does not exist.
3. The active Python runtime (Python 3.14, inferred from `__pycache__` bytecode naming) is incompatible with every 2020-era pinned dependency in `requirements.txt`.

These three findings share a common fix: modernise the dependency pins. Two Medium findings — the 404 path missing from requirements.md and an incorrect architecture assumption about input validation — require documentation updates rather than code changes.

All findings, decisions, and required file updates are documented below.

---

## Review Inputs

| Artifact | Path | Commit |
|---|---|---|
| Architecture under review | `artifacts/architecture.md` | `0585e36` (updated `f96ddcd`) |
| Approved requirements | `artifacts/requirements.md` | `3d269da` |
| Router layer | `app/main.py` | working tree |
| Service layer | `app/api/api.py` | working tree |
| Data / ORM layer | `app/db/models.py` | working tree |
| DB session provider | `app/db/database.py` | working tree |
| Tests | `test/test_vehicle.py` | working tree |
| Dependency manifest | `requirements.txt` | working tree |

---

## Findings

### Findings Table

| ID | Severity | Area | Finding | Impact | Recommendation | Decision | Status |
|---|---|---|---|---|---|---|---|
| DR-001 | High | Dependency Compatibility | `fastapi==0.46.0` (Jan 2020) requires Pydantic v1. The code uses Pydantic v2 syntax (`ConfigDict`, `from_attributes=True`). Pydantic is absent from `requirements.txt` — pip will install whatever FastAPI 0.46.0 requests (Pydantic v1), and the application will fail at startup with `ImportError: cannot import name 'ConfigDict' from 'pydantic'`. Risk R-001 from the architecture is confirmed live and unresolved. | App fails to start on a clean install. | Upgrade FastAPI to `>=0.100.0` (first version with Pydantic v2 support) and add `pydantic>=2.0.0,<3.0.0` explicitly to `requirements.txt`. Update architecture Technology Choices table accordingly. | **Accepted — upgrade to FastAPI 0.115.0 (stable, widely used) with Pydantic v2.** Update `requirements.txt` and `architecture.md`. | Open |
| DR-002 | High | Dependency Compatibility | `app/db/database.py` uses `from sqlalchemy.orm import declarative_base`. This import path was introduced in SQLAlchemy 1.4. The `requirements.txt` constraint `>=1.3.0,<2.0.0` permits resolution to SQLAlchemy 1.3.x where this import does not exist. | App fails to start if SQLAlchemy 1.3.x is installed. | Tighten to `sqlalchemy>=1.4.0,<2.0.0`. | **Accepted — update lower bound to 1.4.0. Update `requirements.txt` and architecture.** | Open |
| DR-003 | High | Runtime Compatibility | `__pycache__` bytecode files show `cpython-314`, confirming Python 3.14 as the active interpreter. FastAPI 0.46.0, uvicorn 0.11.1, pytest 5.3.2, and requests 2.22.0 all predate Python 3.12 and have no confirmed Python 3.14 support. `pip install -r requirements.txt` is expected to fail on Python 3.14. | Blocks install and CI on the active runtime. Shares a common fix with DR-001. | Modernise all dependency pins to versions known to support Python 3.14 (aligns with DR-001 fix). Also add a `python_requires` note or a `.python-version` file. | **Accepted — dependency upgrade for DR-001 implicitly resolves this. Add minimum Python version note to architecture.** | Open |
| DR-004 | Medium | Requirements Completeness | `requirements.md` explicitly scopes out "Error handling beyond the happy path." The architecture adds a 404 response for missing IDs, and `test_vehicle.py` tests `AC-002` (404) and `AC-003` (content-type). Neither AC-002 nor AC-003 is defined in `requirements.md`. | Traceability gap: the tests verify acceptance criteria that are not formally in scope. | Add AC-002 ("When a vehicle ID that does not exist is provided, the system shall return HTTP 404 with `{"detail": "Vehicle not found"}`.") and AC-003 ("The response Content-Type shall be `application/json`.") to `requirements.md`. | **Accepted — 404 for a missing resource is an implied requirement of any retrieve-by-ID operation. AC-002 and AC-003 are added to `requirements.md`.** | Open |
| DR-005 | Medium | API Contract Accuracy | Architecture assumption A-002 states "`vehicle_id` is always a positive integer; FastAPI path parameter parsing enforces this." FastAPI type coercion only guarantees an integer; it does not reject zero or negative values. A request for `GET /vehicles/0` or `GET /vehicles/-5` passes validation and reaches the service, returning a 404 (no row found). The assumption misrepresents what is enforced. | Misleading documentation; may cause confusion during testing. | Either add a `Path(..., gt=0)` constraint to the route, or update A-002 to accurately state that only integer type is enforced and non-positive IDs receive a 404. | **Accepted — update A-002 to state that FastAPI enforces integer type only; non-positive IDs return 404 via DB miss. Adding `gt=0` is deferred as a future hardening item.** | Open |
| DR-006 | Medium | Data Integrity | `VehicleResponse` declares `price: float`. SQLAlchemy returns PostgreSQL `Numeric(12,2)` as `decimal.Decimal`. Pydantic v2 coerces `Decimal` to `float`. IEEE-754 float can introduce rounding error on some values. The test uses `pytest.approx`, which masks this. The architecture documents this as A-003 but without formal product acceptance. | Prices may display extra decimal places in some consumers. Low risk for a read-only display feature. | Formally accept A-003. If precision becomes a consumer issue, the fix is confined to `VehicleResponse` (change `price: float` to `price: Decimal` and add `from decimal import Decimal` import). | **Accepted — A-003 formally accepted. Float precision is adequate for display. Fix path documented.** | Accepted |
| DR-007 | Low | Code Quality | `get_vehicle_by_id(vehicle_id: int, db)` in `app/api/api.py` lacks a type hint for `db` and has no return type annotation. | Reduces static analysis and IDE support. | Add `db: Session` and `-> Optional[Vehicle]` annotations. | **Accepted — implement during coding step.** | Note for implementation |
| DR-008 | Low | Code Quality | `app/main.py` line 40 calls `payload.dict()`, the Pydantic v1 method deprecated in v2 (replaced by `model_dump()`). Not in the vehicle feature, but in the same module. | Generates `PydanticDeprecatedSince20` deprecation warnings after the v2 upgrade. | Replace with `payload.model_dump()` when upgrading to Pydantic v2. | **Accepted — fix during the same implementation pass as DR-001.** | Note for implementation |
| DR-009 | Low | Traceability | `test_vehicle.py` references `AC-002` and `NFR-001` in docstrings. AC-002 is resolved by DR-004. `NFR-001` (content-type check) is not defined anywhere in requirements. | Minor traceability gap in the test docstring. | Accept AC-003 added via DR-004 as the formal home for the content-type check; update the test docstring from `NFR-001` to `AC-003`. | **Accepted — update test docstring during implementation.** | Note for implementation |

---

## Agreed Design Decisions

| Decision ID | Decision | Rationale | Affected Artifacts |
|---|---|---|---|
| DD-001 | Upgrade FastAPI to `0.115.0` and add `pydantic>=2.0.0,<3.0.0` to `requirements.txt` | Resolves the Pydantic v1/v2 conflict (DR-001) and the Python 3.14 incompatibility (DR-003). FastAPI 0.115.x is a stable, widely deployed release with full Pydantic v2 support. | `requirements.txt`, `artifacts/architecture.md` |
| DD-002 | Tighten SQLAlchemy lower bound to `>=1.4.0,<2.0.0` | Guarantees `from sqlalchemy.orm import declarative_base` is always available (DR-002). | `requirements.txt`, `artifacts/architecture.md` |
| DD-003 | Formally add AC-002 (404 not-found) and AC-003 (JSON content-type) to `requirements.md` | Makes the 404 contract and content-type expectation first-class, traceable requirements rather than undocumented behaviour (DR-004). | `artifacts/requirements.md` |
| DD-004 | Update A-002 to reflect that FastAPI enforces integer type only; non-positive IDs return 404 | Corrects a misleading architecture assumption (DR-005) without introducing a scope-creep constraint. | `artifacts/architecture.md` |
| DD-005 | Formally accept A-003 (float price serialisation) | Price precision adequate for display consumers; fix path documented for future if needed (DR-006). | `artifacts/architecture.md` |

---

## Deferred / Rejected Findings

| Finding | Disposition | Rationale |
|---|---|---|
| Positive-integer `Path(gt=0)` constraint | Deferred | Not in scope for MVP; the 404 response for non-positive IDs is acceptable. Document A-002 accurately instead. |
| Alembic migration tooling | Deferred | Captured as R-003 in architecture; out of scope for this story. |
| Structured logging / tracing | Deferred | Uvicorn access logs sufficient for MVP per architecture Observability section. |
| Auth/authorisation | Deferred | Explicitly out of scope per FR-001 and C-003. |

---

## Required Updates to Architecture.md

The following changes are applied immediately:

1. **Technology Choices table** — Update FastAPI version from `0.46.0 (pinned)` to `0.115.0 (pinned, Pydantic v2-compatible)`; add explicit Pydantic v2 row; update SQLAlchemy lower bound from `1.3.0` to `1.4.0`; add Python ≥ 3.10 requirement note.
2. **Risk R-001** — Mark as resolved; record the decision (FastAPI upgrade to 0.115.0 + explicit Pydantic v2).
3. **Assumption A-002** — Correct wording: FastAPI enforces integer type only; non-positive IDs return 404 via DB miss.
4. **Open Question OQ-001** — Mark resolved: Pydantic v2 is used; FastAPI must be upgraded to match.

---

## Required Updates to Requirements.md

1. Add **AC-002**: "When a vehicle ID that does not exist is provided, the system shall return HTTP 404 with body `{"detail": "Vehicle not found"}`."
2. Add **AC-003**: "The response Content-Type shall be `application/json`."
3. Remove "Error handling beyond the happy path" from the Out of Scope list, or qualify it to clarify that the 404 contract is now in scope.

---

## Open Questions and Follow-up Actions

| ID | Question / Action | Owner | Priority |
|---|---|---|---|
| FA-001 | Update `requirements.txt`: `fastapi==0.115.0`, `pydantic>=2.0.0,<3.0.0`, `uvicorn>=0.24.0`, `sqlalchemy>=1.4.0,<2.0.0`, `pytest>=7.0.0`, `requests>=2.28.0`. | Implementation Agent | High |
| FA-002 | Add type annotations to `get_vehicle_by_id` per DR-007. | Implementation Agent | Low |
| FA-003 | Replace `payload.dict()` with `payload.model_dump()` per DR-008. | Implementation Agent | Low |
| FA-004 | Update `test_vehicle.py` docstring: `NFR-001 / AC-003` → `AC-003`. | Implementation Agent | Low |
| OQ-002 | Is there an Alembic migration or seeding script for the `vehicles` table? (Carried from architecture OQ-002.) | Planner Agent | Medium |
| OQ-003 | Should `vehicle_id` ever be returned in the response? (Carried from architecture OQ-003.) | Product | Low |

---

## Readiness Recommendation

**Ready to proceed to planning and implementation with conditions.**

The three High findings (DR-001, DR-002, DR-003) share a single fix: modernise the dependency pins (see DD-001 and DD-002). The architecture updates and requirements additions (DR-004, DR-005) are documentation-only changes applied in this review. No architectural redesign is required.

The Planner Agent and Implementation Agent must ensure `requirements.txt` is updated per FA-001 before any test run, as the current pins will cause an import-time failure on the active Python 3.14 runtime.

All structural design decisions (three-layer architecture, single endpoint, SQLite/PostgreSQL duality, 404 contract, six-attribute response model, `id` exclusion) are sound and approved.
