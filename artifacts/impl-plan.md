# Implementation Plan - Car Portal Vehicle Details API (Phase 1)

**Phase:** Step 4 - Planner Agent  
**Input Artifacts:**
- `artifacts/requirements.md` (FR-001: Retrieve Vehicle Details by ID) ✅ Approved
- `artifacts/architecture.md` (4-layer architecture: API / Service / Repository / DB) ✅ Approved
- `artifacts/design-review.md` (Conditional PASS with action items A1-A4) ✅ Approved

**Scope:** Phase 1 (MVP) - FR-001 only. All Phase 2+ enhancements (list, create, caching, Kubernetes) are deferred.

**Date:** 2026-09-19  
**Status:** Ready for Implementation (Step 5)

---

## 1. Phase 1 Scope Confirmation

### 1.1 In-Scope Deliverables for Phase 1

✅ **Single Functional Requirement:**
- **FR-001:** Retrieve vehicle details by ID via `GET /api/v1/vehicles/{vehicle_id}`
- **AC-001:** Return all 6 vehicle attributes (make, model, year, price, transmission, fuel_type)

✅ **Architecture Implementation:**
- API Layer: FastAPI HTTP endpoint with request validation
- Service Layer: VehicleService with business logic orchestration
- Repository Layer: VehicleRepository with parameterized SQL queries
- Database Layer: PostgreSQL with Vehicle ORM model and indexes

✅ **Infrastructure & Deployment:**
- Docker containerization for FastAPI application
- Docker Compose for local development environment
- Database migrations (Alembic schema versioning)
- Environment configuration management (.env files)

✅ **Quality Assurance:**
- Unit tests for service and repository layers (target >80% coverage)
- Integration tests for API + database interaction
- Manual E2E testing of full request flow
- Error handling and edge case validation

✅ **Documentation & Handoff:**
- Auto-generated API documentation (OpenAPI/Swagger)
- Implementation guide for deployment
- Architecture decision log

### 1.2 Out-of-Scope (Deferred to Phase 2+)

❌ List Vehicles endpoint (`GET /api/v1/vehicles`)  
❌ Create Vehicle endpoint (`POST /api/v1/vehicles`)  
❌ Update / Delete endpoints  
❌ Redis in-memory caching  
❌ User authentication and authorization  
❌ Rate limiting at API layer  
❌ Production Kubernetes deployment  
❌ Distributed tracing (OpenTelemetry)  
❌ Advanced monitoring (Prometheus + Grafana)  

---

## 2. Blocking Design Decisions (Must Resolve First)

These 4 decisions from the design review must be confirmed before Step 5 Implementation begins. **Status: BLOCKED** until stakeholder decisions are made.

### Decision D1: Vehicle ID Type (Action A2 from Design Review)

**Question:** Integer (sequential) or UUID (globally unique)?

| Aspect | Integer | UUID |
|--------|---------|------|
| **Indexing** | Native, efficient | Requires B-tree with UUID type |
| **Storage** | 8 bytes (BIGINT) | 16 bytes (UUID) |
| **API Clarity** | `GET /api/v1/vehicles/1` | `GET /api/v1/vehicles/550e8400-e29b-41d4-a716-446655440000` |
| **Migration Cost** | Low; simple sequential assignment | Medium; requires generation strategy |

**Recommendation:** **Integer** (current architecture assumption)  
**Rationale:** Simpler indexing, smaller storage, matches existing schema  
**Action:** Stakeholder approval required. Implementation blocked until confirmed.

**Decision Impact:**
- If Integer: No changes to ORM schema, API endpoint, or indexing strategy
- If UUID: Update Vehicle ORM model to use UUID type; modify API endpoint parameter type; adjust database indexing

---

### Decision D2: Scope Boundary - Phase 1 vs Phase 2 (Action A1 from Design Review)

**Question:** Does Phase 1 include ONLY FR-001 (get-by-ID), or also list/create endpoints?

**Current Recommendation:** **Phase 1 = FR-001 Only (get-by-ID)**

| Scope Option | Effort | Risk | Timeline |
|---|---|---|---|
| **Phase 1: FR-001 only (MVP)** | 2-3 weeks | Low | Predictable, achievable |
| **Phase 1: FR-001 + list + create** | 4-5 weeks | Medium | Adds complexity, error handling, validation |
| **Phase 1: All CRUD operations** | 6-8 weeks | High | Major effort, testing complexity |

**Recommendation:** Proceed with **Phase 1 = FR-001 only (MVP)**  
**Rationale:** Delivers business value quickly, minimizes risk, establishes architectural foundation  
**Action:** Stakeholder approval required. If scope changes, re-plan task list.

**Impact:** This implementation plan assumes Phase 1 = FR-001 only. Tasks for list/create/update/delete are OUT-OF-SCOPE.

---

### Decision D3: Validation & Error Handling Strategy (Actions A3-A4 from Design Review)

**Question:** What validation rules apply to vehicle_id? How to handle errors?

**Recommendation for Phase 1:**

| Aspect | Decision |
|--------|----------|
| **Vehicle ID Validation** | Must be positive integer (>0); must exist in database |
| **400 Bad Request** | Invalid vehicle_id (not integer, negative, zero, out of bounds) |
| **404 Not Found** | Valid integer, but vehicle doesn't exist |
| **500 Internal Error** | Database connection failure, query timeout, unexpected exceptions |
| **Error Response Format** | `{"detail": "...", "error_code": "..."}` (safe, no stack traces) |
| **Centralized Error Handling** | Implement middleware to catch all exceptions and return consistent error envelope |
| **Security Approach** | Never expose database schema, internals, or stack traces to client |

**Action:** Implementation team to implement centralized error middleware (TASK-010) per this strategy.

---

### Decision D4: Configuration Management & Secrets (Recommendation R4 from Design Review)

**Question:** How to manage environment-specific settings and secrets?

**Recommendation for Phase 1:**

| Setting | Strategy |
|---------|----------|
| **Database URL** | Environment variable `DATABASE_URL` (e.g., `postgresql://user:password@localhost/carportal`) |
| **API Port** | Environment variable `API_PORT` (default 8000) |
| **Log Level** | Environment variable `LOG_LEVEL` (default INFO) |
| **Debug Mode** | Environment variable `DEBUG` (default False, never True in production) |
| **Secrets Storage** | Never commit secrets to git. Use `.env` file (local dev) or secrets manager (production) |
| **Configuration File** | Create `.env.example` template with dummy values for documentation |

**Action:** Implementation team to create `.env.example` and use environment variables (TASK-001).

---

## 3. Implementation Task Breakdown

### 3.1 Task Organization by Phase

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1 Implementation: 12 Tasks across 4 Categories       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Category 1: Setup & Configuration (TASK-001 to TASK-003)   │
│  ├─ TASK-001: Environment Setup & Configuration             │
│  ├─ TASK-002: Database Setup (PostgreSQL + Alembic)         │
│  └─ TASK-003: FastAPI Skeleton & Dependency Injection       │
│                                                              │
│  Category 2: Core FR-001 Implementation (TASK-004 to TASK-008)
│  ├─ TASK-004: Vehicle ORM Model & Indexes                   │
│  ├─ TASK-005: VehicleRepository Layer                       │
│  ├─ TASK-006: VehicleService Layer                          │
│  ├─ TASK-007: API Endpoint (GET /api/v1/vehicles/{id})      │
│  └─ TASK-008: Request/Response Validation (Pydantic)        │
│                                                              │
│  Category 3: Quality & Reliability (TASK-009 to TASK-011)   │
│  ├─ TASK-009: Error Handling Middleware                     │
│  ├─ TASK-010: Unit Tests (Service + Repository)             │
│  └─ TASK-011: Integration Tests (API + DB)                  │
│                                                              │
│  Category 4: Documentation & Handoff (TASK-012)             │
│  └─ TASK-012: API Documentation & Deployment Guide          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Dependency Graph

