---
description: "FastAPI backend boundaries and JSON persistence conventions for route, application, and data changes."
applyTo: "app/**/*.py"
---

# FastAPI Backend Boundaries

Applies to backend production code under `app/`.

## Route layer: `app/main.py`

- Define FastAPI routes, request parsing, response status codes, and HTTP error mapping here.
- Use Pydantic models from `app/db/models.py` for request validation and response contracts.
- Keep route handlers thin: validate the request, call application logic, and translate domain outcomes into HTTP responses.
- Do not put JSON file reads, recommendation matching, or persistence details directly in route handlers.

## Application and data operations: `app/api/api.py`

- Keep recommendation logic and application operations in `app/api/api.py` unless an approved artifact introduces another service module.
- Do not import FastAPI request/response objects or raise transport-specific errors from application functions; return values or explicit domain outcomes for the route layer to map.
- Keep functions focused and use shared helpers for repeated JSON loading, validation, and lookup behavior.
- Handle missing files, malformed JSON, missing records, and invalid business inputs deliberately. Do not leak raw exceptions or print operational errors.

## Persistence boundary: `data/*.json`

- The current persistence mechanism is JSON files under `data/`; do not introduce PostgreSQL, SQLAlchemy, or another database without an approved architecture or implementation task.
- Resolve paths consistently from the repository root or an explicit project path. Do not add new working-directory assumptions.
- Treat loaded JSON as untrusted data: validate required fields before indexing or matching, and handle empty collections safely.
- Avoid mutating source data in memory unless the operation explicitly requires persistence and the write behavior is specified.

## Change and validation rules

- Preserve the existing `main.py` -> `api.py` -> `data/` flow for scoped changes.
- For endpoint behavior changes, update focused tests under `test/` and run `pytest test/test.py` from the repository root.
- Read [code-quality.instructions.md](code-quality.instructions.md) for shared security and error-handling rules and [tests.instructions.md](tests.instructions.md) for test expectations.
