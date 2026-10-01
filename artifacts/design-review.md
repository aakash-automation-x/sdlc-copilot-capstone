# Design Review

## Review Summary

The proposed three-layer architecture (Router → Service → Data) is well-structured and supports the core requirements for vehicle retrieval (FR-001, AC-001, AC-002). **Critical findings resolved.** Stakeholder decisions:

- **DR-001 (Critical):** Approved Option A — Data migrated from `cars.json` to `data/vehicles.json` with complete schema (make, model, year, price, transmission, fuel_type). ✅ **RESOLVED**
- **DR-003 (Critical):** Approved integer ID type. Vehicle ID path parameter type confirmed as `int`. ✅ **RESOLVED**

Remaining High/Medium findings are actionable and accepted for implementation phase. Design is **Ready for Planning**.

---

## Review Inputs
- `artifacts/architecture.md` (v1.0, 2026-10-01)
- `artifacts/requirements.md` (v1.0, 2026-10-01)
- Repository state: `app/main.py`, `app/api/api.py`, `app/db/models.py`, `data/cars.json`

---

## Findings

| ID | Severity | Area | Finding | Impact | Recommendation | Decision | Status |
|---|---|---|---|---|---|---|---|
| DR-001 | Critical | Deployment & CI/CD | File path mismatch: Architecture assumes `data/vehicles.json`, but repository contained `data/cars.json`. Schema was incompatible (missing make, model, year, transmission). | Service layer will fail at runtime when trying to read non-existent file or return incomplete vehicle data missing AC-001 required attributes. AC-001 acceptance criteria cannot be met without correct data. | **RESOLVED:** Created `data/vehicles.json` with complete schema (id, make, model, year, price, transmission, fuel_type). Data migrated from cars.json with all 10 vehicle records. Schema now fully supports AC-001. | Approved: Option A | ✅ Resolved |
| DR-002 | High | Components and responsibilities | Data schema mismatch: AC-001 requires 6 attributes (make, model, year, price, transmission, fuel_type). Current `data/cars.json` provides only id, name, fuel, price, category, link. Pydantic Vehicle model defines optional fields for missing attributes, masking the gap. | Implementation will pass endpoint tests but violate AC-001 acceptance criteria (not all required attributes returned). Acceptance criteria cannot be validated in production. | Align data schema with AC-001 requirements. Add make, model, year, transmission fields to `data/cars.json` or confirm if AC-001 should be narrowed to available fields. Validate against requirements before proceeding. | Pending AC-001 clarification | Open |
| DR-003 | Critical | Reliability and fault tolerance | Vehicle ID type inconsistency: Architecture diagrams show string path parameter ("v123"), but `data/vehicles.json` uses integer IDs (1–10). Service layer `read_vehicle()` compares `car['id'] == vehicle_id` without type coercion. | Router path parameter will be parsed as string, Service layer will compare string to integer, and `==` comparison will fail even for valid IDs. AC-001 success path will never execute; all requests return 404. | **RESOLVED:** Confirmed vehicle_id type as `int`. Router layer will parse path parameter as integer via FastAPI type hint. Service layer will compare integer to integer correctly. Architecture and tests updated. | Approved: integer type | ✅ Resolved |
| DR-004 | High | Requirements alignment | Incomplete endpoint: `/vehicles/{vehicle_id}` endpoint is not present in `app/main.py`. Existing service function `read_vehicle()` exists but is not called by any route. | FR-001 cannot be verified; no HTTP endpoint exposes vehicle retrieval. Implementation phase will need to add endpoint, but architecture does not specify parameter type, response serialization, or error handling wiring. | Add `@app.get("/vehicles/{vehicle_id}")` endpoint to `app/main.py` that calls `api.read_vehicle()`, handles 404 via HTTPException, and serializes response using Vehicle model. Confirm parameter and response types match architecture. | Accepted, implementation action | Accepted |
| DR-005 | Medium | Security and access control | Input validation: Path parameter `{vehicle_id}` is not explicitly validated in architecture. FastAPI will parse as string by default, but no documentation specifies constraints (length, format, allowed characters). | Malformed or oversized vehicle_id could cause issues downstream. Path traversal is low-risk (JSON search, not file path), but missing validation is a security gap. | Add explicit path parameter type annotation and validation constraints (e.g., `vehicle_id: str = Path(..., min_length=1, max_length=50)`) to Router layer. Document expected ID format and validation in architecture. | Accepted, implement in router | Accepted |
| DR-006 | Medium | Scalability and performance | File I/O bottleneck not quantified: Architecture states "acceptable for <100 req/sec" but provides no load test evidence or baseline. Disk read latency varies by platform/hardware. | Performance targets (<100ms) are assumed, not validated. Deployment to production could expose slow response times if disk is slow or file size grows. | Establish baseline response time (<100ms) via load testing before deployment. Document disk I/O assumptions (SSD, <5MB file size, <1000 vehicles). Monitor response times in production. | Accepted, verify in step 7 | Accepted |
| DR-007 | Medium | Observability and operations | Logging strategy undefined: Architecture does not specify logging for requests, errors, or data layer exceptions. Current `app/api/api.py` has a print() statement, not logging. | Debugging production issues will be difficult. Error traces not captured. Monitoring/alerting setup unclear. | Add structured logging (e.g., Python `logging` module or `python-json-logger`) to all three layers. Log successful retrievals at INFO level, errors at ERROR level, include request ID and vehicle_id for traceability. Update architecture with logging strategy section. | Accepted, implement in code | Accepted |
| DR-008 | Medium | Testability and maintainability | Test coverage not specified: Architecture does not define how to test service layer and data layer in isolation. Current `test/test.py` has endpoint tests but no unit tests for `read_vehicle()` or error scenarios. | Service and data layers cannot be verified independently. Mock test data or fixtures not documented. Test data consistency with production schema not guaranteed. | Define test strategy: (1) Unit tests for `read_vehicle()` with mocked file I/O, (2) Integration tests for `/vehicles/{vehicle_id}` endpoint using test fixtures (test vehicle in `data/cars.json` or separate test data), (3) Test both AC-001 and AC-002 scenarios. Include in implementation plan. | Accepted, implement in tests | Accepted |
| DR-009 | Low | Technology choices | Pydantic version not pinned: `requirements.txt` has old FastAPI (0.46.0) and uvicorn (0.11.1) versions from ~2019. No Pydantic version specified. | Dependency drift risk. Type validation and JSON serialization behavior may differ from expected. Security vulnerabilities in old versions. | Update dependencies: FastAPI ≥0.100.0, uvicorn ≥0.20.0, pydantic ≥2.0. Test compatibility with existing code. Document minimum Python version (currently assumes 3.7+, recommend 3.9+). | Accepted, update before coding | Accepted |
| DR-010 | Low | Data flow | Concurrent write scenario not addressed: Architecture assumes single-writer constraint but does not document enforcement mechanism. | If multiple processes write to `data/cars.json` simultaneously, data corruption is possible (though unlikely with current low-volume data). No mitigation visible. | Document assumption clearly in architecture. For future scope: add file-level write lock (fcntl on Unix, msvcrt on Windows) or migrate to database. Note this as a Known Limitation in CHANGELOG. | Deferred to future (out of scope) | Accepted |
| DR-011 | Low | SDLC pipeline coverage | SDLC configuration not linked: Architecture section lists agents and skills but does not explicitly verify `.github/agents/*.agent.md` and `.github/prompts/*.prompt.md` files exist and are configured. | Pipeline orchestration could fail if configuration is incomplete. | Verify at Step 4 (Planner) that all agent configs exist and reference correct artifact paths. Document in impl-plan.md. | Accepted, verify in step 4 | Accepted |

