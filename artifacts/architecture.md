# Architecture Document - Car Portal Vehicle Details API

**Project:** Car Portal Recommendation System  
**Phase:** Step 2 - Architect Agent  
**Version:** 1.0  
**Date:** 2026-09-19  
**Status:** Proposed for Review

---

## 1. Executive Summary

This document defines the high-level system architecture for the Car Portal Vehicle Details API, designed to fulfill FR-001: **Retrieve Vehicle Details by ID**. The architecture builds upon the existing FastAPI foundation and introduces a modular, scalable design that cleanly separates concerns across three layers: API, Business Logic, and Data Access.

**Phase 1 Scope (MVP - FR-001 Only):**
This document prioritizes Phase 1 implementation focused exclusively on FR-001 (get-by-ID). List, create, update, delete endpoints, distributed caching, and production Kubernetes topology are deferred to Phase 2+.

The recommended architecture leverages:
- **FastAPI** for HTTP API routing and request validation
- **SQLAlchemy ORM** for database abstraction and type-safe queries
- **PostgreSQL** for persistent, structured vehicle data storage
- **Docker & Docker Compose** for consistent containerization and local development
- **Layered Architecture** for maintainability, testability, and extensibility

---

## 2. Architecture Overview

### 2.1 System Context

```
┌──────────────────────────────────────────────────────────┐
│                    Car Portal System                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────┐         ┌─────────────────┐         │
│  │   HTTP Client   │◄────────│  FastAPI App    │         │
│  │  (Web/Mobile)   │         │  (API Layer)    │         │
│  └─────────────────┘         └────────┬────────┘         │
│                                       │                   │
│                              ┌────────▼────────┐         │
│                              │ Business Logic  │         │
│                              │ (Service Layer) │         │
│                              └────────┬────────┘         │
│                                       │                   │
│                              ┌────────▼────────┐         │
│                              │  SQLAlchemy     │         │
│                              │  (Data Access)  │         │
│                              └────────┬────────┘         │
│                                       │                   │
│                              ┌────────▼────────┐         │
│                              │   PostgreSQL    │         │
│                              │   (Database)    │         │
│                              └─────────────────┘         │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Architectural Principles

1. **Separation of Concerns:** Each layer has a single, well-defined responsibility
2. **Dependency Injection:** Explicit dependency management for testability
3. **Type Safety:** Pydantic models and SQLAlchemy schemas ensure type correctness
4. **Traceability:** Every component traces back to approved requirements
5. **Scalability Ready:** Design supports horizontal scaling, caching, and async operations

---

## 3. Phase-Based Roadmap

### 3.1 Phase 1 (MVP) - FR-001 Implementation

**Scope:** Implement ONLY FR-001 (Retrieve Vehicle Details by ID)

**In Scope:**
- `GET /api/v1/vehicles/{vehicle_id}` endpoint
- VehicleService.get_vehicle_by_id() business logic
- VehicleRepository.find_by_id() database access
- Layered architecture (API / Service / Repository / DB)
- Input validation and error handling
- Unit and integration tests
- Docker Compose local development environment

**Out of Scope (Defer to Phase 2):**
- List Vehicles endpoint (`GET /api/v1/vehicles`)
- Create Vehicle endpoint (`POST /api/v1/vehicles`)
- Update Vehicle endpoint (`PATCH /api/v1/vehicles/{id}`)
- Delete Vehicle endpoint (`DELETE /api/v1/vehicles/{id}`)
- Redis in-memory caching
- Production Kubernetes deployment
- Rate limiting at middleware level
- Distributed tracing and observability
- Advanced monitoring and alerting
- Multi-tenant or user authentication

### 3.2 Phase 2+ (Future Enhancements)

**Planned Extensions:**
- List/create/update/delete operations for full CRUD
- Redis caching layer for hot vehicle queries
- User authentication and authorization (OAuth2/JWT)
- Advanced search and filtering
- Production Kubernetes orchestration
- API rate limiting and DDoS protection
- Distributed tracing (OpenTelemetry/Jaeger)
- Advanced monitoring (Prometheus + Grafana)

### 3.3 Architectural Decisions Approved for Phase 1

The layered architecture design is approved and extensible. All future Phase 2+ additions will follow the same layered pattern without requiring architectural changes.

---

## 4. Architectural Goals & Drivers

| Driver | Goal | Influence on Architecture |
|--------|------|--------------------------|
| **FR-001** | Retrieve vehicle details by ID | Drives core API endpoint design and database schema |
| **Performance** | Sub-100ms response times (after indexing) | Database indexing on ID; async I/O in FastAPI |
| **Reliability** | Graceful error handling | Centralized error middleware, meaningful error responses |
| **Maintainability** | Clear code structure | Layered architecture, type hints, comprehensive testing |
| **Extensibility** | Support future features | Modular design, repository pattern, plugin-ready |
| **Security** | Protect vehicle data | Input validation, SQL injection prevention via parameterized queries |

---

## 4. Recommended Architecture

### 4.1 Layered Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│                     (app/api/routes.py)                          │
│                                                                   │
│  [PHASE 1 - MVP]                                                 │
│  GET /api/v1/vehicles/{vehicle_id}  ◄─ FastAPI Router            │
│                                                                   │
│  [PHASE 2+ - Future Features]                                    │
│  GET /api/v1/vehicles               ◄─ List Vehicles             │
│  POST /api/v1/vehicles              ◄─ Create Vehicle (Admin)    │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│                   Service Layer                                   │
│                (app/services/vehicle_service.py)                  │
│                                                                   │
│  VehicleService:                                                  │
│    [PHASE 1]                                                      │
│    - get_vehicle_by_id(id) -> VehicleDTO                         │
│    [PHASE 2+]                                                     │
│    - list_vehicles() -> List[VehicleDTO]                         │
│    - create_vehicle(data) -> VehicleDTO                          │
│    - validate_vehicle_data(data) -> bool                         │
│    - calculate_price_with_fees(base_price: float) -> float       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│               Data Access Layer                                   │
│           (app/db/repositories/vehicle_repository.py)             │
│                                                                   │
│  VehicleRepository:                                               │
│    [PHASE 1]                                                      │
│    - find_by_id(id) -> Vehicle (ORM)                             │
│    [PHASE 2+]                                                     │
│    - find_all() -> List[Vehicle]                                 │
│    - save(vehicle) -> Vehicle                                    │
│    - delete(id) -> bool                                          │
└───────────────────┬─────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│                    Database Layer                                 │
│                  (PostgreSQL + SQLAlchemy)                        │
│                                                                   │
│  Table: vehicles                                                  │
│    - id (PK)                                                      │
│    - make, model, year, price, transmission, fuel_type           │
│    - created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Key Components and Responsibilities

#### 4.2.1 API Layer (`app/api/routes.py`)
- **Responsibility:** Handle HTTP requests/responses, route requests to services
- **Technologies:** FastAPI, Pydantic
- **Key Classes/Functions:**
  - `router: APIRouter` — FastAPI router for vehicle endpoints
  - `get_vehicle(vehicle_id: int) -> VehicleResponse` — Fetch single vehicle [**Traces to FR-001**]
  - `list_vehicles(skip: int, limit: int) -> List[VehicleResponse]` — Fetch vehicle list
  - Request/response validation via Pydantic schemas

**Responsibilities:**
- Validate HTTP request parameters (vehicle_id is integer, within valid range)
- Convert request data to domain objects
- Call service layer to retrieve/process data
- Convert service results to API response DTOs (Data Transfer Objects)
- Handle and return appropriate HTTP status codes (200, 404, 400, 500)

#### 4.2.2 Service Layer (`app/services/vehicle_service.py`)
- **Responsibility:** Implement business logic, coordinate data operations, enforce domain rules
- **Technologies:** Python, type hints, dependency injection
- **Key Classes:**
  - `VehicleService` — Orchestrate vehicle operations
  - Methods:
    - `get_vehicle_by_id(vehicle_id: int) -> VehicleDTO` — [**Traces to FR-001**]
    - `list_vehicles() -> List[VehicleDTO]`
    - `validate_vehicle_data(data: dict) -> bool`
    - `calculate_price_with_fees(base_price: float) -> float` — Example extensible method

**Responsibilities:**
- Coordinate calls to repository layer
- Apply business rules and validation
- Transform data between formats (ORM ↔ DTO)
- Cache-friendly design (support memo-ization)
- Provide consistent error handling

#### 4.2.3 Data Access Layer (`app/db/repositories/vehicle_repository.py`)
- **Responsibility:** Abstract database operations, provide repository pattern
- **Technologies:** SQLAlchemy ORM, PostgreSQL
- **Key Classes:**
  - `VehicleRepository` — CRUD operations for vehicles
  - Methods:
    - `find_by_id(vehicle_id: int) -> Vehicle` — [**Traces to FR-001**]
    - `find_all(skip: int = 0, limit: int = 100) -> List[Vehicle]`
    - `save(vehicle: Vehicle) -> Vehicle`
    - `delete(vehicle_id: int) -> bool`

**Responsibilities:**
- Execute parameterized SQL queries (prevent SQL injection)
- Transform database rows to ORM objects
- Manage database sessions and transactions
- Provide indexing guidance (ID index for FR-001 performance)

#### 4.2.4 Database Layer (`app/db/models.py`)
- **Responsibility:** Define data schema and ORM mappings
- **Technologies:** SQLAlchemy, PostgreSQL
- **Key Classes:**
  - `Vehicle` ORM class
  - Attributes: `id`, `make`, `model`, `year`, `price`, `transmission`, `fuel_type`, `created_at`, `updated_at`
  - Indexes: Unique index on `id` (PK), supporting FR-001 performance

**Responsibilities:**
- Define table schema in Python via ORM
- Specify relationships and constraints
- Provide type hints for all attributes
- Support migrations via Alembic

---

## 5. Data Flow for FR-001

### 5.1 Sequence Diagram: Get Vehicle Details by ID

```
┌─────────┐         ┌──────────┐        ┌─────────────┐      ┌──────────┐      ┌───────────┐
│ Client  │         │  FastAPI │        │   Service   │      │Repository│      │  Database │
└────┬────┘         └─────┬────┘        └──────┬──────┘      └─────┬────┘      └─────┬─────┘
     │                    │                     │                   │               │
     │ GET /api/v1/       │                     │                   │               │
     │ vehicles/{id}      │                     │                   │               │
     ├───────────────────►│                     │                   │               │
     │                    │ Validate ID         │                   │               │
     │                    ├─────┐               │                   │               │
     │                    │◄────┘               │                   │               │
     │                    │                     │                   │               │
     │                    │ get_vehicle_by_id() │                   │               │
     │                    ├────────────────────►│                   │               │
     │                    │                     │ find_by_id()      │               │
     │                    │                     ├──────────────────►│               │
     │                    │                     │                   │ SELECT * FROM│
     │                    │                     │                   │ vehicles     │
     │                    │                     │                   │ WHERE id = ? │
     │                    │                     │                   ├──────────────►
     │                    │                     │                   │               │
     │                    │                     │                   │◄──────────────┤
     │                    │                     │                   │ Vehicle row  │
     │                    │                     │◄──────────────────┤               │
     │                    │                     │ VehicleDTO        │               │
     │                    │◄────────────────────┤                   │               │
     │                    │ VehicleResponse     │                   │               │
     │◄───────────────────┤                     │                   │               │
     │ 200 + JSON         │                     │                   │               │
     │                    │                     │                   │               │