```
TASK-001 (Environment)
    ├─▶ TASK-002 (Database Setup)
    │       └─▶ TASK-003 (FastAPI Skeleton)
    │               ├─▶ TASK-004 (ORM Model) ────────┐
    │               │       └─▶ TASK-005 (Repository) ┤
    │               │               └─▶ TASK-006 (Service) ─┐
    │               │                                        │
    │               └─▶ TASK-008 (Request/Response Validation)
    │                                   └─▶ TASK-007 (API Endpoint) ──┤
    │                                                                  │
    │                                   ┌──────────────────────────────┘
    │                                   │
    └─▶ TASK-009 (Error Middleware) ────┤
                                        │
                        ┌───────────────┘
                        │
                    TASK-007 (API Endpoint) [READY FOR TESTING]
                        │
            ┌───────────┴───────────┐
            │                       │
        TASK-010 (Unit Tests)   TASK-011 (Integration Tests)
            │                       │
            └───────────┬───────────┘
                        │
                    TASK-012 (Documentation)
                        │
                    ✅ PHASE 1 COMPLETE
```

### 3.3 Parallel vs Sequential Execution

**Sequential Path (Critical Blocking):**
1. TASK-001 → TASK-002 → TASK-003 (Foundation layers)
2. TASK-004 → TASK-005 → TASK-006 → TASK-007 (FR-001 implementation flow)
3. TASK-010 + TASK-011 (Testing, can overlap)
4. TASK-012 (Final documentation)

**Parallel Opportunities (Can Run Concurrently):**
- TASK-004 (ORM Model) and TASK-008 (Request/Response Validation) can start simultaneously after TASK-003 ✅
- TASK-010 (Unit Tests) and TASK-011 (Integration Tests) can run in parallel after TASK-007 ✅
- TASK-009 (Error Middleware) can be implemented any time after TASK-003 ✅

---

## 4. Task Details (Dependency-Ordered)

---

## TASK-001: Environment Setup & Configuration

**Category:** Setup & Configuration  
**Priority:** High  
**Depends on:** None  
**Blocked by:** None  
**Target agent:** Implementation Agent  
**Effort:** Small (1-2 hours)  

### Description

Set up environment variables, configuration management, and project structure for Phase 1 implementation. Establish secrets management pattern and document configuration strategy.

**Detailed Work:**
1. Create `.env.example` template with all required environment variables (DATABASE_URL, API_PORT, LOG_LEVEL, DEBUG)
2. Add `.env` file to `.gitignore` to prevent secrets from being committed
3. Create `app/config.py` module to load environment variables and provide configuration object
4. Set up Python logging configuration (structured JSON logging)
5. Document configuration schema in project README
6. Validate that all required environment variables are present at application startup

### Expected output

- `.env.example` template file with documented configuration options
- `app/config.py` Python module with Settings class (Pydantic BaseSettings)
- Updated `.gitignore` to protect `.env` secrets
- Logging configuration ready for use throughout application
- Configuration validation logic in application startup

### Validation

✅ `.env` file can be created from `.env.example`  
✅ Application reads DATABASE_URL, API_PORT, LOG_LEVEL from environment  
✅ `.env` files are properly ignored by git  
✅ Configuration errors are caught at startup with clear messages  
✅ Logging format is consistent (JSON structured logs)

### Architecture traceability

- **Traces to:** Design Review Section 5.2 (Configuration Management)
- **Traces to:** Architecture Section 10 (Error Handling & Observability)
- **Component:** Infrastructure / Configuration Layer

---

## TASK-002: Database Setup (PostgreSQL + Alembic)

**Category:** Setup & Configuration  
**Priority:** High  
**Depends on:** TASK-001 (Environment configuration established)  
**Blocked by:** None  
**Target agent:** Implementation Agent  
**Effort:** Small-Medium (2-3 hours)

### Description

Set up PostgreSQL database connection, initialize Alembic migration framework, and create initial schema migration for the vehicles table. This task establishes the data persistence layer foundation.

**Detailed Work:**
1. Update `requirements.txt` to include: `psycopg2-binary`, `SQLAlchemy>=2.0`, `Alembic`
2. Create `app/db/database.py` module with:
   - SQLAlchemy engine initialization (using DATABASE_URL from env)
   - Session factory configuration (sessionmaker)
   - Base declarative class for ORM models
   - Connection pooling configuration
3. Initialize Alembic in `alembic/` directory
4. Create initial migration file for vehicles table schema:
   ```sql
   CREATE TABLE vehicles (
       id BIGINT PRIMARY KEY,
       make VARCHAR(100) NOT NULL,
       model VARCHAR(100) NOT NULL,
       year INTEGER NOT NULL,
       price NUMERIC(10,2) NOT NULL,
       transmission VARCHAR(50) NOT NULL,
       fuel_type VARCHAR(50) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```
5. Create index on `id` (PK index) for FR-001 query performance
6. Set up Alembic downgrade/upgrade commands
7. Test migration: `alembic upgrade head` and `alembic downgrade base`

### Expected output

- Updated `requirements.txt` with database dependencies
- `app/db/database.py` with SQLAlchemy engine, session factory, Base class
- `alembic/` directory structure with environment and script templates
- `alembic/versions/{timestamp}_initial_schema.py` migration file
- Verified: `alembic upgrade head` creates vehicles table successfully
- Database connection pooling configured for Phase 1 (20 connections, adjustable)

### Validation

✅ `psycopg2` connection to PostgreSQL established via DATABASE_URL  
✅ SQLAlchemy engine initializes without errors  
✅ Alembic migration runs successfully: schema created in database  
✅ `vehicles` table exists with correct columns and indexes  
✅ Migration can be reversed: `alembic downgrade base` removes table  
✅ Connection pool is configured (default 20, adjustable via env var)

### Architecture traceability

- **Traces to:** Architecture Section 4.2.4 (Database Layer)
- **Traces to:** Architecture Section 6 (Technology Choices - PostgreSQL)
- **Component:** Database + ORM Setup
- **Risk mitigation:** R5 (Connection pool exhaustion) — pool size is configurable

---

## TASK-003: FastAPI Skeleton & Dependency Injection

**Category:** Setup & Configuration  
**Priority:** High  
**Depends on:** TASK-001 (Environment setup complete), TASK-002 (Database setup complete)  
**Blocked by:** None  
**Target agent:** Implementation Agent  
**Effort:** Small-Medium (2-3 hours)

### Description

Set up FastAPI application skeleton, initialize routing structure, configure dependency injection, and establish the HTTP server foundation for Phase 1.

**Detailed Work:**
1. Update `requirements.txt` to include: `fastapi>=0.104.0`, `uvicorn[standard]`, `pydantic>=2.0`
2. Create `app/main.py` FastAPI application entry point:
   - Initialize FastAPI app with title, description, version
   - Configure CORS if needed (local dev)
   - Set up request/response logging middleware
   - Set up error handler middleware (placeholder for TASK-009)
