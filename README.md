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

## Data Files

Application data is stored in the `data/` directory:

| File | Purpose |
|---|---|
| `users.json` | User records |
| `questions.json` | Questionnaire questions |
| `alternatives.json` | Available answers for each question |
| `answers.json` | Answer-related data |
| `cars.json` | Vehicle catalog and vehicle attributes |
| `results.json` | Saved user-to-vehicle results |

The application reads these files directly at runtime using Python's built-in `json` module. There is no SQL or NoSQL database configured.

Run the application from the repository root so the relative paths under `data/` resolve correctly.

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── api.py
│   └── db/
│       └── models.py
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
└── userstory.md
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

### How to use

1. Start the server:
python -m uvicorn app.main:app --reload
1. Open http://localhost:8000/ui in your browser
2. Enter a Vehicle ID (1–10) and click Search — the card shows 5 attributes: Make, Model, Year, Fuel Type, Transmission pulled from GET /vehicles/{vehicle_id}.


## License

No license file or licensing information is currently included in the repository.