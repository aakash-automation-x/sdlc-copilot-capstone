# Car Portal — Vehicle Recommendation System

A lightweight FastAPI application that helps users find vehicle recommendations based on questionnaire answers. The application exposes REST-style endpoints for retrieving users, questions, answer alternatives, vehicle recommendations, and saved results.

The project currently uses JSON files as its data store and is intended for local development and demonstration purposes.

## Features

- FastAPI-based HTTP API
- Vehicle recommendations based on:
  - Vehicle category
  - Budget range
  - Fuel type
- Question and answer alternative endpoints
- User and saved-result endpoints
- Pydantic request validation
- Automated endpoint tests with `pytest`
- File-based persistence using JSON documents

## Technology Stack

- Python 3
- FastAPI `0.46.0`
- Uvicorn `0.11.1`
- Pydantic, provided through the FastAPI dependency
- Pytest `5.3.2`
- Requests `2.22.0`
- JSON files for application data

## Requirements

- Python 3
- `pip`
- A virtual-environment tool recommended for local development

The exact Python 3 minor version is not pinned in the repository.

## Installation

Clone the repository and change into its directory:

```bash
git clone <repository-url>
cd <repository-directory>
```

Create and activate a virtual environment:

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI development server from the repository root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

The application entry point is:

```text
app.main:app
```

The interactive API documentation is available at:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

These are provided by FastAPI's default configuration.

## API Endpoints

### Health or root endpoint

```http
GET /
```

Returns a basic application message.

Example response:

```json
{
  "message": "Fast API in Python"
}
```

### List users

```http
GET /user
```

Returns the users stored in `data/users.json`.

### Retrieve a question

```http
GET /question/{position}
```

Returns the question whose position matches the supplied path parameter.

Example:

```http
GET /question/1
```

If no question is found, the endpoint returns HTTP `400` with:

```json
{
  "detail": "Error"
}
```

### Retrieve question alternatives

```http
GET /alternatives/{question_id}
```

Returns all alternatives associated with a question.

Example:

```http
GET /alternatives/1
```

### Create a recommendation request

```http
POST /answer
```

Accepts a JSON payload containing a user ID and a list of answers.

Request schema:

```json
{
  "user_id": 1,
  "answers": [
    {
      "question_id": 1,
      "alternative_id": 1
    },
    {
      "question_id": 2,
      "alternative_id": 6
    },
    {
      "question_id": 3,
      "alternative_id": 8
    }
  ]
}
```

The request is validated using the following models:

- `user_id`: integer
- `answers`: list of answer objects
- `question_id`: integer
- `alternative_id`: integer

A successful request returns HTTP `201` and a list of matching vehicles.

### Retrieve a saved result

```http
GET /result/{user_id}
```

Returns the saved result associated with the supplied user ID, including the matching user and vehicle records when available.

Example:

```http
GET /result/1
```

### Retrieve a vehicle by ID

```http
GET /vehicles/{vehicle_id}
```

Retrieves detailed information about a vehicle by its unique integer ID. This endpoint supports the vehicle retrieval feature (FR-001) with full attribute returns (AC-001) and proper error handling (AC-002).

**Path Parameters:**
- `vehicle_id` (integer, required): Vehicle ID to retrieve. Must be greater than 0. Invalid values (≤0, non-integer) return HTTP 422 validation error.

**Success Response (HTTP 200) — AC-001:**
Returns the vehicle with all 6 required attributes:

```json
{
  "id": 1,
  "make": "Volkswagen",
  "model": "ID.3",
  "year": 2023,
  "price": 35000.0,
  "transmission": "automatic",
  "fuel_type": "electric"
}
```

**Error Response (HTTP 404) — AC-002:**
When vehicle_id does not exist in the database:

```json
{
  "detail": "Vehicle not found"
}
```