3. Create `app/api/routes.py` module with:
   - APIRouter instance for vehicle endpoints
   - Dependency injection setup (database session injection)
   - Placeholder route handlers (to be implemented in TASK-007)
4. Create `app/dependencies.py` module:
   - Database session dependency (FastAPI Depends)
   - Configuration dependency injection
5. Update `app/__init__.py` to export main FastAPI app
6. Verify application starts: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Verify OpenAPI docs accessible at `http://localhost:8000/docs`

### Expected output

- `app/main.py` with FastAPI application initialization
- `app/api/routes.py` with APIRouter and route structure
- `app/dependencies.py` with dependency injection providers (database session, config)
- Updated `requirements.txt` with FastAPI, Uvicorn, Pydantic
- Application starts without errors: `uvicorn app.main:app`
- OpenAPI documentation accessible at `/docs` endpoint

### Validation

✅ FastAPI app initializes with no import errors  
✅ Uvicorn server starts and listens on configured API_PORT  
✅ OpenAPI docs page (`/docs`) loads successfully  
✅ Database session is injected correctly via FastAPI dependency system  
✅ Configuration is accessible in route handlers via dependency injection  
✅ Request logging middleware captures HTTP requests  

### Architecture traceability

- **Traces to:** Architecture Section 4.2.1 (API Layer)
- **Traces to:** Architecture Section 6 (Technology Choices - FastAPI)
- **Component:** API Framework & Request Handling
- **Security note:** Error handler middleware is placeholder; TASK-009 will implement full error handling

---

## TASK-004: Vehicle ORM Model & Database Indexes

**Category:** Core FR-001 Implementation  
**Priority:** High  
**Depends on:** TASK-003 (FastAPI skeleton ready), TASK-002 (Database migration framework ready)  
**Blocked by:** Decision D1 (Vehicle ID type must be confirmed)  
**Target agent:** Implementation Agent  
**Effort:** Small (1-2 hours)

### Description

Define Vehicle ORM model using SQLAlchemy with all attributes required by FR-001. Create database indexes for query performance.

**Detailed Work:**
1. Create `app/db/models.py` with Vehicle ORM class:
   ```python
   class Vehicle(Base):
       __tablename__ = "vehicles"
       
       id = Column(Integer, primary_key=True, autoincrement=False)  # Decision D1: Integer
       make = Column(String(100), nullable=False)
       model = Column(String(100), nullable=False)
       year = Column(Integer, nullable=False)
       price = Column(Numeric(10, 2), nullable=False)
       transmission = Column(String(50), nullable=False)
       fuel_type = Column(String(50), nullable=False)
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
       
       def __repr__(self):
           return f"<Vehicle(id={self.id}, make={self.make}, model={self.model})>"
   ```
2. Define indexes for query performance:
   - Primary Key index on `id` (automatic in PostgreSQL)
   - Consider composite index on `(make, model, year)` for Phase 2 list queries
3. Add type hints to all model attributes
4. Add methods for data transformation (ORM to DTO)
5. Test: Create Vehicle instance and verify attributes
6. Verify SQLAlchemy model is compatible with Alembic migrations

### Expected output

- `app/db/models.py` with Vehicle ORM class
- All 6 FR-001 attributes (make, model, year, price, transmission, fuel_type) defined
- Metadata columns (created_at, updated_at) for audit trail
- Primary key index on `id` for fast lookups (FR-001 performance)
- Type hints on all attributes
- ORM model verified with SQLAlchemy inspection tools

### Validation

✅ Vehicle model can be instantiated: `Vehicle(id=1, make="Toyota", ...)`  
✅ SQLAlchemy can inspect model and generate SQL schema  
✅ Model is compatible with Alembic migration generation  
✅ All FR-001 attributes are present and properly typed  
✅ Model can be queried: `session.query(Vehicle).filter(Vehicle.id == 1)`  
✅ Indexes are created correctly in database

### Architecture traceability

- **Traces to:** FR-001 (All 6 vehicle attributes present)
- **Traces to:** AC-001 (Acceptance Criteria - Return all attributes)
- **Traces to:** Architecture Section 4.2.4 (Database Layer - Vehicle ORM)
- **Traces to:** Architecture Section 8.1 (Traceability Matrix)
- **Component:** Data Model / ORM Layer
- **Assumption:** Vehicle ID is Integer (Decision D1 must be confirmed)

---

## TASK-005: VehicleRepository Layer

**Category:** Core FR-001 Implementation  
**Priority:** High  
**Depends on:** TASK-004 (Vehicle ORM model created)  
**Blocked by:** None  
**Target agent:** Implementation Agent  
**Effort:** Small (1.5-2 hours)

### Description

Implement the Data Access Layer using the Repository pattern. The VehicleRepository provides an abstraction over database queries and ensures SQL injection prevention through parameterized queries.

**Detailed Work:**
1. Create `app/db/repositories/vehicle_repository.py` with BaseRepository and VehicleRepository classes:
   ```python
   class BaseRepository(Generic[T]):
       def __init__(self, db_session: Session, model_class: Type[T]):
           self.db_session = db_session
           self.model_class = model_class
       
       # Common methods: create, read, update, delete
   
   class VehicleRepository(BaseRepository[Vehicle]):
       def find_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
           """Retrieve vehicle by ID using parameterized query."""
           # Parameterized query prevents SQL injection
           return self.db_session.query(Vehicle).filter(
               Vehicle.id == vehicle_id
           ).first()
   ```
2. Implement method: `find_by_id(vehicle_id: int) -> Optional[Vehicle]` for FR-001
3. Add error handling: Raise custom `VehicleNotFound` exception if vehicle doesn't exist
4. Ensure all queries use parameterized queries (SQLAlchemy handles this automatically)
5. Add logging for debug/monitoring: Log query execution, cache hits/misses
6. Test repository in isolation (unit test with mock session)
7. Verify: No raw SQL strings, no string concatenation in queries

### Expected output

- `app/db/repositories/__init__.py` (package marker)
- `app/db/repositories/vehicle_repository.py` with:
  - BaseRepository class with generic CRUD methods
  - VehicleRepository class extending BaseRepository
  - `find_by_id(vehicle_id: int) -> Optional[Vehicle]` method
  - Custom exception: `VehicleNotFound`
- All queries use parameterized queries (SQLAlchemy ORM guarantees this)
- Repository is testable in isolation (no hard DB dependencies)

### Validation

✅ Repository can be instantiated with SQLAlchemy session  
✅ `find_by_id(1)` returns Vehicle object if exists  
✅ `find_by_id(999)` returns None or raises VehicleNotFound  
✅ Queries use parameterized statements (verify via SQLAlchemy inspection)  
✅ No raw SQL strings or string concatenation in codebase  
✅ Unit tests pass for repository layer (mock session)  
✅ Logging is in place for query execution

### Architecture traceability

- **Traces to:** FR-001 (Retrieve vehicle details by ID)
- **Traces to:** Architecture Section 4.2.3 (Data Access Layer - VehicleRepository)
- **Traces to:** Architecture Section 9.1 (Security - SQL Injection Prevention)
- **Component:** Repository Pattern / Data Access
- **Risk mitigation:** R1 (SQL injection vulnerability) — Parameterized queries prevent injection