```

### 5.2 Data Transformation Pipeline

```
HTTP Request
    ↓
    └─ FastAPI validates request parameter (vehicle_id: int)
    ↓
VehicleService.get_vehicle_by_id(vehicle_id)
    ↓
    └─ Check cache (optional) for quick retrieval
    ↓
VehicleRepository.find_by_id(vehicle_id)
    ↓
    └─ Execute parameterized SQL: SELECT * FROM vehicles WHERE id = %s
    ↓
SQLAlchemy ORM maps row to Vehicle entity
    ↓
    └─ Vehicle(id=1, make="Toyota", model="Camry", year=2023, ...)
    ↓
Service transforms ORM → DTO (VehicleDTO)
    ↓
    └─ VehicleDTO(id=1, make="Toyota", model="Camry", year=2023, ...)
    ↓
API layer transforms DTO → Response JSON
    ↓
    └─ { "id": 1, "make": "Toyota", "model": "Camry", ... }
    ↓
HTTP 200 Response
```

---

## 6. Technology Choices and Rationale

| Component | Technology | Rationale | Trade-off |
|-----------|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Modern, fast, async-ready, auto-generated API docs, built-in validation (Pydantic) | Learning curve for developers unfamiliar with async Python |
| **ORM** | SQLAlchemy 2.0+ | Industry standard, type-safe queries, prevents SQL injection, flexible | Performance overhead vs. raw SQL (mitigated by indexing) |
| **Database** | PostgreSQL 13+ | ACID compliance, JSON support, excellent indexing, open-source, mature | Operational complexity vs. managed cloud databases |
| **Container Runtime** | Docker + Docker Compose | Consistent dev/staging/prod environments, easy scaling, isolation | Operational overhead, requires container knowledge |
| **API Documentation** | OpenAPI/Swagger | Auto-generated from FastAPI, interactive, reduces documentation debt | Requires discipline to keep specs updated |
| **Data Validation** | Pydantic | Built into FastAPI, type hints, automatic serialization/deserialization | Slight overhead for simple types |
| **Async/Concurrency** | asyncio + aiofiles | Handles I/O efficiently, supports high concurrency, native Python | Async complexity can mask bugs; requires careful error handling |

---

## 7. Copilot SDLC Agents & Artifacts

This architecture document is produced by the **Architect Agent** (Step 2) and serves as input to:

| Downstream Agent | Input Use | Output Artifact |
|---|---|---|
| **Design Review Agent** (Step 3) | Validate component boundaries, data contracts, error handling strategy | artifacts/design-review.md |
| **Planner Agent** (Step 4) | Define implementation tasks, estimate effort, prioritize endpoints | artifacts/impl-plan.md |
| **Implementation Agent** (Step 5) | Code generation for routes, services, repositories, tests | source code + test suite |
| **Verification Agent** (Step 7) | Test plan for each data flow, edge cases, integration tests | test suite + verification report |

---

## 8. Traceability Matrix

### 8.1 Requirement-to-Component Mapping

| Requirement | Component | Method | API Endpoint | Details |
|---|---|---|---|---|
| **FR-001: Retrieve Vehicle Details by ID** | VehicleService | `get_vehicle_by_id(vehicle_id: int) -> VehicleDTO` | `GET /api/v1/vehicles/{vehicle_id}` | Returns make, model, year, price, transmission, fuel_type |
| **AC-001: Return all vehicle attributes** | VehicleService + API | Response schema includes all 6 attributes | Same endpoint | Response DTO must include all AC-001 fields |

### 8.2 Data Contract: FR-001 Response

```python
# Request
GET /api/v1/vehicles/{vehicle_id}