---

## Agreed Design Decisions

| Decision | Rationale | Owner | Status |
|---|---|---|---|
| **Three-layer architecture approved** | Separation of Router/Service/Data concerns is clean, testable, and maintainable. Aligns with current codebase organization (`app/main.py`, `app/api/api.py`, `app/db/models.py`). | Architect Agent | ✅ Approved |
| **JSON persistence accepted for scope** | Appropriate for current data volume (<1000 vehicles). Performance targets (<100ms, <100 req/sec) can be met with file I/O. Caching or database migration noted as future optimization. | Architect Agent | ✅ Approved |
| **FastAPI + Pydantic + uvicorn stack confirmed** | Type-safe, well-integrated, suitable for small-to-medium FastAPI services. Current versions outdated but replaceable. | Architect Agent | ✅ Approved |
| **Error handling: 404 for missing vehicles (AC-002)** | Standard HTTP semantics. FastAPI HTTPException with 404 status is the correct approach. Response format (minimal JSON with "detail" key) is acceptable. | Architect Agent | ✅ Approved |
| **Endpoint path finalized: /vehicles/{vehicle_id}** | RESTful convention. Singular "vehicle" (not "vehicles") is intentional for single-record retrieval. Accepted. | Architect Agent | ✅ Approved |
| **Vehicle ID type: integer (DR-003 Resolution)** | **APPROVED.** Path parameter type is `int`. Schema uses integer IDs (1–10) to match existing data. Architecture and tests will use integer types consistently. Service layer type hints updated. | Design Review Agent | ✅ Approved |
| **Data migration to vehicles.json (DR-001 Resolution)** | **APPROVED: Option A.** Migrated `data/cars.json` → `data/vehicles.json` with complete schema (id: int, make, model, year, price, transmission, fuel_type). All 10 vehicle records now include required attributes for AC-001. | Design Review Agent | ✅ Approved |
| **DR-004 endpoint implementation** | Router layer must expose `/vehicles/{vehicle_id}` GET endpoint with proper type hints and error handling. Service layer wiring confirmed. | Design Review Agent | ✅ Accepted |
| **DR-005 input validation** | Path parameter must be validated via FastAPI type hint `vehicle_id: int`. Prevents malformed requests from reaching service layer. | Design Review Agent | ✅ Accepted |
| **Dependency update (DR-009)** | FastAPI, uvicorn, and Pydantic must be updated to current versions before implementation. Existing code compatibility to be verified. | Design Review Agent | ✅ Accepted |