---

## TASK-006: VehicleService Layer

**Category:** Core FR-001 Implementation  
**Priority:** High  
**Depends on:** TASK-005 (VehicleRepository created), TASK-001 (Logging configured)  
**Blocked by:** None  
**Target agent:** Implementation Agent  
**Effort:** Small (1.5-2 hours)

### Description

Implement the Business Logic Layer. The VehicleService orchestrates repository calls, applies business rules, and transforms data between ORM entities and API DTOs.

**Detailed Work:**
1. Create `app/services/vehicle_service.py` with VehicleService class:
   ```python
   class VehicleService:
       def __init__(self, repository: VehicleRepository):
           self.repository = repository
       
       def get_vehicle_by_id(self, vehicle_id: int) -> VehicleDTO:
           """Orchestrate retrieval and transformation for FR-001."""
           # Validate input
           if vehicle_id <= 0:
               raise ValueError("Vehicle ID must be positive")
           
           # Query database
           vehicle = self.repository.find_by_id(vehicle_id)
           if not vehicle:
               raise VehicleNotFound(f"Vehicle {vehicle_id} not found")
           
           # Transform ORM → DTO
           return VehicleDTO.from_orm(vehicle)
   ```
2. Define `VehicleDTO` Pydantic model for service output
3. Implement method: `get_vehicle_by_id(vehicle_id: int) -> VehicleDTO` for FR-001
4. Define custom exceptions:
   - `VehicleNotFound` (404)
   - `InvalidVehicleID` (400)
5. Add logging for business logic events (service calls, validation failures)
6. Add caching-friendly design (methods can be memoized later in Phase 2)
7. Test service in isolation (unit test with mock repository)

### Expected output

- `app/services/__init__.py` (package marker)
- `app/services/vehicle_service.py` with:
  - VehicleService class
  - `get_vehicle_by_id(vehicle_id: int) -> VehicleDTO` method
  - Custom exceptions (VehicleNotFound, InvalidVehicleID)
  - DTO transformation logic
- Dependency injection ready: Service accepts repository as constructor parameter
- Business logic is testable in isolation (mock repository)

### Validation

✅ VehicleService can be instantiated with VehicleRepository  
✅ `get_vehicle_by_id(1)` returns VehicleDTO with all 6 attributes  
✅ `get_vehicle_by_id(999)` raises VehicleNotFound  
✅ `get_vehicle_by_id(-1)` raises InvalidVehicleID or ValueError  
✅ ORM-to-DTO transformation preserves all data  
✅ Unit tests pass for service layer (mock repository)  
✅ Logging captures business logic events

### Architecture traceability

- **Traces to:** FR-001 (Retrieve vehicle details by ID)
- **Traces to:** AC-001 (Return all 6 vehicle attributes)
- **Traces to:** Architecture Section 4.2.2 (Service Layer - VehicleService)
- **Component:** Business Logic / Service Layer
- **Design pattern:** Dependency Injection, DTO transformation

---

## TASK-007: API Endpoint Implementation (GET /api/v1/vehicles/{vehicle_id})

**Category:** Core FR-001 Implementation  
**Priority:** High  
**Depends on:** TASK-006 (VehicleService created), TASK-008 (Request/Response validation defined)  
**Blocked by:** Decision D1 (Vehicle ID type must be confirmed)  
**Target agent:** Implementation Agent  
**Effort:** Small-Medium (1.5-2 hours)

### Description

Implement the FastAPI HTTP endpoint that exposes FR-001 to API consumers. Handle request routing, parameter validation, service orchestration, and response formatting.

**Detailed Work:**
1. Create endpoint in `app/api/routes.py`:
   ```python
   @router.get("/api/v1/vehicles/{vehicle_id}", response_model=VehicleResponse)
   async def get_vehicle(
       vehicle_id: int,
       service: VehicleService = Depends(get_vehicle_service)
   ) -> VehicleResponse:
       """Retrieve vehicle details by ID (FR-001)."""
       dto = service.get_vehicle_by_id(vehicle_id)
       return VehicleResponse.from_dto(dto)
   ```
2. Define request/response schemas (TASK-008)
3. Implement endpoint:
   - Path parameter validation: vehicle_id must be integer
   - Dependency injection: Inject VehicleService
   - Call service method: get_vehicle_by_id()
   - Transform service result to HTTP response (DTO → Response)
   - Return 200 OK on success
4. Error handling (will be completed by TASK-009):
   - Service exceptions (VehicleNotFound, InvalidVehicleID) will be caught by middleware
5. Add logging: Log incoming requests and responses
6. Test endpoint manually: `curl http://localhost:8000/api/v1/vehicles/1`
7. Verify OpenAPI documentation includes endpoint

### Expected output

- `app/api/routes.py` with:
  - FastAPI APIRouter instance
  - `get_vehicle()` endpoint handler for GET /api/v1/vehicles/{vehicle_id}
  - Request/response logging
  - Dependency injection of VehicleService
- Endpoint traces to FR-001 in code comments
- OpenAPI documentation generated automatically by FastAPI/Pydantic
- Endpoint is testable via HTTP client (curl, Postman, pytest)

### Validation

✅ HTTP GET /api/v1/vehicles/1 returns 200 OK with vehicle JSON  
✅ Response includes all 6 FR-001 attributes  
✅ Response also includes metadata (created_at, updated_at)  
✅ HTTP GET /api/v1/vehicles/999 returns error (404 via middleware)  
✅ HTTP GET /api/v1/vehicles/abc returns error (400 via middleware)  
✅ Endpoint is documented in OpenAPI/Swagger  
✅ Request/response logging is in place

### Architecture traceability

- **Traces to:** FR-001 (Retrieve vehicle details by ID)
- **Traces to:** AC-001 (Return all 6 vehicle attributes)
- **Traces to:** Architecture Section 4.2.1 (API Layer)
- **Traces to:** Architecture Section 5.1 (Sequence Diagram for FR-001)
- **Traces to:** Architecture Section 8.2 (Data Contract)
- **Component:** API Endpoint / HTTP Handler
- **RESTful design:** GET method, /api/v1/ path prefix, standard HTTP semantics

---

## TASK-008: Request/Response Validation (Pydantic Schemas)

**Category:** Core FR-001 Implementation  
**Priority:** High  
**Depends on:** TASK-003 (FastAPI skeleton), TASK-004 (Vehicle ORM model)  
**Blocked by:** Decision D3 (Validation rules must be confirmed)  
**Target agent:** Implementation Agent  
**Effort:** Small (1-2 hours)

### Description

Define Pydantic models for request and response validation. These schemas enforce data contracts and provide automatic validation/serialization/documentation.

**Detailed Work:**
1. Create `app/schemas/vehicle_schemas.py` with Pydantic models:
   ```python
   class VehicleResponse(BaseModel):
       id: int
       make: str
       model: str
       year: int
       price: float
       transmission: str
       fuel_type: str
       created_at: datetime
       updated_at: datetime
       
       class Config:
           from_attributes = True  # SQLAlchemy ORM compatibility
           json_schema_extra = {
               "example": {
                   "id": 1,
                   "make": "Toyota",
                   "model": "Camry",
                   ...
               }
           }
   ```
2. Define request validation:
   - `vehicle_id` parameter validation: positive integer
