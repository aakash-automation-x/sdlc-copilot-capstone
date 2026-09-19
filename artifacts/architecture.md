# Car Portal - System Architecture

## Architecture Overview

The Car Portal is a lean, 2-vehicle comparison REST API built with FastAPI and PostgreSQL. The system enforces strict 2-vehicle validation, user authorization, and persistent storage with UUID-based identifiers. This architecture supports the 5 core functional requirements with minimal scope and no speculative features.

**Scope:** MVP with 2 REST endpoints, user-scoped comparison storage, and 5 key vehicle attributes.

---

## Architectural Goals & Drivers

| Driver | Rationale |
|--------|-----------|
| **2-vehicle constraint** | FR-001 enforces exactly 2 vehicles per comparison; validation must occur early in API layer |
| **User isolation** | FR-005 requires users access only their own comparisons; authorization checks on every retrieval |
| **Persistent storage** | FR-004 mandates UUID-based database persistence across sessions |
| **Fast queries** | < 2 second response time per requirements; indexed lookups on comparison_id and user_id |
| **Simple deployment** | Single FastAPI server + PostgreSQL; no distributed cache or message queue needed for MVP |

---

## High-Level Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Client (REST)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                           │
│  POST /api/v1/comparisons  │  GET /api/v1/comparisons/{id}      │
│  ├─ Request validation     │  ├─ Auth check                    │
│  ├─ 2-vehicle check        │  ├─ Ownership check               │
│  └─ Call Business Logic    │  └─ Call Business Logic           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               Business Logic Layer                               │
│  ├─ Comparison Validator (2-vehicle, attributes)                │
│  ├─ Authorization Service (user ownership)                      │
│  └─ Comparison Builder (aggregate vehicles + metadata)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          Data Access Layer (SQLAlchemy ORM)                      │
│  ├─ Comparison queries (SELECT, INSERT by ID/user)              │
│  └─ Vehicle queries (fetch vehicle attributes by ID)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                             │
│  ├─ comparisons table (comparison_id, user_id, created_at)      │
│  ├─ vehicles table (vehicle_id, price, make, model, ...)        │
│  ├─ comparison_vehicles (join table, idx on comparison_id)      │
│  └─ indexes on user_id, comparison_id, vehicle_id              │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. CREATE Comparison Flow (FR-001, FR-004):
   POST /api/v1/comparisons
   ├─ Parse request (vehicle_ids: [uuid, uuid])
   ├─ Validate: exactly 2 vehicles
   ├─ Extract user_id from auth token
   ├─ Query vehicles table for both vehicle_ids
   ├─ Insert new row in comparisons table with UUID
   ├─ Insert 2 rows in comparison_vehicles join table
   └─ Return comparison_id + vehicle attributes

2. RETRIEVE Comparison Flow (FR-002, FR-005):
   GET /api/v1/comparisons/{comparison_id}
   ├─ Extract user_id from auth token
   ├─ Query comparison by comparison_id
   ├─ Check: owner is current user (403 if not)
   ├─ Query comparison_vehicles join table for 2 vehicle_ids
   ├─ Query vehicles table for attributes
   └─ Return aggregated comparison JSON