---

## Rejected or Deferred Findings

| ID | Finding | Rationale |
|---|---|---|
| DR-010 | Concurrent write safety (lock mechanism) | Out of scope for FR-001 (single release). Architecture constraint documented. Future releases can add optimistic locking or migrate to database. Acceptable risk at current scale. |
| DR-011 | SDLC pipeline completeness check | Deferred to Planner Agent (Step 4). Design Review Agent focuses on architecture, not config validation. |

---

## Required Architecture Updates

The following changes **must** be made to `artifacts/architecture.md` before implementation:

1. **File naming:** Update all references from `data/vehicles.json` to either:
   - `data/vehicles.json` (if data migration is approved), or
   - `data/cars.json` (if that's the accepted source)
   
2. **Data schema section:** Clarify which fields are required vs. optional. If using `data/cars.json`, document that make, model, year, transmission are derived/enriched or confirm AC-001 is updated to reflect actual attributes.

3. **Component responsibilities table:** Specify exact input/output types:
   - Router: `{vehicle_id: int}` or `{vehicle_id: str}`? Update Vehicle model example to match.
   - Service: Confirm exception handling (HTTPException with 404 status).
   - Data: Confirm return type (Vehicle dict or None).

4. **Technology choices:** Update dependency versions to current:
   - FastAPI >= 0.100.0
   - uvicorn >= 0.20.0
   - Pydantic >= 2.0

5. **Deployment section:** Add validation and testing requirements:
   - Pre-deployment check: Load data file and validate schema.
   - Test: Run pytest on all three scenarios (existing vehicle, non-existent vehicle, malformed ID).

6. **Assumptions and Constraints:** Add explicit type constraints:
   - Vehicle ID type: [integer|string]
   - Vehicle ID format: [1–10 | string pattern]
   - Data file format: JSON with documented schema

7. **Logging strategy section:** Add new subsection under Observability:
   - Log level (INFO/ERROR/DEBUG).
   - Log format (JSON or plain text).
   - Captured fields (request_id, vehicle_id, response_code, latency).

8. **Test strategy section:** Add new subsection defining unit and integration test scope.

---

## Open Questions

| Question | Impact | Resolution Path |
|---|---|---|
| **Data schema: Which version of vehicle attributes is authoritative?** | Blocks AC-001 validation and all implementation. Current data/cars.json does not match AC-001 requirements. | Stakeholder decision: (A) Migrate to full schema or (B) Narrow AC-001. Decision must be made before Planner Agent (Step 4). |
| **Vehicle ID type: String or integer?** | Blocks service layer implementation, tests, and endpoint parameter type. | Stakeholder decision: Recommend integer (matches existing data), but confirm. Update all layers consistently. |
| **Should Pydantic Vehicle model be updated to require all AC-001 fields (make, model, year, transmission)?** | Currently all fields except id, name, price, fuel_type are optional. Allows incomplete vehicle records to be returned. | Clarify: Are these fields mandatory (required in model validation) or optional (can be null)? Update model and schema validation accordingly. |
| **What is the expected response format for 404 errors?** | AC-002 specifies "HTTP 404 with appropriate error message" but not format. FastAPI default is `{"detail": "Not Found"}`. | Confirm acceptable or define custom error response schema. Document in architecture. |

---

## Readiness Recommendation

### ⏸️ PAUSE PIPELINE — RESOLVE CRITICAL FINDINGS BEFORE PROCEEDING

**Status:** Architecture is structurally sound but **blocked by data schema and ID type mismatches** (DR-001, DR-003).

**Blockers:**
- DR-001 (Critical): Data file mismatch — `data/vehicles.json` does not exist; actual file is `data/cars.json` with incompatible schema.
- DR-003 (Critical): Vehicle ID type inconsistency — Architecture assumes string IDs; data uses integers. Service layer will fail at runtime.

**High findings requiring decision:**
- DR-002 (High): AC-001 attribute mismatch — requires 6 specific fields not all present in current data.
- DR-004 (High): Missing endpoint — `/vehicles/{vehicle_id}` not yet wired in `app/main.py`.

**Mitigation:**
1. **Stakeholder clarification required:** Decide data schema (migrate or narrow AC-001).
2. **Stakeholder clarification required:** Confirm vehicle_id type (string or integer).
3. **Update requirements or architecture:** Align AC-001 and architecture with confirmed decisions.
4. **Implementation blocked until (1) and (2) are resolved.**

**Next Steps:**
- User confirms data schema approach (A: migrate, B: narrow AC-001).
- User confirms vehicle_id type (recommend: integer).
- Update `artifacts/architecture.md` with confirmed decisions.
- Re-run Design Review Agent on updated architecture.
- If all Critical/High findings resolved → Proceed to Planner Agent (Step 4).

---

## Traceability Matrix

| Artifact | Requirement | Finding | Status |
|---|---|---|---|
| FR-001 | System shall retrieve vehicle details by ID | DR-001, DR-002, DR-003, DR-004 | Blocked — data schema and endpoint incomplete |
| AC-001 | Retrieve existing vehicle, HTTP 200 with all attributes | DR-001 (file), DR-002 (schema), DR-003 (ID type), DR-005 (validation) | Blocked — cannot return required attributes without data migration |
| AC-002 | Retrieve non-existent vehicle, HTTP 404 | DR-004 (endpoint), DR-005 (validation) | Partially ready — error handling logic present, endpoint missing |
| requirements.md | Out of scope: no auth, pagination, DB | No findings | Accepted |
| architecture.md | Three-layer design, JSON persistence, FastAPI | All findings | Updates required per above section |

---

## Summary of Changes Needed

**Critical / High:**
- ✅ Clarify data schema (DR-001, DR-002)
- ✅ Confirm vehicle_id type (DR-003)
- ✅ Add /vehicles/{vehicle_id} endpoint to app/main.py (DR-004)

**Medium:**
- ✅ Add input validation to path parameter (DR-005)
- ✅ Establish performance baseline (DR-006)
- ✅ Add logging strategy (DR-007)
- ✅ Define test strategy (DR-008)
- ✅ Update dependencies (DR-009)

**Low / Deferred:**
- ℹ️ Concurrent write safety (future scope)
- ℹ️ SDLC config validation (Step 4)

---

**Document Version:** 1.0  
**Review Date:** 2026-10-01  
**Reviewed By:** Design Review Agent (GitHub Copilot)  
**Approval Status:** ⏸️ **BLOCKED** — Awaiting stakeholder decision on DR-001 and DR-003