3. Define response schema: `VehicleResponse` with all 6 FR-001 attributes
4. Add field validation:
   - `vehicle_id`: `Field(gt=0, description="Positive vehicle ID")`
   - `price`: `Field(ge=0, description="Vehicle price in USD")`
   - `year`: `Field(ge=1900, le=2099, description="Manufacturing year")`
5. Add error handling hints (error codes for validation failures)
6. Add Pydantic config for ORM model conversion (from_attributes)
7. Add field examples for OpenAPI documentation
8. Test validation: Invalid inputs should raise ValidationError

### Expected output

- `app/schemas/__init__.py` (package marker)
- `app/schemas/vehicle_schemas.py` with:
  - VehicleResponse Pydantic model (with all 6 attributes)
  - VehicleDTO for service layer
  - Validation rules and constraints
  - OpenAPI documentation (examples, descriptions)
- Pydantic models are ORM-compatible (from_attributes=True)
- Validation errors provide clear error messages

### Validation

✅ VehicleResponse model can be instantiated from Vehicle ORM  
✅ Pydantic auto-serializes to JSON  
✅ Invalid data raises ValidationError with clear messages  
✅ OpenAPI documentation includes field constraints  
✅ All FR-001 required attributes are present  
✅ Request/response schemas match architecture contract (Section 8.2)

### Architecture traceability

- **Traces to:** FR-001 (All 6 vehicle attributes required)
- **Traces to:** AC-001 (Acceptance Criteria - Return all attributes)
- **Traces to:** Architecture Section 4.2.1 (API Layer - Request/Response Validation)
- **Traces to:** Architecture Section 8.2 (Data Contract)
- **Component:** Data Contracts / Validation Schemas
- **Security:** Input validation prevents invalid data from entering system

---

## TASK-009: Centralized Error Handling Middleware

**Category:** Quality & Reliability  
**Priority:** High  
**Depends on:** TASK-003 (FastAPI skeleton ready), TASK-006 (Custom exceptions defined)  
**Blocked by:** Decision D3 (Error handling strategy must be confirmed)  
**Target agent:** Implementation Agent  
**Effort:** Small-Medium (2-3 hours)

### Description

Implement centralized error handling middleware that catches all exceptions and returns safe, consistent error responses. This prevents information disclosure and provides clear feedback to API consumers.

**Detailed Work:**
1. Create `app/middleware/error_handler.py` with error handling middleware:
   ```python
   async def error_handler_middleware(request: Request, call_next):
       try:
           response = await call_next(request)
           return response
       except VehicleNotFound as e:
           return JSONResponse(
               status_code=status.HTTP_404_NOT_FOUND,
               content={"detail": "Vehicle not found", "error_code": "NOT_FOUND"}
           )
       except ValueError as e:
           return JSONResponse(
               status_code=status.HTTP_400_BAD_REQUEST,
               content={"detail": str(e), "error_code": "VALIDATION_ERROR"}
           )
       except DatabaseError as e:
           logger.error(f"Database error: {e}")  # Log internally
           return JSONResponse(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
           )
       except Exception as e:
           logger.error(f"Unexpected error: {e}")
           return JSONResponse(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
           )
   ```
2. Define custom exception hierarchy:
   - `ApplicationException` (base)
   - `VehicleNotFound` (404)
   - `InvalidVehicleID` (400)
   - `DatabaseError` (500)
3. Map exceptions to HTTP status codes (see Design Review Section 10.1.2)
4. Ensure error responses:
   - Never expose stack traces
   - Never expose database schema or internals
   - Include error_code for client-side error handling
   - Include human-readable detail message
5. Add structured logging for all exceptions
6. Register middleware in FastAPI app: `app.add_middleware(ErrorHandlerMiddleware)`
7. Test error handling with invalid requests
8. Verify no sensitive information is exposed in error responses

### Expected output

- `app/middleware/__init__.py` (package marker)
- `app/middleware/error_handler.py` with:
  - ErrorHandlerMiddleware class
  - Exception-to-HTTP-status mapping
  - Safe error response envelope format
- `app/exceptions.py` with custom exception hierarchy
- Middleware registered in `app/main.py`
- All exceptions caught and transformed to safe responses
- Logging in place for debugging (server-side only)

### Validation

✅ VehicleNotFound exception returns 404 with safe message  
✅ ValueError exception returns 400 with validation error  
✅ Database exceptions return 500 with generic message (no schema exposed)  
✅ Unexpected exceptions return 500 with generic message  
✅ No stack traces visible in HTTP responses  
✅ No database schema or connection strings leaked  
✅ All errors include error_code field for client handling  
✅ Server logs contain full exception details for debugging

### Architecture traceability

- **Traces to:** Design Review Section 10.1 (Error Handling Strategy)
- **Traces to:** Architecture Section 10.1.2 (Centralized Error Handler)
- **Component:** Middleware / Error Handling
- **Security:** Information Disclosure Prevention (OWASP A2)
- **Risk mitigation:** R3 (Unhandled exception leaks schema) — Centralized handler masks details

---

## TASK-010: Unit Tests (Service & Repository Layers)

**Category:** Quality & Reliability  
**Priority:** High  
**Depends on:** TASK-006 (VehicleService created), TASK-005 (VehicleRepository created)  
**Blocked by:** None  
**Target agent:** Implementation Agent (or Verification Agent)  
**Effort:** Medium (3-4 hours)

### Description

Write unit tests for service and repository layers using mock objects and fixtures. Achieve >80% code coverage for business logic.

**Detailed Work:**
1. Set up test framework:
   - Add `pytest`, `pytest-mock`, `pytest-cov` to requirements.txt
   - Create `test/conftest.py` with pytest fixtures
2. Create `test/test_vehicle_repository.py`:
   - Mock SQLAlchemy session
   - Test `find_by_id()` success case (vehicle exists)
   - Test `find_by_id()` failure case (vehicle not found)
   - Test parameterized queries (verify no raw SQL)
   - Test database connection error handling
3. Create `test/test_vehicle_service.py`:
   - Mock VehicleRepository
   - Test `get_vehicle_by_id()` success case
   - Test `get_vehicle_by_id()` with invalid ID (negative, zero)
   - Test `get_vehicle_by_id()` with non-existent ID (raises VehicleNotFound)
   - Test ORM-to-DTO transformation
   - Test logging calls
4. Test fixtures:
   - `sample_vehicle()` — Valid Vehicle ORM instance
   - `vehicle_dto()` — Valid VehicleDTO
   - `mock_repository()` — Mock VehicleRepository
   - `mock_session()` — Mock SQLAlchemy session
5. Validate test coverage:
   - Run: `pytest --cov=app test/`
   - Target: >80% coverage for service and repository layers
6. Verify all tests pass: `pytest test/`

### Expected output

- `test/conftest.py` with shared fixtures
- `test/test_vehicle_repository.py` with repository unit tests
- `test/test_vehicle_service.py` with service unit tests
- Test coverage report (target >80%)
- All unit tests passing
- Mock objects used (no real database connections in unit tests)

### Validation

✅ All unit tests pass: `pytest test/`  
✅ Code coverage >80% for service and repository layers  
✅ Mock repository is used in service tests (no real DB)  
✅ Mock session is used in repository tests (no real DB)  
✅ Happy path tested: get_vehicle_by_id(1) returns VehicleDTO  
✅ Error paths tested: get_vehicle_by_id(999) raises VehicleNotFound  
✅ Edge cases tested: negative/zero/invalid IDs  
✅ Logging is verified (mock check for log calls)