```

---

## Key Components & Responsibilities

### 1. API Layer (FastAPI Endpoints)
**Addresses:** FR-001, FR-002  
**Responsibilities:**
- Receive and parse HTTP requests
- Route to appropriate handler (create/retrieve)
- Call business logic layer
- Return JSON response with correct HTTP status codes (201, 200, 400, 401, 403, 404)

**Key Methods:**
- `POST /api/v1/comparisons` → `create_comparison(request, user_id)`
- `GET /api/v1/comparisons/{comparison_id}` → `get_comparison(comparison_id, user_id)`

### 2. Business Logic Layer (Validators & Services)
**Addresses:** FR-001, FR-003, FR-005  
**Responsibilities:**
- Validate 2-vehicle constraint (reject < 2 or > 2 vehicles)
- Verify ownership on retrieval (user_id match)
- Build comparison object with 5 key attributes
- Coordinate vehicle lookups and comparison assembly

**Key Classes:**
- `ComparisonValidator` → `validate_vehicle_count(vehicle_ids)`
- `AuthorizationService` → `check_ownership(user_id, comparison_id)`
- `ComparisonBuilder` → `build_comparison(vehicles, user_id, comparison_id)`

### 3. Data Access Layer (Repository Pattern via SQLAlchemy)
**Addresses:** FR-004  
**Responsibilities:**
- Execute SQL queries (SELECT, INSERT) via ORM
- Handle transaction boundaries
- Return domain objects (Comparison, Vehicle)
- Raise exceptions on query failures

**Key Methods:**
- `save_comparison(comparison_record)` → UUID
- `get_comparison_by_id(comparison_id)` → Comparison
- `get_vehicles_by_ids(vehicle_ids)` → List[Vehicle]

### 4. Authentication & Authorization (Middleware)
**Addresses:** FR-005  
**Responsibilities:**
- Extract and verify bearer token
- Populate user_id context
- Return 401 on invalid token
- Trigger ownership check in handlers

**Implementation:** FastAPI dependency injection via `Depends(verify_token)`

### 5. Database Schema & Indexing
**Addresses:** FR-004  
**Responsibilities:**
- Store comparisons with unique UUIDs
- Normalize vehicles (centralized table, no duplication)
- Join comparisons to vehicles via comparison_vehicles table
- Index on (user_id, created_at) and comparison_id for fast lookups

---

## Data Model & Schema

### Relational Schema

```
┌─────────────────────────────┐
│      comparisons            │
├─────────────────────────────┤
│ comparison_id (UUID, PK)    │
│ user_id (UUID, FK)          │
│ created_at (TIMESTAMP)      │
│ INDEX: (user_id, created_at)│
│ INDEX: comparison_id        │
└─────────────────────────────┘
           │
           │ (1:many)
           ▼
┌─────────────────────────────┐
│ comparison_vehicles (join)  │
├─────────────────────────────┤
│ comparison_id (FK, PK part) │
│ vehicle_id (FK, PK part)    │
│ display_order (int, 1 or 2) │
│ INDEX: (comparison_id)      │
└─────────────────────────────┘
           │
           │ (many:1)
           ▼