# Response (200 OK)
{
  "id": 1,
  "make": "Toyota",           # FR-001
  "model": "Camry",           # FR-001
  "year": 2023,               # FR-001
  "price": 28500.00,          # FR-001
  "transmission": "Automatic", # FR-001
  "fuel_type": "Gasoline",    # FR-001
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}

# Error Response (404 Not Found)
{
  "detail": "Vehicle with ID 999 not found"
}

# Error Response (400 Bad Request)
{
  "detail": "Vehicle ID must be a positive integer"
}
```

---

## 9. Security Considerations

### 9.1 Security Threats & Mitigations

| Threat | Mitigation | Component |
|--------|-----------|-----------|
| **SQL Injection** | Use parameterized queries (SQLAlchemy) | Repository Layer |
| **Invalid Input** | Pydantic type validation, range checks | API Layer |
| **Missing Vehicle** | Return 404 gracefully, never expose DB errors | Service + API Layer |
| **Unauthorized Access** | (Future) Add authentication via JWT/OAuth2 | API Layer |
| **Data Exposure** | (Future) Implement field-level encryption for sensitive data | Database + Service Layer |
| **DDoS** | (Future) Implement rate limiting and request throttling | API Gateway |

### 9.2 Data Protection

- **In Transit:** Use HTTPS/TLS in production (handled by API Gateway/Load Balancer)
- **At Rest:** PostgreSQL native encryption, regular backups
- **Access Control:** Database credentials stored in environment variables, never committed to source

---

## 10. Error Handling & Observability Strategy

### 10.1 Error Handling Architecture

All exceptions in the request pipeline must be caught and transformed into safe, consistent error responses. This prevents information disclosure and provides clear feedback to API consumers.

#### 10.1.1 Centralized Error Handler (Middleware)

**Location:** `app/middleware/error_handler.py`

**Responsibility:** Catch all unhandled exceptions and return standardized error envelope

**Implementation:**

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

async def error_handler_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValueError as e:
        # Invalid input (vehicle_id not integer, etc.)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e), "error_code": "VALIDATION_ERROR"}
        )
    except VehicleNotFound as e:
        # Vehicle with ID does not exist
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Vehicle not found", "error_code": "NOT_FOUND"}
        )
    except DatabaseError as e:
        # Connection, timeout, or query error
        logger.error(f"Database error: {e}")  # Log internally
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
        )
```

