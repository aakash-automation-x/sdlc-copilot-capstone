# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run the application

```bash
uvicorn app.main:app --reload
```

Must be run from the repo root — the app uses relative paths like `data/users.json`. API available at `http://127.0.0.1:8000`. Interactive docs at `/docs`.

### Run tests

```bash
# All tests
pytest

# Gated test suite (used by deployment scripts)
pytest test/test_vehicle.py -v

# Single test file
pytest test/test.py -v

# Single test by name
pytest test/test_vehicle.py::test_get_vehicle_by_id_success -v
```

`test/test_vehicle.py` uses an in-memory SQLite database with dependency override — no running server or real DB needed. `test/test.py` uses Starlette `TestClient` against the full app and reads from `data/*.json` files.

### Database

The app defaults to `sqlite:///./carportal.db` (created at startup). Override via the `DATABASE_URL` environment variable for PostgreSQL in production.

### SDLC pipeline

```bash
# Start the full 8-step pipeline from Step 1
/00-orchestrator.prompt

# Resume at a specific step (e.g. after a pause)
/00-orchestrator.prompt resume step=<N>

# Check current pipeline state
/00-orchestrator.prompt status

# Restart the pipeline from scratch
/00-orchestrator.prompt restart
```

Each step produces a human review gate (Approve / Request Changes / Pause) before the next agent runs. State is tracked in `artifacts/ORCHESTRATION_LOG.md`.

---

## Hooks

Automated checks live in `.claude/hooks/scripts/` and are wired in `.claude/settings.json`. They run via bash on every relevant tool event.

| Event | Matcher | Script | What it does |
|-------|---------|--------|--------------|
| `PreToolUse` | `Edit\|Write` | `hook_pre_edit.py` | Blocks edits to existing test files |
| `PreToolUse` | `Bash(git commit*)` | `hook_scan_secrets.py` | Blocks commit if staged diff contains credential keywords (`password=`, `api_key=`, etc.) |
| `PostToolUse` | `Edit\|Write` | `hook_autoformat.py` | Auto-formats `.py` files with `ruff format` or `black` (skips if neither installed) |
| `PostToolUse` | `Edit\|Write` | `hook_post_edit.py` | Validates `data/*.json`, lints with ruff, runs `pytest test/test_vehicle.py` after any `app/` edit |
| `PostToolUse` | `Bash` | `hook_log_commands.py` | Appends every executed command to `logs/commands.log` |
| `Stop` | *(session end)* | `hook_test_summary.py` | Runs `pytest -q` and prints pass/fail summary |

Hook commands use `[ -f '<script>' ] && python '<script>'` so they skip gracefully on a fresh clone before `git pull`.

---

## Application architecture

The app is a **three-layer FastAPI monolith**:

```
app/main.py         ← Router layer: route definitions, HTTP error mapping, response serialisation
app/api/api.py      ← Service layer: business logic, JSON file reads, ORM queries
app/db/models.py    ← Data layer: SQLAlchemy ORM model (Vehicle) + Pydantic schemas
app/db/database.py  ← DB session factory (get_db dependency), engine creation
data/               ← JSON flat-file store (users, questions, alternatives, cars, results)
```

### Two coexisting data access patterns

- **Legacy endpoints** (`/user`, `/question`, `/alternatives`, `/answer`, `/result`) — read directly from `data/*.json` files in `app/api/api.py` using Python's `json` module. No ORM involved.
- **New endpoint** (`GET /vehicles/{vehicle_id}`) — uses SQLAlchemy ORM via a `Session` dependency injected by FastAPI's `Depends(get_db)`. The `Vehicle` SQLAlchemy model and `VehicleResponse` Pydantic schema live in `app/db/models.py`.

### Dependency injection flow for ORM endpoints

`app/db/database.py:get_db` yields a `SessionLocal` instance → injected into the route handler in `app/main.py` via `Depends(get_db)` → passed down to `app/api/api.py:get_vehicle_by_id`.

### `models.py` class inventory

`app/db/models.py` defines four classes:
- `Answer` (Pydantic) — a single question-answer pair used in `UserAnswer`.
- `UserAnswer` (Pydantic) — the `POST /answer` request body.
- `Vehicle` (SQLAlchemy ORM) — `__tablename__ = "vehicles"`, fields: `id`, `make`, `model`, `year`, `price`, `transmission`, `fuel_type`.
- `VehicleResponse` (Pydantic) — response schema for `GET /vehicles/{vehicle_id}`, built from the ORM model via `from_attributes=True`.