┌─────────────────────────────┐
│      vehicles               │
├─────────────────────────────┤
│ vehicle_id (UUID, PK)       │
│ price (DECIMAL)             │
│ make (VARCHAR)              │
│ model (VARCHAR)             │
│ year (INT)                  │
│ transmission (VARCHAR)      │
│ fuel_type (VARCHAR)         │
│ INDEX: vehicle_id           │
└─────────────────────────────┘
```

### SQL Schema Definition

```sql
CREATE TABLE comparisons (
    comparison_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicles (
    vehicle_id UUID PRIMARY KEY,
    price DECIMAL(12, 2) NOT NULL,
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    year INT NOT NULL,
    transmission VARCHAR(50) NOT NULL,
    fuel_type VARCHAR(50) NOT NULL
);

CREATE TABLE comparison_vehicles (
    comparison_id UUID NOT NULL REFERENCES comparisons(comparison_id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(vehicle_id),
    display_order INT NOT NULL,
    PRIMARY KEY (comparison_id, vehicle_id)
);

CREATE INDEX idx_comparisons_user_id ON comparisons(user_id);
CREATE INDEX idx_comparison_vehicles_comparison_id ON comparison_vehicles(comparison_id);
CREATE INDEX idx_vehicles_vehicle_id ON vehicles(vehicle_id);
```

---

## API Contract & Responses

### POST /api/v1/comparisons

**Request:**
```json
{
  "vehicle_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]
}
```

**Response (201 Created):**
```json
{
  "comparison_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "vehicles": [
    {
      "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
      "price": 25000.00,
      "make": "Toyota",
      "model": "Camry",
      "year": 2023,
      "transmission": "Automatic",
      "fuel_type": "Gasoline"
    },
    {
      "vehicle_id": "550e8400-e29b-41d4-a716-446655440001",
      "price": 28500.00,
      "make": "Honda",
      "model": "Accord",
      "year": 2024,
      "transmission": "CVT",
      "fuel_type": "Hybrid"
    }
  ],
  "created_at": "2026-09-19T14:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` → vehicle_ids missing, count != 2, invalid UUID format
- `401 Unauthorized` → missing/invalid auth token
- `404 Not Found` → one or both vehicle_ids do not exist in vehicles table

---

### GET /api/v1/comparisons/{comparison_id}

**Request:**
- Header: `Authorization: Bearer <token>`
- Path: `/api/v1/comparisons/f47ac10b-58cc-4372-a567-0e02b2c3d479`

**Response (200 OK):**
```json
{
  "comparison_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "vehicles": [...]  /* Same as POST response */,
  "created_at": "2026-09-19T14:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` → missing/invalid auth token
- `403 Forbidden` → comparison exists but user_id does not match auth token
- `404 Not Found` → comparison_id does not exist

---

## Technology Stack & Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Framework** | FastAPI | Async Python, built-in validation, auto-generated OpenAPI docs, low latency |
| **Database** | PostgreSQL | ACID compliance, relational normalization, UUID support, indexing for fast lookups |
| **ORM** | SQLAlchemy | Declarative models, query builder, transaction safety, widely used in Python |
| **ID Strategy** | UUID v4 | Non-sequential, secure (no enumeration), distributed-friendly, 128-bit uniqueness |
| **Auth** | Bearer Token (JWT assumed) | Stateless, scalable, standard REST pattern; token parsed from Authorization header |
| **Deployment** | Docker + Compose | Single container, reproducible environment, easy local dev and CI/CD |
| **Python Version** | 3.11+ | Async/await maturity, type hints, fast performance |

### Why NOT Chosen (Alternatives Considered)

| Alternative | Why Not |
|-------------|---------|
| REST vs GraphQL | GraphQL adds complexity; simple CRUD does not benefit from schema flexibility |
| NoSQL (MongoDB) | Relational normalization is essential; no document polymorphism needed; PostgreSQL is industry standard |
| Redis Cache | < 2 sec response time easily met by indexed SQL queries; cache invalidation overhead not worth it |
| JWT vs Session Cookies | API-first design favors stateless JWT; easier for mobile and distributed deployments |

---

## Security, Authorization & Input Validation

### User Authorization (FR-005)

**Strategy:**
1. Extract `user_id` from JWT token in Authorization header (middleware)
2. On `GET`, query comparison record and compare `comparison.user_id` with `token.user_id`
3. Return `403 Forbidden` if mismatch
4. No cross-user access possible by design

**Implementation:**
```python
@router.get("/api/v1/comparisons/{comparison_id}")
async def get_comparison(comparison_id: UUID, user_id: UUID = Depends(verify_token)):
    comparison = await db.get_comparison_by_id(comparison_id)
    if comparison.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return comparison
```

### Input Validation (All Endpoints)

| Input | Validation | Mechanism |
|-------|-----------|-----------|
| `vehicle_ids` | Exactly 2 items, valid UUID format | Pydantic schema + `ComparisonValidator` |
| `comparison_id` | Valid UUID format | Pydantic path parameter |
| `Authorization` header | Bearer token present, JWT valid | FastAPI dependency |
| Database query results | Non-null, type-correct | SQLAlchemy ORM type safety |

### Injection Prevention

- **SQL Injection:** SQLAlchemy parameterized queries prevent SQL injection
- **NoSQL Injection:** N/A (using PostgreSQL)
- **XOR attacks:** All user input validated via Pydantic before database access

### Rate Limiting (Out of Scope)

- Not included in MVP; if needed, add `slowapi` middleware or reverse proxy layer (nginx/Cloudflare)

---

## Scalability & Performance Considerations

### Query Performance (< 2 sec SLA)

**Create Comparison:**
1. Validate 2-vehicle constraint: O(1) list check
2. Query vehicles table: O(log N) indexed lookup by vehicle_id × 2
3. Insert comparison + 2 join records: O(1) write
4. Total: ~50-100ms on modern PostgreSQL

**Retrieve Comparison:**
1. Query comparison by id: O(log N) indexed lookup
2. Check ownership: O(1) UUID comparison
3. Query comparison_vehicles: O(log N) indexed join fetch
4. Query vehicles: O(log N) indexed lookup × 2
5. Total: ~50-150ms on modern PostgreSQL

**Indexes ensure < 2 sec compliance at any dataset size.**

### Horizontal Scaling (Future)

- **Multiple FastAPI instances:** Stateless design supports load balancing (nginx, k8s)
- **Read replicas:** GET endpoints can scale to PostgreSQL read replicas
- **Connection pooling:** Use `asyncpg` with connection pool (via SQLAlchemy)

### Storage Footprint (MVP)

- One comparison = ~200 bytes (UUIDs + timestamp)
- One vehicle = ~500 bytes (attributes)
- 10k comparisons × 2 vehicles = ~10MB + 5MB overhead = ~15MB total (minimal)

---

## Copilot Agents & SDLC Pipeline Integration

This architecture is designed to support the Agentic SDLC pipeline:

| Agent | Input | Output | Dependency |
|-------|-------|--------|-----------|
| **Step 1: Requirements** | User story | `artifacts/requirements.md` (5 FRs) | — |
| **Step 2: Architect** (→ This doc) | Requirements | `artifacts/architecture.md` | Requires Step 1 ✅ |
| **Step 3: Design Review** | Architecture | `artifacts/design-review.md` (inspection) | Requires Step 2 (you are here) |
| **Step 4: Planner** | Architecture + Review | `artifacts/impl-plan.md` (tasks) | Requires Steps 2–3 |
| **Step 5: Implementation** | Plan | Source code + tests | Requires Step 4 |
| **Step 6: Review** | Code + tests | Review notes / PR fixes | Requires Step 5 |
| **Step 7: Verify** | Code + tests | Test results / coverage | Requires Step 5 |
| **Step 8: PR Agent** | Code + review | Pull Request + `CHANGELOG.md` | Requires Steps 6–7 |

**This architecture document is sufficient for Steps 3–4 to proceed without re-interpretation.**

---

## Traceability to Requirements

| Requirement | Addressed By | Architecture Section |
|-------------|--------------|---------------------|
| **FR-001** Create comparison with exactly 2 vehicles via POST | API Layer + Business Logic validation | "API Contract", "Key Components", "Validation Strategy" |
| **FR-002** Retrieve saved comparison via GET | API Layer + Data Access Layer | "API Contract", "Component Diagram", "Data Flow" |
| **FR-003** Display 5 key vehicle attributes | Data Model + API response schema | "Data Model", "API Contract Response" |
| **FR-004** Persist all comparisons with UUID identifiers | Database Schema + ORM Layer | "Data Model & Schema", "SQL Schema Definition" |
| **FR-005** Enforce user-scoped access (users access only their own) | Authorization Service + ownership check | "Security, Authorization & Input Validation", "Key Components #4" |

**All 5 FRs have dedicated architecture components. No gaps.**

---

## Assumptions, Constraints & Open Questions

### Confirmed Assumptions

1. **Authentication method:** Bearer token (JWT) with user_id claim. Token parsing/validation handled upstream (API gateway or auth service).
2. **Vehicle data pre-loaded:** `vehicles` table is pre-populated; no create/update vehicle endpoints in scope.
3. **Single region deployment:** No multi-region replication complexity for MVP.
4. **Synchronous API only:** No async jobs, background tasks, or queues needed.

### Constraints

- **Exactly 2 vehicles per comparison:** No flexibility; enforced at API and business logic layers.
- **Read-only vehicles table:** Comparisons point to existing vehicles; no vehicle creation in this API.
- **< 2 second SLA:** Achieved via indexing and stateless design; no caching layer needed.

### Open Questions for Design Review

1. **Token extraction:** Where is JWT validation performed? Should it be in this API (middleware), or assumed valid by upstream proxy?
2. **Error logging:** Should errors be logged to a central service (e.g., Sentry), or just local stdout?
3. **CORS policy:** Should the API allow cross-origin requests? If so, which origins?
4. **Audit trail:** Should comparison creation/access be logged for compliance? Not in current scope but flag for future.

---

## Summary

The Car Portal architecture is a straightforward 3-tier REST service (API + Business Logic + Data Access) backed by PostgreSQL. It enforces 2-vehicle constraints, user isolation, and UUID persistence with no overengineering. FastAPI + SQLAlchemy + PostgreSQL provide solid foundations for fast, safe queries. Indexing ensures < 2 second response times. The design is ready for Planner decomposition into implementation tasks.

**Status:** ✅ Ready for Design Review (Step 3)  
**Next Step:** Design Review Agent validates this architecture against requirements and best practices.

---

**Version:** 1.0  
**Date:** 2026-09-19  
**Author:** Architect Agent  
**Pipeline Step:** 2 of 8