**Key Principles:**
- Never expose database schema, stack traces, or internal detail to client
- Log full error details securely server-side for debugging
- Return consistent error envelope: `{"detail": "...", "error_code": "..."}`
- Map specific exceptions to appropriate HTTP status codes

#### 10.1.2 HTTP Status Code Mapping

| Exception | HTTP Status | Error Code | Response |
|-----------|-------------|-----------|----------|
| `ValueError` (invalid vehicle_id type) | 400 Bad Request | `VALIDATION_ERROR` | `{"detail": "Vehicle ID must be a positive integer"}` |
| `VehicleNotFound` (ID doesn't exist) | 404 Not Found | `NOT_FOUND` | `{"detail": "Vehicle not found"}` |
| `DatabaseConnectionError` | 500 Internal Server Error | `INTERNAL_ERROR` | `{"detail": "Internal server error"}` |
| `DatabaseTimeoutError` | 503 Service Unavailable | `SERVICE_UNAVAILABLE` | `{"detail": "Service temporarily unavailable"}` |
| Unexpected exception | 500 Internal Server Error | `INTERNAL_ERROR` | `{"detail": "Internal server error"}` |

### 10.2 Logging Strategy

**Framework:** Python's built-in `logging` module with structured JSON output

**Levels:**
- `DEBUG`: Request parameters, query details (development only, never in production)
- `INFO`: API requests received, responses sent
- `WARNING`: Recoverable errors, validation failures
- `ERROR`: Unhandled exceptions, database errors
- `CRITICAL`: System-level failures

**Structured Logging Format:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "logger": "app.services.vehicle_service",
  "trace_id": "abc123def456",
  "message": "Vehicle not found",
  "vehicle_id": 999,
  "exception": "VehicleNotFound"
}
```

**Trace ID Propagation:**
- Assign unique trace_id to each HTTP request (via middleware)
- Propagate trace_id through all layers (service, repository)
- Include trace_id in all log messages for end-to-end request tracing

---

## 11. Configuration Management

### 11.1 Environment-Based Configuration

**Principle:** Never hardcode secrets or environment-specific settings. Use environment variables exclusively.

**Configuration File:** `app/config.py`

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/carportal"
    )
    
    # API
    API_TITLE: str = "Car Portal Vehicle Details API"
    API_VERSION: str = "1.0.0"
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 11.2 Environment Variables Template

**File:** `.env.example` (commit to repo, never commit actual `.env`)

```bash
# Database Configuration
DATABASE_URL=postgresql://carportal_user:password@localhost:5432/carportal_dev

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000