**Validation Error Response (HTTP 422):**
When path parameter validation fails (e.g., vehicle_id ≤ 0 or non-integer):

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["path", "vehicle_id"],
      "msg": "ensure this value is greater than 0",
      "input": 0
    }
  ]
}
```

**Examples:**

```http
GET /vehicles/1
```

```http
GET /vehicles/5
```

## Data Files

Application data is stored in the `data/` directory:

| File | Purpose |
|---|---|
| `users.json` | User records |
| `questions.json` | Questionnaire questions |
| `alternatives.json` | Available answers for each question |
| `answers.json` | Answer-related data |
| `cars.json` | Vehicle catalog and vehicle attributes |
| `vehicles.json` | Vehicle details with all 6 attributes (id, make, model, year, price, transmission, fuel_type) |
| `results.json` | Saved user-to-vehicle results |

The application reads these files directly at runtime using Python's built-in `json` module. There is no SQL or NoSQL database configured.

Run the application from the repository root so the relative paths under `data/` resolve correctly.

## Requirements Traceability Matrix

This section maps functional requirements (FR), acceptance criteria (AC), and implementation tasks (TASK) to code locations and tests.

### FR-001: Vehicle Retrieval

**Requirement:** System shall retrieve vehicle details by ID.

**Acceptance Criteria:**

| AC | Description | Status | Code Location | Test Location |
|---|---|---|---|---|
| AC-001 | HTTP 200 success response includes all 6 vehicle attributes (id, make, model, year, price, transmission, fuel_type) | ✅ Implemented | [app/main.py](app/main.py#L46), [app/api/api.py](app/api/api.py#L32), [app/db/models.py](app/db/models.py#L36) | [test/test.py](test/test.py#L98), [test/test.py](test/test.py#L193) |
| AC-002 | HTTP 404 error response with "Vehicle not found" message when vehicle ID does not exist in database | ✅ Implemented | [app/api/api.py](app/api/api.py#L42) | [test/test.py](test/test.py#L154), [test/test.py](test/test.py#L231) |

**Implementation Tasks:**

| Task | Description | Status |
|---|---|---|
| TASK-001 | Update Vehicle Pydantic model with all 6 required attributes | ✅ Complete |
| TASK-002 | Implement data layer fetch_vehicle() function | ✅ Complete |
| TASK-003 | Implement service layer get_vehicle() with 404 handling | ✅ Complete |
| TASK-004 | Implement GET /vehicles/{vehicle_id} FastAPI endpoint | ✅ Complete |
| TASK-005 | Add Path validation (gt=0) | ✅ Complete |
| TASK-006 | Update requirements.txt with current dependency versions | ✅ Complete |
| TASK-007 | Verify logging is in place | ✅ Complete |
| TASK-008 | Add unit tests for service & data layers | ✅ Complete |
| TASK-009 | Add integration tests for endpoint | ✅ Complete |
| TASK-010 | Add documentation and inline code comments | ✅ Complete |

**Architecture Layer Mapping:**

```
GET /vehicles/{vehicle_id}  (Router, app/main.py)
         ↓
api.get_vehicle(id)         (Service, app/api/api.py)
         ↓
fetch_vehicle(id)           (Data, app/db/models.py)
         ↓
data/vehicles.json          (JSON file)
```

## Project Structure

App structure with layer responsibilities:

```text
.
├── app/
│   ├── main.py              # Router Layer (FastAPI endpoints, HTTP handling)
│   ├── api/
│   │   └── api.py           # Service Layer (business logic, error conversion)
│   └── db/
│       └── models.py        # Data Layer (Pydantic models, JSON I/O)
├── data/
│   ├── vehicles.json        # Vehicle data (6 attributes per AC-001)
│   ├── users.json
│   ├── questions.json
│   ├── alternatives.json
│   ├── cars.json
│   ├── answers.json
│   └── results.json
├── test/
│   └── test.py              # Test suite (unit + integration tests)
└── requirements.txt         # Python dependencies
```


│   ├── main.py
│   ├── api/
│   │   └── api.py
│   └── db/
│       └── models.py
├── artifacts/                        # Generated by the SDLC pipeline
│   ├── ORCHESTRATION_LOG.md
│   ├── requirements.md
│   ├── architecture.md
│   ├── design-review.md
│   ├── impl-plan.md
│   └── CHANGELOG.md
├── data/
│   ├── alternatives.json
│   ├── answers.json
│   ├── cars.json
│   ├── questions.json
│   ├── results.json
│   └── users.json
├── test/
│   ├── __init__.py
│   └── test.py
├── requirements.txt
├── README.md
└── userstory.md                      # User story reference (canonical source: Jira CAP-13)
```