### Test isolation for ORM tests

`test/test_vehicle.py` overrides `get_db` with an in-memory SQLite engine and uses an `autouse` fixture to create/drop the schema and seed one `Vehicle` row per test. This is the pattern to follow for any new ORM-backed endpoint tests.

### Dead code: `read_vehicle` in `api.py`

`app/api/api.py` contains two vehicle lookup functions:
- `get_vehicle_by_id(vehicle_id, db)` — ORM-based, wired to `GET /vehicles/{vehicle_id}` in `main.py`. This is the live path.
- `read_vehicle(vehicle_id)` — JSON flat-file lookup from `data/cars.json`, not registered in any route. Dead code.

Do not add a second route for `read_vehicle` without first deciding which data source owns vehicle retrieval.

### Vehicle recommendation matching

`create_answer` in `api.py` matches vehicles by checking whether all three selected answer strings appear *anywhere* in `car.values()` — a loose value-set intersection, not a keyed field lookup. Changing alternative labels in `alternatives.json` must stay in sync with the exact string values in `data/cars.json` or recommendations will silently return zero results.

### Dead code: `read_vehicle` note removed

The `read_vehicle` JSON-based function was removed. The sole vehicle lookup path is `get_vehicle_by_id(vehicle_id, db)` — ORM-based, wired to `GET /vehicles/{vehicle_id}`.

---

## Agentic SDLC pipeline

### Pipeline steps and agents

Each agent delegates its full workflow to the corresponding skill — the agent file is a thin invoker, the skill is the source of truth.

| Step | Agent | Skill | Output artifact |
|------|-------|-------|-----------------|
| 1 | Requirements Agent | `write-requirements` | `artifacts/requirements.md` |
| 2 | Architect Agent | `design-architecture` | `artifacts/architecture.md` |
| 3 | Design Review Agent | `design-review` | `artifacts/design-review.md` |
| 4 | Planner Agent | `plan-implementation` | `artifacts/impl-plan.md` |
| 5 | Implementation Agent | `implement-task` | production code + tests |
| 6 | Review Agent | `code-review` | review findings + fixes |
| 7 | Verify Agent | `verify-implementation` | `artifacts/verification-report.md` |
| 8 | PR Agent | `create-pr` | pull request + `artifacts/CHANGELOG.md` |

All agents also use `sdlc-traceability` to maintain stable IDs across artifacts.

### Traceability ID conventions

| ID format | Scope |
|-----------|-------|
| `FR-###` | Functional requirement (in `requirements.md`) |
| `NFR-###` | Non-functional requirement (in `requirements.md`) |
| `DR-###` | Design-review finding (in `design-review.md`) |
| `TASK-###` | Implementation task (in `impl-plan.md`) |

IDs are assigned once and never renumbered. Downstream artifacts reference IDs instead of restating the content. Code comments use these IDs to trace back to requirements (e.g. `# FR-001`).

### Rules (path-scoped, auto-applied)

Rules in `.claude/rules/` load automatically when Claude works on matching files.
No explicit invocation needed — they're part of every relevant editing session.

| File | Paths matched | Governs |
|------|--------------|---------|
| `.claude/rules/code-quality.md` | `**/*.py`, `**/*.{js,ts,jsx,tsx}` | OWASP-safe, DRY, clear-code standards |
| `.claude/rules/tests.md` | `test/**`, `tests/**`, `**/__tests__/**`, `**/*.test.py`, `**/*.spec.py` | coverage, structure, determinism |
| `.claude/rules/sdlc-artifacts.md` | `artifacts/**/*.md` | document structure, traceability, writing quality |

### `.claude/` layout

```
.claude/
├── CLAUDE.md                          ← this file
├── agents/                            ← one agent per pipeline step
├── skills/                            ← one skill per agent (workflow detail)
│   ├── read-user-story/
│   ├── sdlc-traceability/
│   ├── write-requirements/
│   ├── design-architecture/
│   ├── design-review/
│   ├── plan-implementation/
│   ├── implement-task/
│   ├── code-review/
│   ├── verify-implementation/
│   └── create-pr/
├── rules/                             ← path-scoped rules (auto-applied by Claude Code)
│   ├── code-quality.md
│   ├── tests.md
│   └── sdlc-artifacts.md
└── commands/
    └── 00-orchestrator.prompt.md      ← pipeline entry point
```