# (Add secrets like API keys, tokens here; never commit)
# SECRET_KEY=your-secret-key-here
```

### 11.3 .gitignore Configuration

**Commit to repo:**

```
# Environment variables (never commit actual secrets)
.env
.env.local
.env.*.local

# IDE settings
.vscode/
.idea/

# Python artifacts
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
.coverage

# Database
db_data/
```

### 11.4 Secrets Management Best Practices

**For Development:**
- Use `.env.example` as a template
- Create local `.env` file with development credentials
- Add `.env` to `.gitignore` (prevents accidental commits)

**For Production:**
- Use cloud provider's secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- Never commit secrets to any repository
- Inject secrets as environment variables at runtime
- Rotate credentials regularly
- Audit secret access

---

## 12. Testing Strategy (Phase 1)

### 10.1 Performance Optimizations

1. **Database Indexing**
   - Primary Key index on `vehicles.id` (automatic in PostgreSQL)
   - Optional: Composite index on `(make, model, year)` for future list filtering

2. **Caching Strategy**
   - L1 Cache: In-memory cache (Redis) for frequently accessed vehicles (optional, Phase 2)
   - L2 Cache: HTTP cache headers (`Cache-Control: max-age=300`) for client-side caching
   - Cache invalidation: On vehicle update, clear cache entry

3. **Query Optimization**
   - Use `SELECT id, make, model, year, price, transmission, fuel_type` to avoid fetching extra columns
   - Connection pooling: SQLAlchemy manages connection pool (default 20 connections)

4. **Async I/O**
   - FastAPI supports `async def` endpoints for non-blocking I/O
   - Database queries can be offloaded to thread pool or async driver (asyncpg)

### 10.2 Scalability Architecture (Future)

```
                      ┌─────────────┐
                      │ Load Balancer│
                      └──────┬──────┘
                             │
                 ┌───────────┼───────────┐
                 │           │           │
            ┌────▼───┐  ┌────▼───┐  ┌──▼─────┐
            │FastAPI │  │FastAPI │  │FastAPI │
            │Replica1│  │Replica2│  │Replica3│
            └────┬───┘  └────┬───┘  └──┬─────┘
                 │           │         │
                 └───────────┬────────┘
                             │
                      ┌──────▼──────┐
                      │ Redis Cache │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │ PostgreSQL  │
                      │   Primary   │
                      └──────┬──────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              ┌─────▼─────┐     ┌─────▼─────┐
              │PostgreSQL  │     │PostgreSQL  │
              │ Read Replica1   │ Read Replica2
              └────────────┘     └────────────┘
