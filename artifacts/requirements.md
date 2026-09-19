# Car Portal – Vehicle Comparison Feature – Requirements

**Project:** Car Portal Recommendation System  
**Feature:** Vehicle Comparison (MVP)  
**User Story Version:** 2.0  
**Requirements Version:** 1.0  
**Status:** Draft – Awaiting Approval  
**Last Updated:** 2026-09-19  

---

## 1. User Story & Business Objective

**User Story:**  
> As a car shopper, I want to compare 2 vehicles to help me make a purchase decision.

**Business Objective:**  
Enable users to create and retrieve vehicle comparisons so they can make informed purchase decisions.

**Scope:**  
This document captures all requirements for the **MVP release**, which provides core comparison creation and retrieval for exactly 2 vehicles with user ownership enforcement and basic security. Future enhancements (export, history, 5+ vehicles, visual features) are explicitly out of scope and marked as deferred.

---

## 2. Stakeholders & Actors

| Actor | Role | Context |
|-------|------|---------|
| **Car Shopper** | End user | Authenticated user seeking to compare vehicles |
| **System** | Comparison Engine | FastAPI backend processing comparisons |
| **Vehicle Database** | Data source | Upstream system providing vehicle specifications |
| **Authentication System** | Access control | Upstream system providing user identity & JWT tokens |

---

## 3. Functional Requirements

### FR-001: Create Comparison for Exactly 2 Vehicles

**Requirement Statement:**  
The system shall allow authenticated users to create a new comparison for exactly 2 vehicles. If the request includes fewer than 2 or more than 2 vehicle IDs, the system shall reject the request with a clear error message.

**Acceptance Criteria:**
- ✅ POST `/api/v1/comparisons` accepts a JSON payload with exactly 2 vehicle IDs  
- ✅ System validates vehicle count; rejects if count ≠ 2  
- ✅ System verifies each vehicle exists in the vehicle database before creating comparison  
- ✅ On success, returns HTTP 201 with comparison ID (UUID v4), creation timestamp, and both vehicle IDs  
- ✅ On failure (wrong count or missing vehicles), returns HTTP 400 with descriptive error message  
- ✅ Comparison record is immediately retrievable by the same user  
- ✅ Comparison includes all vehicle attributes (price, make, model, year, transmission, fuel_type)  

**Test Cases:**
- Happy path: valid 2-vehicle comparison creation
- Reject: 1 vehicle
- Reject: 3 vehicles
- Reject: non-existent vehicle IDs
- Reject: duplicate vehicle IDs in same comparison

---

### FR-002: Retrieve Comparison by ID

**Requirement Statement:**  
The system shall retrieve a previously created comparison by its comparison ID. Only the user who created the comparison may retrieve it.

**Acceptance Criteria:**
- ✅ GET `/api/v1/comparisons/{comparison_id}` returns the comparison record if the requesting user owns it  
- ✅ Response includes comparison ID, creation timestamp, both vehicles with all attributes, and vehicle IDs  
- ✅ Returns HTTP 200 on success  
- ✅ Returns HTTP 404 if comparison ID does not exist  
- ✅ Returns HTTP 403 if user does not own the comparison (access denied)  
- ✅ Error responses do not expose implementation details  

**Test Cases:**
- Happy path: user retrieves their own comparison
- Reject: non-existent comparison ID (404)
- Reject: user retrieves another user's comparison (403)
- Reject: malformed comparison ID format (400)

---

### FR-003: Persist Comparisons to Database

**Requirement Statement:**  
The system shall persist all created comparisons to a PostgreSQL database with full ACID compliance. Comparisons must survive application restarts and be queryable by ID and user owner.

**Acceptance Criteria:**
- ✅ Every comparison is stored in a `comparisons` table with columns: `id` (UUID, primary key), `user_id` (foreign key to users), `vehicle_1_id`, `vehicle_2_id`, `created_at`, `updated_at`  
- ✅ Database applies unique constraint on `id` to prevent duplicates  
- ✅ Foreign keys enforce referential integrity with user and vehicle tables  
- ✅ Comparison retrieval queries execute using parameterized statements (SQL injection prevention)  
- ✅ Indexes on `user_id`, `id`, and `vehicle_id` columns for query performance  