### Architecture traceability

- **Traces to:** Design Review Section 5.2 (Testing Strategy)
- **Traces to:** Design Review Section 8 (Checklist - Unit Testing)
- **Component:** Unit Testing / Test Suite
- **Quality goal:** >80% code coverage for Phase 1
- **Test pyramid:** Unit tests (fast, isolated, many)

---

## TASK-011: Integration Tests (API + Database)

**Category:** Quality & Reliability  
**Priority:** High  
**Depends on:** TASK-007 (API endpoint created), TASK-005 (VehicleRepository uses real DB)  
**Blocked by:** None  
**Target agent:** Verification Agent  
**Effort:** Medium-Large (4-5 hours)

### Description

Write integration tests that verify the full request flow from API endpoint through service layer to database. Test real database connections, schema, and data.

**Detailed Work:**
1. Set up integration test infrastructure:
   - Create test database configuration in `.env.test`
   - Create `test/conftest.py` fixtures for test database
   - Use Docker Compose or SQLite in-memory for test DB
2. Create `test/test_vehicle_api.py`:
   - Test FastAPI endpoint using TestClient
   - Test happy path: GET /api/v1/vehicles/1 returns 200 + vehicle JSON
   - Test 404 case: GET /api/v1/vehicles/999 returns 404
   - Test 400 case: GET /api/v1/vehicles/abc returns 400
   - Test validation: vehicle_id must be positive integer
   - Verify response schema matches VehicleResponse
   - Verify all 6 FR-001 attributes in response
3. Create `test/test_database_integration.py`:
   - Test full flow: API → Service → Repository → Database
   - Seed test database with sample vehicles
   - Verify database queries work end-to-end
   - Test error paths: missing vehicle, connection failures
4. Test fixtures:
   - `test_client()` — FastAPI TestClient
   - `test_db()` — Test database with schema
   - `sample_vehicles()` — Seed test data
5. Run integration tests: `pytest test/test_vehicle_api.py -v`
6. Verify all E2E flows work correctly
7. Document test execution and results

### Expected output

- `test/test_vehicle_api.py` with API integration tests
- `test/test_database_integration.py` with DB integration tests
- Test database setup and teardown fixtures
- Sample data (vehicles) for testing
- Integration tests pass with real database
- All response schemas validated

### Validation

✅ Happy path test: GET /api/v1/vehicles/1 returns 200 + complete vehicle JSON  
✅ 404 test: GET /api/v1/vehicles/999 returns 404 with error message  
✅ 400 test: GET /api/v1/vehicles/abc returns 400 with validation error  
✅ Validation test: vehicle_id > 0 and < max integer  
✅ Response includes all 6 FR-001 attributes + metadata  
✅ Response matches VehicleResponse Pydantic schema  
✅ Database integration verified (reads/writes work)  
✅ Error middleware catches exceptions and returns safe responses

### Architecture traceability

- **Traces to:** Design Review Section 5.2 (Testing Strategy)
- **Traces to:** Architecture Section 5.1 (Sequence Diagram - Full flow tested)
- **Component:** Integration Testing / Test Suite
- **Test pyramid:** Integration tests (slower, more realistic, fewer)
- **Quality goal:** Validate full FR-001 flow works end-to-end

---

## TASK-012: API Documentation & Deployment Guide

**Category:** Documentation & Handoff  
**Priority:** Medium  
**Depends on:** TASK-007 (API endpoint implemented), TASK-002 (Database setup complete)  
**Blocked by:** None  
**Target agent:** Implementation Agent (or PR Agent)  
**Effort:** Small-Medium (2-3 hours)

### Description

Document the API, create deployment instructions, and produce artifacts for handoff to operations/stakeholders. Include OpenAPI spec, deployment guide, and troubleshooting.

**Detailed Work:**
1. API Documentation:
   - OpenAPI/Swagger auto-generated by FastAPI at `/docs`
   - Export OpenAPI schema: `GET /openapi.json`
   - Document endpoint:
     - Path: `GET /api/v1/vehicles/{vehicle_id}`
     - Parameters: vehicle_id (positive integer)
     - Response: 200 OK with VehicleResponse schema
     - Errors: 400 Bad Request, 404 Not Found, 500 Internal Error
   - Document request/response examples
2. Create `DEPLOYMENT.md`:
   - Local development setup (Docker Compose)
   - Database initialization (Alembic migrations)
   - Environment variables required
   - Running tests
   - Manual testing examples (curl, Postman)
3. Create `TROUBLESHOOTING.md`:
   - Common issues and solutions
   - Database connection errors
   - Migration failures
   - Application startup issues
4. Update project `README.md`:
   - Project overview
   - Quick start guide
   - Architecture summary
   - Phase 1 scope and Phase 2 roadmap
5. Create `ARCHITECTURE_SUMMARY.md`:
   - Reference to detailed architecture document
   - Components overview
   - Key design decisions
   - Traceability to FR-001
6. Document code with comments:
   - Main entry point (app/main.py)
   - API endpoints (app/api/routes.py)
   - Service methods (app/services/vehicle_service.py)
   - Repository methods (app/db/repositories/vehicle_repository.py)
7. Verify documentation accuracy:
   - Test examples in DEPLOYMENT.md
   - Verify all code comments are accurate
   - Check that OpenAPI docs match implementation

### Expected output

- Updated `README.md` with project overview and quick start
- `DEPLOYMENT.md` with step-by-step deployment instructions
- `TROUBLESHOOTING.md` with common issues and solutions
- `ARCHITECTURE_SUMMARY.md` referencing `artifacts/architecture.md`
- Code comments and docstrings in all major functions
- OpenAPI documentation accessible at `/docs` endpoint
- Deployment ready: Docker Compose, Alembic migrations, env config

### Validation

✅ README provides clear project overview and quick start  
✅ DEPLOYMENT.md has step-by-step instructions  
✅ TROUBLESHOOTING.md covers common issues  
✅ Code is well-commented with docstrings  
✅ OpenAPI docs at `/docs` accurately reflect implementation  
✅ All examples in documentation are tested and working  
✅ Deployment instructions can be followed end-to-end

### Architecture traceability

- **Traces to:** Design Review Section 8 (Architecture Readiness)
- **Component:** Documentation & Handoff
- **Audience:** Operations, developers, stakeholders
- **Quality goal:** Enable smooth onboarding and deployment

---

## 5. Task Execution Timeline & Parallelization

### 5.1 Critical Path (Sequential Blocking Tasks)

```
TASK-001 (Environment)      [2 hours]  ──┐
                                          │
TASK-002 (Database Setup)    [3 hours]  ◄─┴─┐
                                            │
TASK-003 (FastAPI Skeleton) [3 hours]  ◄───┴─┐
                                            │
    ┌─────────────────────────┬─────────────┘
    │                         │
TASK-004 (ORM Model) [2 hrs] │   TASK-008 (Validation) [2 hrs]
    │                         │
TASK-005 (Repository) [2 hrs]│
    │                         │
TASK-006 (Service) [2 hrs]   │
    │                         │
TASK-007 (API Endpoint) [2 hrs] ◄───────────┘
    │
TASK-009 (Error Middleware) [3 hours] ◄─────────┐
                                                  │ [Can start after TASK-003]
    ┌─────────────────────────┬──────────────────┘
    │                         │
TASK-010 (Unit Tests) [4 hrs]│
    │                         │
TASK-011 (Integration Tests) [5 hrs]
    │
TASK-012 (Documentation) [3 hours]
    │
✅ PHASE 1 COMPLETE
```