### Important modules

#### `app/main.py`

Defines the FastAPI application instance and HTTP routes:

```python
app = FastAPI()
```

This module is used by Uvicorn with:

```bash
uvicorn app.main:app
```

#### `app/api/api.py`

Contains the application logic for:

- Reading users
- Reading questions
- Reading alternatives
- Generating vehicle recommendations
- Reading saved results

#### `app/db/models.py`

Defines the Pydantic request models:

- `Answer`
- `UserAnswer`

#### `test/test.py`

Contains endpoint tests using Starlette's `TestClient`.

## Running Tests

Run the test suite from the repository root:

```bash
pytest
```

The tests cover:

- The root endpoint
- User retrieval
- Valid question retrieval
- Invalid question handling
- Alternative retrieval
- Recommendation submission
- Result retrieval

To run the test file explicitly:

```bash
pytest test/test.py
```

## GitHub Copilot Agentic SDLC Pipeline

This repository includes a full **Agentic SDLC Pipeline** driven by GitHub Copilot.
Every phase of delivery — requirements, architecture, design review, planning,
implementation, code review, verification, and PR creation — is orchestrated through
Copilot agents, prompts, instructions, and skills in the `.github/` directory.

### Starting the pipeline

Open GitHub Copilot Chat in VS Code or GitHub.com and run:

```
/00-orchestrator
```

The orchestrator guides you through all 8 steps with human review gates at each stage.
Pipeline state is tracked in `artifacts/ORCHESTRATION_LOG.md`; SDLC deliverables are
written to the `artifacts/` directory.

### Pipeline configuration

| Location | Purpose |
|---|---|
| `.github/copilot-instructions.md` | Global pipeline overview and core principles |
| `.github/agents/*.agent.md` | One autonomous agent per SDLC step |
| `.github/prompts/00-orchestrator.prompt.md` | Single entry-point slash command |
| `.github/instructions/*.instructions.md` | Path-scoped coding and artifact standards |
| `.github/skills/*/SKILL.md` | On-demand domain knowledge loaded by agents |

See `.github/copilot-instructions.md` for the full pipeline stage table and working
agreements.

## Development Notes

The application uses synchronous functions and synchronous file I/O. Routes are defined with regular `def` functions rather than `async def`.

The current implementation is intentionally simple:

- There is no authentication or authorization.
- There is no database layer.
- There is no environment-based configuration.
- There is no custom middleware.
- There are no custom exception handlers.
- There are no API version prefixes.
- There is no Docker or deployment configuration included.
- JSON files are loaded during request processing.

For production use, the project would benefit from a database, structured configuration, authentication, stronger validation, logging, and deployment configuration.

## Recommendation Data

Vehicles in `data/cars.json` are matched using attributes such as:

- `category`
- `price`
- `fuel`

The available questionnaire categories and values are represented by the records in:

- `data/questions.json`
- `data/alternatives.json`

When changing the questionnaire or vehicle catalog, ensure that the values used by the alternatives correspond to the vehicle attributes in `data/cars.json`.

## API Documentation

After starting the server, use FastAPI's generated documentation:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

These interfaces can be used to inspect endpoints and submit requests interactively.

## Troubleshooting

### `FileNotFoundError` for a data file

Run Uvicorn from the repository root:

```bash
uvicorn app.main:app --reload
```

The application uses relative paths such as:

```text
data/users.json
data/cars.json
```

### Import errors

Confirm that dependencies are installed in the active virtual environment:

```bash
pip install -r requirements.txt
```

Also verify that commands are being run from the repository root.

### Port already in use

Start the server on another port:

```bash
uvicorn app.main:app --reload --port 8001
```

The API will then be available at:

```text
http://127.0.0.1:8001
```

## License

No license file or licensing information is currently included in the repository.