**Test Cases:**
- Happy path: comparison persists after create
- Happy path: comparison survives application restart
- Happy path: query by user_id returns only that user's comparisons
- Reject: duplicate ID insertion blocked by unique constraint

---

### FR-004: Enforce User Ownership

**Requirement Statement:**  
The system shall ensure that each user can only create, retrieve, and manage their own comparisons. A user cannot access, modify, or delete comparisons created by another user.

**Acceptance Criteria:**
- ✅ User identity is extracted from JWT bearer token in the `Authorization` header  
- ✅ Every comparison is associated with the authenticated user's `user_id` at creation time  
- ✅ Retrieval queries filter by both `comparison_id` AND `user_id` (authenticated user's ID)  
- ✅ If a user attempts to retrieve a comparison not belonging to them, system returns HTTP 403 Forbidden  
- ✅ Error messages do not reveal whether the comparison ID exists (no "that ID belongs to another user" message)  
- ✅ Authorization check is performed before any database query  

**Test Cases:**
- Happy path: user creates and retrieves their own comparison
- Happy path: user's comparisons are not visible in another user's queries
- Reject: User A attempts to retrieve User B's comparison (403)
- Reject: missing or invalid JWT token (401)
- Reject: expired JWT token (401)

---

## 4. Non-Functional Requirements

### NFR-001: Performance – Comparison Creation

**Requirement Statement:**  
Comparison creation (POST endpoint) shall complete within 500 milliseconds under normal load, measured from request receipt to response transmission.

**Acceptance Criteria:**
- ✅ P95 latency: ≤ 500ms (95th percentile of requests)  
- ✅ P99 latency: ≤ 700ms (99th percentile of requests)  
- ✅ Measurement includes database write, validation, and response serialization  
- ✅ Baseline: single user, no concurrent requests  

**Test Cases:**
- Load test: 100 sequential comparison creations, measure P95/P99
- Concurrent test: 50 simultaneous comparison creations, measure P95/P99

---

### NFR-002: Performance – Comparison Retrieval

**Requirement Statement:**  
Comparison retrieval (GET endpoint) shall complete within 500 milliseconds under normal load.

**Acceptance Criteria:**
- ✅ P95 latency: ≤ 500ms  
- ✅ P99 latency: ≤ 700ms  
- ✅ Measurement includes database lookup and response serialization  

**Test Cases:**
- Load test: 100 sequential comparison retrievals, measure P95/P99
- Concurrent test: 50 simultaneous retrievals, measure P95/P99

---

### NFR-003: Performance – Side-by-Side Rendering

**Requirement Statement:**  
The comparison response (retrieved data) shall be formatted and ready for side-by-side rendering within 2 seconds, including network transit time.

**Acceptance Criteria:**
- ✅ Full response payload (both vehicles + metadata) shall not exceed 100 KB  
- ✅ Comparison JSON structure shall be optimized for direct client-side rendering  
- ✅ No additional processing, pagination, or lazy-loading required for 2-vehicle comparison  

**Test Cases:**
- Response size: payload ≤ 100 KB
- Client-side rendering test: compare response can be rendered in < 2s on standard browser

---

### NFR-004: API Concurrency

**Requirement Statement:**  
The API shall support at least 50 simultaneous comparison requests (create or retrieve) without degradation or errors.

**Acceptance Criteria:**
- ✅ Load test: 50 concurrent requests all complete successfully  
- ✅ No HTTP 5xx errors due to concurrency  
- ✅ All requests respect their individual timeout and latency SLAs (NFR-001, NFR-002)  
- ✅ Database connection pool configured to support this load  

**Test Cases:**
- Load test: 50 concurrent POST requests (create)
- Load test: 50 concurrent GET requests (retrieve)
- Mixed load test: 25 POST + 25 GET concurrently

---

### NFR-005: Database Indexing

**Requirement Statement:**  
The database shall have appropriate indexes to support fast queries on comparison retrieval and user-scoped lookups.

**Acceptance Criteria:**
- ✅ Index on `comparisons.id` (primary key lookup)  
- ✅ Index on `comparisons.user_id` (user-scoped queries)  
- ✅ Index on `comparisons.vehicle_id` (if cross-reference queries added in future)  
- ✅ Indexes are created during database migration  
- ✅ Query planner confirms index usage for retrieval queries  

**Test Cases:**
- Query plan analysis: verify index usage
- Performance regression test: ensure retrieval latency remains ≤ 500ms with 10k+ comparisons

---

### NFR-006: Security – User Authorization

**Requirement Statement:**  
The system shall enforce mandatory user authentication and ownership-based authorization for all comparison endpoints.

**Acceptance Criteria:**
- ✅ All comparison endpoints require a valid JWT bearer token in the `Authorization` header  
- ✅ Invalid or missing tokens result in HTTP 401 Unauthorized  
- ✅ User ownership is verified on every retrieve operation (not cached)  
- ✅ No comparison data is leaked in error responses  

**Test Cases:**
- Reject: missing Authorization header
- Reject: invalid JWT signature
- Reject: expired JWT token
- Reject: user retrieves another user's comparison

---

### NFR-007: Security – Input Validation

**Requirement Statement:**  
All user-supplied input shall be validated before processing or database operations to prevent injection attacks and data corruption.

**Acceptance Criteria:**
- ✅ Vehicle IDs are validated as valid UUIDs before database lookup  
- ✅ Payload size is limited (max 1 MB per request)  
- ✅ Unexpected fields in JSON payload are rejected or silently ignored (configurable)  
- ✅ All database queries use parameterized statements (no string concatenation)  
- ✅ Invalid input returns HTTP 400 Bad Request with clear error message  

**Test Cases:**
- Reject: malformed UUID in vehicle_ids
- Reject: oversized payload
- Reject: SQL injection attempt in vehicle_id field
- Reject: non-numeric comparison_id
- Accept: extra unknown fields in payload (if applicable)

---

### NFR-008: Security – Rate Limiting

**Requirement Statement:**  
The system shall enforce rate limiting to prevent abuse: maximum 10 comparison operations (create + retrieve) per minute per authenticated user.

**Acceptance Criteria:**
- ✅ Rate limit is tracked per user_id extracted from JWT  
- ✅ Exceeding limit returns HTTP 429 Too Many Requests  
- ✅ Response includes `Retry-After` header with seconds until limit resets  
- ✅ Rate limit window is rolling (last 60 seconds)  
- ✅ Rate limit counter is stored in-memory or Redis (implementation choice)  

**Test Cases:**
- Happy path: user can make 10 requests per minute without throttling
- Reject: 11th request within a minute returns 429
- Accept: requests after minute boundary reset counter

---

### NFR-009: Security – No Hardcoded Credentials

**Requirement Statement:**  
No database passwords, API keys, tokens, or secrets shall be hardcoded in source code, configuration files, or committed to version control.

**Acceptance Criteria:**
- ✅ All secrets are loaded from environment variables (DATABASE_URL, JWT_SECRET, etc.)  
- ✅ `.env` file (if used locally) is listed in `.gitignore`  
- ✅ No credentials appear in code comments or documentation  
- ✅ Code review checklist includes verification of this requirement  

**Test Cases:**
- Static analysis: scan source code for hardcoded secrets
- Git audit: confirm no secrets in commit history

---

### NFR-010: Security – SQL Injection Prevention

**Requirement Statement:**  
All database queries shall use parameterized statements (prepared statements) to prevent SQL injection attacks.

**Acceptance Criteria:**
- ✅ SQLAlchemy ORM is used exclusively; no raw SQL string concatenation  
- ✅ All user-supplied values are bound as parameters, not interpolated  
- ✅ Code review confirms no `.format()`, `f-string`, or `%` string interpolation in SQL queries  

**Test Cases:**
- Code review: audit all database queries
- Security test: attempt SQL injection in vehicle_id and comparison_id fields

---

### NFR-011: Security – Error Message Handling

**Requirement Statement:**  
Error messages shall be user-friendly and not expose internal implementation details, database schema, or system architecture.

**Acceptance Criteria:**
- ✅ User-facing errors are generic: "Comparison not found" instead of "SELECT * FROM comparisons WHERE id='xyz' failed"  
- ✅ Stack traces are never returned to clients  
- ✅ Internal errors are logged server-side with full context for debugging  
- ✅ No SQL error messages, file paths, or version information exposed to clients  

**Test Cases:**
- Error response analysis: verify no stack trace in 400/404/500 responses
- Database error simulation: confirm sanitized error returned to client

---

### NFR-012: Test Coverage – Unit Tests

**Requirement Statement:**  
Comparison logic (creation, retrieval, validation, authorization) shall have a minimum of 80% unit test code coverage.

**Acceptance Criteria:**
- ✅ Unit tests cover all comparison creation logic, including edge cases (1 vehicle, 3 vehicles, duplicates)  
- ✅ Unit tests cover all authorization checks and edge cases (missing token, invalid token, different users)  
- ✅ Code coverage tool (pytest-cov) reports ≥ 80% for `app/comparison/` module  
- ✅ Coverage report is generated and reviewed before merge  

**Test Cases:**
- Run `pytest --cov=app/comparison/ --cov-report=html` and verify 80%+
- Uncovered lines are documented or remediated

---

### NFR-013: Test Coverage – Integration Tests

**Requirement Statement:**  
API endpoints shall have integration tests that verify full request/response cycle, including database writes and authentication.

**Acceptance Criteria:**
- ✅ Integration test for POST `/api/v1/comparisons` with valid payload  
- ✅ Integration test for GET `/api/v1/comparisons/{comparison_id}` with valid comparison  
- ✅ Integration tests use a test database or in-memory store  
- ✅ All integration tests pass before merge  

**Test Cases:**
- Full create-then-retrieve workflow
- Create with invalid vehicle count (1, 3, 0)
- Retrieve with unauthorized user
- Retrieve non-existent comparison

---

### NFR-014: API Response Format Consistency

**Requirement Statement:**  
All API responses shall follow a consistent JSON structure and HTTP status codes.

**Acceptance Criteria:**
- ✅ Success responses (2xx) include a `data` field with the comparison object  
- ✅ Error responses (4xx, 5xx) include an `error` field with `code` and `message`  
- ✅ All timestamps are in ISO 8601 format (UTC)  
- ✅ HTTP status codes are used correctly: 201 Created, 200 OK, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests, 500 Internal Server Error  

**Example Success Response (201):**
```json
{
  "data": {
    "comparison_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user123",
    "vehicle_1": { "id": "...", "make": "...", "model": "...", ... },
    "vehicle_2": { "id": "...", "make": "...", "model": "...", ... },
    "created_at": "2026-09-19T14:30:00Z"
  }
}
```

**Example Error Response (400):**
```json
{
  "error": {
    "code": "INVALID_VEHICLE_COUNT",
    "message": "Comparison requires exactly 2 vehicles; received 1"
  }
}
```

**Test Cases:**
- Verify response structure for all status codes
- Verify timestamp format is ISO 8601

---

### NFR-015: Logging & Observability

**Requirement Statement:**  
The system shall log all comparison operations (create, retrieve, authorization failures) for debugging and audit purposes.

**Acceptance Criteria:**
- ✅ Info-level logs: successful comparison creation with ID and user_id  
- ✅ Info-level logs: successful comparison retrieval with ID and user_id  
- ✅ Warn-level logs: authorization failures (user accessing non-owned comparison)  
- ✅ Error-level logs: database errors, validation failures  
- ✅ Logs include timestamp, log level, and correlation ID for request tracing  
- ✅ No user passwords, tokens, or sensitive data in logs  

**Test Cases:**
- Logs audit trail: successful operations logged at info level
- Logs security events: authorization failures logged at warn level

---

## 5. Dependencies & Assumptions

### Technical Dependencies

| Dependency | Version | Role |
|------------|---------|------|
| **Python** | 3.8+ | Application runtime |
| **FastAPI** | Latest stable | Web framework |
| **PostgreSQL** | 12+ | Relational database |
| **SQLAlchemy** | 1.4+ | ORM layer |
| **Pydantic** | 1.8+ | Request/response validation |
| **pytest** | Latest | Unit test framework |
| **pytest-asyncio** | Latest | Async test support |
| **python-jose** | Latest | JWT token handling |

### External System Assumptions

1. **Vehicle Database:** A vehicle table with schema `(id, make, model, year, price, transmission, fuel_type, ...)` exists and is accessible via SQLAlchemy.
2. **User Authentication:** A separate authentication system (upstream responsibility) provides JWT bearer tokens; the comparison service verifies tokens but does not issue them.
3. **User Table:** A users table exists with schema `(id, email, created_at, ...)` for foreign key validation.

### Process & Architecture Assumptions

1. Users are **always authenticated** before accessing comparison endpoints (authentication is upstream responsibility).
2. Vehicle attributes are **immutable** during the MVP; if a vehicle's price or specs change, a new comparison is required.
3. Comparison IDs are **UUIDs v4** and are cryptographically unique; no need for sequential identifiers.
4. 2-vehicle limit is **sufficient for MVP**; multi-vehicle support will be evaluated in future iterations.
5. User identity is **always embedded in the JWT token** and is trusted (no secondary validation needed).

---

## 6. Out-of-Scope Items (Future Enhancements)

The following items are explicitly deferred and will be addressed in subsequent releases:

| Feature | Rationale | Estimated Effort |
|---------|-----------|------------------|
| **Export to PDF** | Nice-to-have; requires external library; deferred to v1.1 | Medium |
| **Export to CSV** | Nice-to-have; can be added after core features stabilize | Medium |
| **Comparison History** | Requires additional schema; 30-day retention policy adds complexity | Medium |
| **5+ Vehicle Support** | Scope creep for MVP; architectural changes needed | High |
| **Visual Highlighting** | UI concern; deferred to frontend roadmap | Medium |
| **Column Reordering** | Personalization feature; low priority for MVP | Low |
| **Attribute Visibility Toggle** | Personalization feature; low priority for MVP | Low |
| **Best Value Scoring** | Requires pricing algorithm; deferred for business review | High |
| **Real-time API Integration** | Requires external vendor integration; scope creep | High |
| **Sub-1-second Performance** | Future optimization; 2-second target is sufficient for MVP | Medium |

---

## 7. Confirmed Decisions

1. **2-Vehicle Limit (MVP):** Requirement is fixed at exactly 2 vehicles for MVP. Future enhancement will explore 5+ vehicles.
2. **PostgreSQL + SQLAlchemy:** Technology stack is mandated by the project.
3. **JWT Bearer Tokens:** Authentication responsibility is upstream; comparison service assumes valid tokens.
4. **UUID v4 Identifiers:** Non-sequential UUIDs are mandated for security and scalability.
5. **User Ownership Enforcement:** Every comparison must be owned by exactly one authenticated user.

---

## 8. Open Questions

| Question | Owner | Impact | Status |
|----------|-------|--------|--------|
| **What is the retention policy for comparisons?** | Product Owner | Data lifecycle, storage costs, GDPR compliance | Not specified in user story |
| **Should users be able to delete their comparisons?** | Product Owner | API design (DELETE endpoint required?), audit trail implications | Not mentioned in user story |
| **Are there analytics/tracking requirements for comparison usage?** | Product Owner | Logging, data pipeline, privacy implications | Not specified |
| **What is the acceptable database downtime/SLA?** | Ops/DevOps | Backup strategy, replication setup | Not specified |
| **Should comparisons support 2 of the same vehicle (e.g., same make/model different year)?** | Product Owner | Validation rules, use case clarification | Assumed to be allowed |

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Database performance degrades** | Medium | Comparison retrieval exceeds SLA | Implement indexes (NFR-005), load testing, caching strategy |
| **Rate limiting causes false positives** | Low | Users blocked unfairly | Monitor rate limit metrics, adjust threshold if needed |
| **Authorization bypass due to JWT validation error** | Low | Critical security issue | Dedicated security test, code review, static analysis |
| **Vehicle database unavailability** | Medium | Cannot validate vehicles at create time | Graceful error handling, upstream SLA dependency |
| **Concurrent request spike** | Medium | API becomes unresponsive | Load testing (NFR-004), API throttling, auto-scaling |

---

## 10. Acceptance Criteria Summary

| Requirement | Acceptance Criteria | Priority |
|-------------|-------------------|----------|
| **FR-001** | Create 2-vehicle comparison; reject ≠2 | P0 (MVP) |
| **FR-002** | Retrieve comparison by ID; enforce ownership | P0 (MVP) |
| **FR-003** | Persist to PostgreSQL with ACID; indexes | P0 (MVP) |
| **FR-004** | Enforce user ownership; return 403 for unauthorized | P0 (MVP) |
| **NFR-001** | Create latency ≤ 500ms P95 | P0 (MVP) |
| **NFR-002** | Retrieve latency ≤ 500ms P95 | P0 (MVP) |
| **NFR-006** | Mandatory JWT auth + ownership validation | P0 (MVP) |
| **NFR-007** | Input validation; parameterized queries | P0 (MVP) |
| **NFR-008** | Rate limiting: 10 ops/min/user | P1 (MVP) |
| **NFR-012** | 80% unit test coverage | P0 (MVP) |

---

## 11. Traceability & Next Steps

**Traceability Matrix – Requirement Status:**

| ID | Type | Requirement | Source | Status | Next Artifact |
|----|------|-------------|--------|--------|----------------|
| FR-001 | Functional | Create 2-vehicle comparison | User story ✓ | Approved | Architecture |
| FR-002 | Functional | Retrieve comparison by ID | User story ✓ | Approved | Architecture |
| FR-003 | Functional | Persist to database | User story ✓ | Approved | Architecture |
| FR-004 | Functional | Enforce user ownership | User story ✓ | Approved | Architecture |
| NFR-001 | Non-Functional | Comparison creation performance | User story ✓ | Approved | Architecture |
| NFR-002 | Non-Functional | Comparison retrieval performance | User story ✓ | Approved | Architecture |
| NFR-003 | Non-Functional | Rendering performance | User story ✓ | Approved | Architecture |
| NFR-004 | Non-Functional | Concurrency support (50 requests) | User story ✓ | Approved | Architecture |
| NFR-005 | Non-Functional | Database indexing | User story ✓ | Approved | Architecture |
| NFR-006 | Non-Functional | User authorization | User story ✓ | Approved | Architecture |
| NFR-007 | Non-Functional | Input validation | User story ✓ | Approved | Architecture |
| NFR-008 | Non-Functional | Rate limiting | User story ✓ | Approved | Architecture |
| NFR-009 | Non-Functional | No hardcoded secrets | Security best practice | Approved | Architecture |
| NFR-010 | Non-Functional | SQL injection prevention | Security best practice | Approved | Architecture |
| NFR-011 | Non-Functional | Error message sanitization | Security best practice | Approved | Architecture |
| NFR-012 | Non-Functional | Unit test coverage 80% | User story ✓ | Approved | Implementation |
| NFR-013 | Non-Functional | Integration test coverage | User story ✓ | Approved | Implementation |
| NFR-014 | Non-Functional | API response consistency | Design best practice | Approved | Architecture |
| NFR-015 | Non-Functional | Logging & observability | Operational requirement | Approved | Architecture |

**Next Phase:**  
The Architect Agent will produce `artifacts/architecture.md`, mapping each FR/NFR to system components and data flows.

---

**Document Sign-Off:**

- **Requirements Status:** Draft – Awaiting stakeholder approval
- **Target Approval Date:** 2026-09-20
- **Prepared By:** Requirements Agent (Agentic SDLC)
- **Last Modified:** 2026-09-19 14:30 UTC

---