### 5.2 Timeline Estimate

**Sequential Critical Path:**
- TASK-001 → TASK-002 → TASK-003 → TASK-007 = **11 hours** (blocking path)
- Plus TASK-004, TASK-005, TASK-006 = **6 hours**
- Plus TASK-008 (parallel) = **2 hours**
- Plus TASK-009 (parallel) = **3 hours**
- Plus TASK-010 = **4 hours**
- Plus TASK-011 = **5 hours**
- Plus TASK-012 = **3 hours**

**Total Effort (Sequential):** ~37 hours  
**Total Effort (Parallel):** ~28 hours (with TASK-004-006 and TASK-008-009 in parallel)

**Recommended Timeline:** 2-3 weeks (assuming 1 implementation engineer full-time)

### 5.3 Parallel Execution Strategy

**Phase A (Foundation - Sequential):** TASK-001 → TASK-002 → TASK-003  
**Weeks 1:** Setup & Framework (~8 hours)

**Phase B (Core Parallelization):** Start after TASK-003  
- **Track 1 (ORM & Repository):** TASK-004 → TASK-005 → TASK-006 (~6 hours)
- **Track 2 (API Contracts):** TASK-008 (~2 hours)
- **Track 3 (Error Handling):** TASK-009 (~3 hours)
- **Synchronization point:** TASK-007 (API endpoint, depends on TASK-006 + TASK-008)
**Week 2:** Core Implementation (~11 hours parallel = ~6 hours clock time)

**Phase C (Quality & Handoff - Sequential):** Start after TASK-007  
- TASK-010 (Unit Tests) → TASK-011 (Integration Tests) → TASK-012 (Documentation)
**Week 3:** Testing & Documentation (~12 hours = ~3 days)

---

## 6. Dependencies & Blocking Factors

### 6.1 Critical Dependencies

| Task | Depends On | Reason | Unblock Criteria |
|------|-----------|--------|-----------------|
| TASK-002 | TASK-001 | Env vars needed for DB connection | DATABASE_URL configured |
| TASK-003 | TASK-002 | DB session injection needed | Database connection pool established |
| TASK-004 | TASK-003 | ORM models use SQLAlchemy from TASK-003 | FastAPI app initialized |
| TASK-005 | TASK-004 | Repository needs Vehicle ORM model | Vehicle model defined |
| TASK-006 | TASK-005 | Service calls repository | Repository methods implemented |
| TASK-007 | TASK-006 + TASK-008 | Endpoint calls service; needs validation schemas | Service + schemas ready |
| TASK-009 | TASK-006 | Exceptions from service need to be caught | Custom exceptions defined |
| TASK-010 | TASK-006 + TASK-005 | Unit tests mock service/repository | Service + repository implemented |
| TASK-011 | TASK-007 + TASK-010 | Integration tests use real API + DB | API endpoint + unit tests ready |
| TASK-012 | TASK-007 + TASK-002 | Document API + deployment | API implemented, DB setup complete |

### 6.2 Blocking Design Decisions (Must Resolve First)

| Decision | Impact | Blocked Tasks | Unblock Criteria |
|----------|--------|---------------|-----------------|
| **D1: Vehicle ID Type** | ORM schema, API endpoint, indexing | TASK-004, TASK-007, TASK-008 | Stakeholder approval: Integer or UUID? |
| **D2: Phase 1 Scope** | Which tasks to implement | TASK-004 to TASK-012 | Stakeholder approval: FR-001 only or include list/create? |
| **D3: Validation Rules** | Input validation in API layer | TASK-008, TASK-007 | Architect decision: validation rules per Design Review Section 5.1 |
| **D4: Config Management** | Secrets handling, env vars | TASK-001, TASK-002, TASK-003 | Architect decision: env vars + .env.example (approved) |

**Status:** ⚠️ **AWAITING STAKEHOLDER APPROVAL FOR D1, D2**

---

## 7. Validation & Acceptance Criteria (Phase 1 Complete)

### 7.1 Functional Acceptance Criteria

| FR / AC | Validation Method | Expected Result |
|---------|-------------------|-----------------|
| **FR-001** | `curl http://localhost:8000/api/v1/vehicles/1` | 200 OK + Vehicle JSON |
| **AC-001** | Response includes: make, model, year, price, transmission, fuel_type | ✅ All 6 attributes present |
| **AC-001** | Response JSON schema matches VehicleResponse Pydantic model | ✅ Valid JSON, correct types |
| **Error 404** | `curl http://localhost:8000/api/v1/vehicles/999` | 404 Not Found + error message |
| **Error 400** | `curl http://localhost:8000/api/v1/vehicles/abc` | 400 Bad Request + validation error |

### 7.2 Technical Acceptance Criteria

| Category | Criterion | Success Criteria |
|----------|-----------|-----------------|
| **Code Coverage** | Unit test coverage | >80% for service + repository |
| **API Documentation** | OpenAPI spec | Endpoint documented at `/docs` |
| **Error Handling** | No information disclosure | No stack traces, schema, or internals exposed |
| **Database** | Schema verified | Alembic migration creates vehicles table correctly |
| **Security** | SQL injection prevention | All queries use parameterized statements |
| **Logging** | Structured logging in place | JSON logs for requests, responses, errors |
| **Integration** | Full flow tested | `curl` → API → Service → Repo → DB → response |
| **Docker** | Containerization | `docker-compose up` starts app + database |
| **Configuration** | Env management | DATABASE_URL, API_PORT, LOG_LEVEL from env vars |

### 7.3 Handoff Criteria to Step 5 (Implementation Agent)

✅ All 4 blocking design decisions (D1-D4) are approved  
✅ Implementation plan is reviewed and accepted by stakeholder  
✅ Architecture requirements (FR-001 + AC-001) are clear  
✅ Dependencies and parallelization strategy is documented  
✅ Task descriptions are detailed enough for implementation  
✅ Effort estimates are reasonable (28 hours total)  
✅ Timeline is achievable (2-3 weeks)  

---

## 8. Risk Assessment & Mitigation

### 8.1 Implementation Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **R1: ORM schema mismatch** | Medium | Implementation delay | Design Review (Section 5.1) confirms ORM schema is correct; TASK-004 validates against Alembic |
| **R2: Async bugs in error handling** | Medium | Data corruption, race conditions | TASK-009 uses proven FastAPI middleware pattern; TASK-011 tests error paths |
| **R3: Database connection pool exhaustion** | Low | Request failures | TASK-002 configures pool size (20); Design Review recommends validation testing |
| **R4: Test coverage gaps** | Medium | Missed edge cases | TASK-010 targets >80% coverage; TASK-011 includes integration tests |
| **R5: Deployment environment mismatch** | Low | "Works on my machine" syndrome | TASK-002 uses Docker Compose; TASK-012 documents deployment steps |
| **R6: Performance regression** | Low (Phase 1) | Slow response times | TASK-004 creates indexes; TASK-011 measures response times; Phase 2 will optimize |