```

---

## 11. Deployment Topology

### 11.1 Development Environment (Current)

```
┌─────────────────────────────────────────────────┐
│         Developer Machine                       │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │       Docker Compose                     │  │
│  │                                          │  │
│  │  ┌─────────────┐   ┌─────────────────┐ │  │
│  │  │ FastAPI     │───│  PostgreSQL    │ │  │
│  │  │ (Port 8000) │   │  (Port 5432)   │ │  │
│  │  └─────────────┘   └─────────────────┘ │  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  docker-compose up -d                         │
└─────────────────────────────────────────────────┘
```

**Services:**
- **FastAPI:** Runs on `http://localhost:8000`, Swagger UI on `http://localhost:8000/docs`
- **PostgreSQL:** Runs on `localhost:5432`, persistent volume `db_data`
- **Network:** Docker bridge network `carportal-network`

### 11.2 Production Environment (Recommended)

```
┌────────────────────────────────────────────────────────────┐
│                     Cloud Provider (AWS/GCP/Azure)         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Kubernetes Cluster                         │ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐   │ │
│  │  │      Load Balancer / Ingress Controller     │   │ │
│  │  └──────────────────┬──────────────────────────┘   │ │
│  │                     │                              │ │
│  │  ┌──────────────────▼─────────────────────────┐   │ │
│  │  │         Service Mesh (optional)            │   │ │
│  │  │         (Istio for observability)          │   │ │
│  │  └──────────────────┬─────────────────────────┘   │ │
│  │                     │                              │ │
│  │   ┌─────────────────┼─────────────────┐           │ │
│  │   │                 │                 │           │ │
│  │ ┌─▼──────┐     ┌──────────┐     ┌──▼─────┐       │ │
│  │ │FastAPI │     │ FastAPI  │     │FastAPI │       │ │
│  │ │Pod (3) │     │ Pod (3)  │     │Pod (3) │       │ │
│  │ └─┬──────┘     └──────┬───┘     └──┬─────┘       │ │
│  │   │                   │            │             │ │
│  │   └───────────────────┼────────────┘             │ │
│  │                       │                          │ │
│  │ ┌─────────────────────▼──────────────────────┐  │ │
│  │ │  Managed PostgreSQL Service (AWS RDS)      │  │ │
│  │ │  - Multi-AZ deployment                     │  │ │
│  │ │  - Automated backups                       │  │ │
│  │ │  - Read replicas for scaling               │  │ │
│  │ └────────────────────────────────────────────┘  │ │
│  │                                                  │ │
│  │ ┌──────────────────────────────────────────┐    │ │
│  │ │  Redis Cache (AWS ElastiCache)           │    │ │
│  │ │  - Multi-AZ replication                  │    │ │
│  │ │  - Auto-failover                        │    │ │
│  │ └──────────────────────────────────────────┘    │ │
│  │                                                  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Deployment Configuration:**
- **Container Orchestration:** Kubernetes with 3+ replicas of FastAPI pods
- **Database:** Managed PostgreSQL (AWS RDS, Azure Database, or GCP Cloud SQL)
- **Caching:** Managed Redis service for distributed caching
- **API Gateway:** Nginx Ingress or AWS API Gateway for routing, rate limiting, CORS
- **Monitoring:** Prometheus + Grafana for metrics, ELK stack for logs
- **CI/CD:** GitHub Actions for automated testing and deployment

---

## 12. Project Structure

### 12.1 Directory Layout (Proposed)

```
carportal-app-capstone/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app initialization
│   ├── config.py                        # Configuration (env vars, secrets)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/                      # API Layer
│   │   │   ├── __init__.py
│   │   │   └── vehicles.py              # Vehicle endpoints (FR-001)
│   │   └── schemas/                     # Pydantic models
│   │       ├── __init__.py
│   │       └── vehicle_schemas.py       # Request/response DTOs
│   ├── services/                        # Service Layer
│   │   ├── __init__.py
│   │   ├── vehicle_service.py           # Business logic (FR-001)
│   │   └── base_service.py              # Base service class
│   └── db/
│       ├── __init__.py
│       ├── database.py                  # Database connection, session mgmt
│       ├── models.py                    # ORM models
│       └── repositories/                # Data Access Layer
│           ├── __init__.py
│           ├── base_repository.py       # Generic CRUD methods
│           └── vehicle_repository.py    # Vehicle-specific queries
├── migrations/                          # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_vehicle_service.py
│   │   └── test_vehicle_repository.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_vehicle_api.py
│   └── e2e/
│       ├── __init__.py
│       └── test_vehicle_workflows.py
├── data/
│   ├── cars.json
│   ├── users.json
│   └── (other data files)
├── docker-compose.yml                  # Local dev environment
├── Dockerfile                          # Container image
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── .github/
│   ├── agents/
│   ├── instructions/
│   ├── prompts/
│   └── skills/
├── artifacts/
│   ├── requirements.md                 # Step 1 output (approved)
│   ├── architecture.md                 # Step 2 output (this document)
│   ├── design-review.md                # Step 3 output (pending)
│   ├── impl-plan.md                    # Step 4 output (pending)
│   └── CHANGELOG.md                    # Step 8 output (pending)
└── README.md                           # Project documentation
```

### 12.2 Key File Descriptions

| File | Purpose | Trace to FR |
|------|---------|------------|
| `app/api/routes/vehicles.py` | FastAPI route handlers | FR-001 |
| `app/services/vehicle_service.py` | Business logic orchestration | FR-001 |
| `app/db/repositories/vehicle_repository.py` | Database queries | FR-001 |
| `app/db/models.py` | ORM model definition | FR-001 |
| `tests/integration/test_vehicle_api.py` | E2E test for FR-001 | FR-001 |

---

## 13. Assumptions

1. **Database Connectivity:** PostgreSQL is available and reachable from the FastAPI container
2. **Vehicle Data:** Vehicles table is pre-populated with the 6 required attributes (make, model, year, price, transmission, fuel_type)
3. **Existing Infrastructure:** Docker, Docker Compose, and Python 3.8+ are available in dev environment
4. **Authentication (Out-of-Scope):** Initial implementation assumes no authentication; future phases will add OAuth2/JWT
5. **Data Integrity:** Vehicle ID values are stable, unique, and never reused
6. **Scalability Threshold:** System can handle up to 10,000 requests/second per pod with 3+ replicas
7. **Backup & Recovery:** PostgreSQL automated backups are configured externally (separate from this architecture)

---

## 15. Open Questions & Follow-up Decisions

| Question | Impact | Status | For Step 3 (Design Review) |
|----------|--------|--------|-----|
| **Q1: Vehicle ID Type (integer vs. UUID)?** | API contract, database indexing strategy | ✅ **APPROVED:** Use sequential integers. Rationale: simpler indexing, fits current schema. Revisit for multi-tenant phase. | Implemented in Phase 1 design |
| **Q2: Soft-deletes vs. hard-deletes?** | Data retention, audit trail requirements | ⚠️ **DEFERRED to Phase 2:** Out-of-scope for Phase 1. Phase 2 will define deletion policy. | Not needed for get-by-ID |
| **Q3: Vehicle inventory size (estimated rows)?** | Index strategy, caching effectiveness, query performance | ⚠️ **ESTIMATE:** 100K-1M vehicles initially. Phase 3 will load test with production data. | Confirm with data owner |
| **Q4: API update semantics (PATCH vs. PUT)?** | API contract, validation complexity | ⚠️ **DEFERRED to Phase 2:** Out-of-scope for Phase 1 (no updates in FR-001). Phase 2 will define HTTP method semantics. | Not needed for get-by-ID |
| **Q5: Field-level encryption required?** | Encryption library, key management, query performance | ⚠️ **DEFERRED to Phase 2:** Out-of-scope for Phase 1. Security review will determine encryption needs. | Not needed for MVP |
| **Q6: API versioning strategy (URL vs. header)?** | URL structure, backward compatibility | ✅ **APPROVED:** URL-based versioning (/api/v1/...). Supports future versions without breaking clients. | Implemented in Phase 1 design |

---

## 16. Risks & Mitigation Strategies

| Risk | Probability | Impact | Mitigation | Phase |
|------|-------------|--------|-----------|-------|
| **Performance degradation with large vehicle tables** | Medium | High | Implement indexing strategy in Phase 1 design review; load test with 1M+ row dataset in Phase 3 | 1 |
| **Database connection pool exhaustion** | Low | High | Validate pool size (default 20) against expected concurrent users in Phase 1; configure via environment variable | 1 |
| **N+1 Query Problem in related entities** | Low | Low | For Phase 1, only single vehicle fetch (no N+1). Phase 2+ will use SQLAlchemy eager loading | 2+ |
| **Unhandled exceptions leak database schema** | Low | High | Implement centralized error handler in Phase 1 that masks internal details; log securely server-side | 1 |
| **API rate limiting missing, leading to abuse** | Medium | Medium | Out-of-scope for Phase 1. Implement at API gateway level in Phase 2 before production | 2+ |
| **Async bugs in FastAPI handlers** | Medium | Medium | Comprehensive async error handling and concurrency tests in Phase 1; integration tests validate request isolation | 1 |

---

## 17. Next Steps

### 17.1 For Step 3 (Design Review Agent)

The Design Review Agent will:
- ✅ Validate component boundaries and data contracts for FR-001
- ✅ Review error handling strategy and edge cases
- ✅ Assess security threat model completeness (SQL injection, input validation)
- ✅ Confirm technology choices align with requirements
- ✅ Identify gaps in FR-001 coverage
- ✅ Produce `artifacts/design-review.md`

### 17.2 For Step 4 (Planner Agent)

The Planner Agent will:
- [ ] Break Phase 1 architecture into implementation tasks
- [ ] Estimate effort per component (routes, service, repository, tests)
- [ ] Define implementation order and dependencies
- [ ] Create test strategy for FR-001 (unit / integration / E2E)
- [ ] Produce `artifacts/impl-plan.md`

### 17.3 For Step 5 (Implementation Agent)

The Implementation Agent will:
- [ ] Generate code scaffolding from Phase 1 architecture
- [ ] Implement VehicleRepository.find_by_id() first
- [ ] Implement VehicleService.get_vehicle_by_id() second
- [ ] Implement API route `GET /api/v1/vehicles/{vehicle_id}` third
- [ ] Implement centralized error handler middleware
- [ ] Write unit + integration + E2E tests for FR-001
- [ ] Achieve >80% code coverage
- [ ] Produce source code + test suite

---

## 18. Summary Table: Phase 1 Architecture at a Glance

| Aspect | Phase 1 Decision | Phase 2+ Extension |
|--------|----------|---|
| **Architecture Style** | Layered (API / Service / Repository / Database) | Same structure; add cache layer |
| **Primary Language** | Python 3.8+ | Same |
| **Web Framework** | FastAPI with async support | Same |
| **ORM** | SQLAlchemy 2.0+ | Same |
| **Database** | PostgreSQL 13+ | Same |
| **Containerization** | Docker & Docker Compose | Docker + Kubernetes |
| **Dev Env** | docker-compose.yml (local) | Same for Phase 1 |
| **Prod Env** | Docker on cloud VM (Phase 1) | Kubernetes on cloud |
| **API Style** | RESTful with JSON | Same |
| **Versioning** | URL-based (/api/v1/...) | Support /api/v2/... |
| **Authentication** | None (Phase 1) | JWT/OAuth2 (Phase 2) |
| **Caching** | None (Phase 1) | Redis (Phase 2) |
| **Monitoring** | Basic logging (Phase 1) | Prometheus + Grafana (Phase 2) |
| **Rate Limiting** | None (Phase 1) | API Gateway middleware (Phase 2) |
| **FR-001 Endpoint** | `GET /api/v1/vehicles/{vehicle_id}` | Deprecated in v2 if schema changes |
| **FR-001 Response Time Target** | < 100ms p95 (no cache) | < 50ms p95 (with Redis) |

---

## 19. Approval Checklist

Before proceeding to Step 3 (Design Review), confirm:

- [x] Architecture addresses all requirements in `artifacts/requirements.md` (FR-001 fully covered)
- [x] Technology stack is justified and appropriate (FastAPI, SQLAlchemy, PostgreSQL)
- [x] Layered architecture is clear and implementable
- [x] Data flow for FR-001 is documented (sequence diagram, data transformation pipeline)
- [x] Security considerations are identified (SQL injection, error handling, input validation)
- [x] Phase 1 scope is bounded to FR-001 only
- [x] Phase 2+ roadmap is defined
- [x] Error handling and configuration strategies documented
- [x] Traceability to FR-001 is complete
- [x] Open questions are resolved or deferred with clear rationale

---

**Document Status:** Updated for Design Review (Step 3)  
**Created by:** Architect Agent (Step 2)  
**Updated by:** Design Review Agent findings  
**Date:** 2026-09-19  
**Next Review Gate:** Step 4 - Planner Agent for implementation planning