### 8.2 Contingency Plans

| Risk | Contingency |
|------|------------|
| **R1: ORM schema mismatch** | If schema is incorrect, Alembic migration (TASK-002) fails fast; rework TASK-004 and re-run migration |
| **R2: Async bugs** | If async error handling fails in TASK-009, fall back to synchronous middleware pattern; add comprehensive logging |
| **R3: Pool exhaustion** | If pool size insufficient, increase DEFAULT_POOL_SIZE env var (TASK-001); load test before Phase 2 |
| **R4: Coverage gaps** | If coverage <80%, add missing tests for edge cases discovered during TASK-011 |
| **R5: Deployment mismatch** | If Docker Compose doesn't work, debug with `docker logs` and `docker-compose logs`; document fixes in TASK-012 |
| **R6: Performance regression** | If response time >100ms, check indexing (TASK-004) and connection pool (TASK-002); revisit Phase 2 optimization plan |

---

## 9. Recommendations for Implementation (Step 5)

### 9.1 Best Practices

1. **Commit Often:** Small, focused commits with clear messages referencing task IDs (TASK-001, TASK-002, etc.)
   - Example: `git commit -m "feat: TASK-004 - Vehicle ORM model with indexes"`

2. **Test-Driven Development:** Write tests BEFORE implementing features (for TASK-010, TASK-011)
   - Write test case → implement feature → verify test passes

3. **Code Review:** Each task should be reviewed before merging to ensure quality
   - Use GitHub pull requests with automated checks

4. **Traceability:** Link code comments to FR-001, AC-001, and architecture components
   - Example: `# FR-001: Retrieve vehicle details by ID (Architecture 4.2.2)`

5. **Dependency Injection:** Inject dependencies explicitly (repository into service, service into API)
   - Avoid hardcoded dependencies
   - Use FastAPI Depends() for HTTP handlers

6. **Error Messages:** Ensure error responses are helpful without exposing internals
   - Good: `"Vehicle not found"`
   - Bad: `"SELECT * FROM vehicles WHERE id = 1 returned no rows"`

### 9.2 Common Pitfalls to Avoid

❌ Don't commit secrets (passwords, API keys) to git  
❌ Don't use raw SQL strings; always use parameterized queries (SQLAlchemy handles this)  
❌ Don't expose stack traces in API error responses  
❌ Don't skip error middleware (TASK-009); it's critical for security  
❌ Don't implement Phase 2 features (list, create) in Phase 1  
❌ Don't forget database indexes (TASK-004); they're essential for performance  
❌ Don't skip logging (TASK-001, TASK-006); it's essential for debugging  

### 9.3 Suggested Verification Checklist Before Code Submission

- [ ] All unit tests pass: `pytest test/ --cov=app`
- [ ] Code coverage >80%: `pytest --cov-report=html`
- [ ] Integration tests pass: `pytest test/test_vehicle_api.py -v`
- [ ] No secrets in code: `grep -r "password\|api_key" app/`
- [ ] Linting passes: `pylint app/` or `flake8 app/`
- [ ] Type hints correct: `mypy app/`
- [ ] Docker builds: `docker build -t carportal .`
- [ ] Docker Compose works: `docker-compose up`
- [ ] API accessible: `curl http://localhost:8000/api/v1/vehicles/1`
- [ ] Swagger docs accessible: `http://localhost:8000/docs`
- [ ] Database migrations run: `alembic upgrade head`
- [ ] All 4 blocking decisions approved (D1-D4)

---

## 10. Traceability Matrix: Requirements → Tasks

| Requirement | Architecture Component | Implementation Task | Verification Task |
|---|---|---|---|
| **FR-001: Retrieve vehicle details by ID** | VehicleService.get_vehicle_by_id() | TASK-006 | TASK-007, TASK-011 |
| **AC-001: Return all 6 attributes (make, model, year, price, transmission, fuel_type)** | Vehicle ORM + VehicleResponse schema | TASK-004, TASK-008 | TASK-011 |
| **API Endpoint: GET /api/v1/vehicles/{vehicle_id}** | API Layer (FastAPI router) | TASK-007 | TASK-011 |
| **Request Validation (vehicle_id is integer)** | Pydantic + API layer | TASK-008 | TASK-011 |
| **Error Handling (404, 400, 500)** | Middleware + Service exceptions | TASK-009, TASK-006 | TASK-011 |
| **Database Storage (PostgreSQL)** | Database Layer + ORM | TASK-002, TASK-004 | TASK-011 |
| **SQL Injection Prevention** | SQLAlchemy + parameterized queries | TASK-005 | TASK-010, TASK-011 |
| **Configuration Management** | Environment variables, .env | TASK-001 | TASK-001 manual test |
| **API Documentation** | OpenAPI/Swagger | TASK-012 (auto-generated) | TASK-012 verification |
| **Deployment & Testing** | Docker Compose, Alembic | TASK-002, TASK-012 | TASK-011, TASK-012 |

---

## 11. Recommended Next Steps

### 11.1 Immediate Actions (Before Step 5 Starts)

1. **Stakeholder Approval:**
   - ✅ Confirm Decision D1 (Vehicle ID: Integer or UUID?)
   - ✅ Confirm Decision D2 (Phase 1 scope: FR-001 only?)
   - ✅ Confirm Decisions D3-D4 (Validation & Config management)

2. **Implementation Team Setup:**
   - Assign implementation engineer(s) to tasks
   - Set up development environment (Python 3.9+, PostgreSQL, Docker)
   - Clone repository and create feature branch for Phase 1 implementation

3. **Review Gate:** This implementation plan should be reviewed and approved by:
   - Product Manager (scope)
   - Architecture Lead (task decomposition)
   - QA Lead (testing strategy)
   - DevOps Lead (deployment considerations)

### 11.2 Execution Order for Implementation Agent (Step 5)

1. **Start TASK-001 & TASK-002** (in parallel if possible)
2. **Then TASK-003** (depends on TASK-001, TASK-002)
3. **Then START PARALLEL TRACKS:**
   - **Track 1:** TASK-004 → TASK-005 → TASK-006
   - **Track 2:** TASK-008
   - **Track 3:** TASK-009
4. **Then TASK-007** (depends on all of above)
5. **Then TASK-010 & TASK-011** (testing)
6. **Finally TASK-012** (documentation)

### 11.3 Success Criteria for Phase 1 Completion

✅ All 12 tasks are completed  
✅ All FR-001 and AC-001 requirements verified  
✅ Unit test coverage >80%  
✅ Integration tests pass end-to-end  
✅ API responds to `GET /api/v1/vehicles/{vehicle_id}` correctly  
✅ Error handling returns safe responses (no information disclosure)  
✅ Database migrations run successfully  
✅ Docker Compose deploys application correctly  
✅ Documentation is complete and accurate  
✅ Code is ready for review (Step 6)  

---

## 12. Sign-Off & Approval

**Prepared by:** Planner Agent (Step 4)  
**Date:** 2026-09-19  
**Status:** ✅ Ready for Implementation

**Approvals Pending:**
- [ ] Product Manager — Scope approval (D1, D2)
- [ ] Architecture Lead — Task decomposition review
- [ ] QA Lead — Testing strategy approval
- [ ] Implementation Lead — Feasibility & resource estimate

**Next Phase:** Step 5 - Implementation Agent

---

**End of Implementation Plan Document**
