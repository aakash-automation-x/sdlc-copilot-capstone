# Car Portal — Agentic SDLC Pipeline

**Project:** Car Portal Recommendation System  
**Purpose:** A Python FastAPI-based application that helps users discover and get recommendations for vehicles based on their preferences, answers, and search criteria.

## Repository implementation reality

- The current implementation is a small FastAPI service backed by JSON files under `data/`; it does not currently use PostgreSQL, SQLAlchemy, Docker, or a separate service process.
- HTTP routes are defined in `app/main.py`, application logic and JSON I/O are in `app/api/api.py`, and Pydantic models are in `app/db/models.py`.
- Relative data paths assume commands are run from the repository root. Preserve this constraint or make path handling explicit before changing it.
- The primary endpoint tests are in `test/test.py`. Run `pytest test/test.py` after Python changes.
- Install dependencies with `pip install -r requirements.txt` and start locally with `uvicorn app.main:app --reload`.
- Treat `README.md` as the source for setup and endpoint details and `userstory.md` as the current local story input; link to them instead of duplicating their content. If Jira or Confluence access is unavailable, use the local story and report the limitation rather than inventing requirements.

## Agent working loop

- Before changing production code, read the applicable scoped instruction file under `.github/instructions/` and the relevant upstream SDLC artifact under `artifacts/`.
- For Python changes, preserve the route/service/data responsibility split and avoid adding database or infrastructure assumptions that are not approved in the artifacts.
- For behavior changes, add or update focused tests in `test/` and run the narrowest relevant pytest command before broader validation.
- Treat explicit user scope constraints such as one functional requirement, one acceptance criterion, or minimal artifacts as binding across requirements, architecture, design review, and implementation planning. Do not add requirements or non-functional scope to fill out a template.
- If a user story, requirement, or approved artifact changes after a pipeline stage has completed, pause downstream work, identify stale artifacts, and request approval before continuing.
- For external story sources, distinguish successful retrieval from tool or connector availability. Record the retrieval result, use `userstory.md` when access fails, and never infer story content from a configured skill or tool name.
- Do not silently repair unrelated defects or rewrite existing user changes. Surface missing artifacts, ambiguous requirements, and architecture mismatches for human approval.

This repository implements an **Agentic SDLC Pipeline** driven entirely by GitHub
Copilot. Every phase of the software delivery lifecycle — from requirements to a
merged pull request — is orchestrated through Copilot **Agents, Prompts,
Instructions, and Skills**.

## How the Copilot capabilities fit together

| Capability | Location | Role in the pipeline |
| --- | --- | --- |
| **Agents** | `.github/agents/*.agent.md` | One autonomous agent per SDLC step. Each agent owns a phase and hands off to the next. |
| **Prompts** | `.github/prompts/*.prompt.md` | Single orchestrator entry point (`/00-orchestrator`) that manages the entire pipeline. |
| **Instructions** | `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` | Always-on and path-scoped standards that shape every generation. |
| **Skills** | `.github/skills/*/SKILL.md` | On-demand domain knowledge (reading a user story, keeping traceability). |

## Pipeline stages and artifacts

The orchestrator manages all 8 steps sequentially:

| Step | Agent | Output artifact |
| --- | --- | --- |
| **Entry Point** | **SDLC Orchestrator** | **`artifacts/ORCHESTRATION_LOG.md`** (state tracking) |
| 1 | Requirements Agent | `artifacts/requirements.md` |
| 2 | Architect Agent | `artifacts/architecture.md` |
| 3 | Design Review Agent | `artifacts/design-review.md` |
| 4 | Planner Agent | `artifacts/impl-plan.md` |
| 5 | Implementation Agent | source code + tests |
| 6 | Review Agent | review notes / fixes |
| 7 | Verify Agent | test suite + content check |
| 8 | PR Agent | Pull Request + `artifacts/CHANGELOG.md` |

## Running the full pipeline

Use the **SDLC Orchestrator** to automate the entire pipeline end-to-end:

```
/00-orchestrator
```

The orchestrator:
- Invokes each agent in sequence (Steps 1–8)
- Captures outputs after each step
- Presents review gates with approval options:
  - ✅ Approve & Proceed to next step
  - 🔄 Request Changes (agent re-runs with feedback)
  - ⏸️ Pause Pipeline (save state, resume later)
- Maintains `artifacts/ORCHESTRATION_LOG.md` tracking all step statuses and approvals
- Supports resume from any step: `/00-orchestrator resume step=3`

**Human approval is required at every gate.** The orchestrator never auto-proceeds.

## Core principles

- **Traceability first.** Every requirement gets an ID (`FR-001`, `NFR-001`).
  Architecture, plan, code, tests, review findings, and the PR must trace back to
  those IDs. Use the `sdlc-traceability` skill.
- **Human-in-the-loop.** Never commit code, push, or open a PR without explicit
  human approval. Never self-merge or push to a protected branch.
  **The orchestrator enforces approval gates at every step.**
- **Gate before you proceed.** Each step reads the previous step's committed
  artifact. Do not start a step whose upstream artifact is missing.
- **Secure by default.** Follow the OWASP Top 10. Never print, log, or commit
  secrets, tokens, or credentials.
- **No speculative scope.** Implement only what an approved artifact requires.
- **Repository facts over plans.** When an artifact, memory note, or user story conflicts with the current code, call out the discrepancy and ask for a decision before introducing a new persistence or deployment stack.

## Working agreements

- Read the upstream artifact before producing the next one.
- Keep the SDLC deliverables (`artifacts/requirements.md`, `artifacts/architecture.md`,
  `artifacts/design-review.md`, `artifacts/impl-plan.md`, `artifacts/CHANGELOG.md`) in the `artifacts/` directory.
- Prefer small, reviewable commits with messages that reference the task or
  requirement ID.
- Escalate ambiguous or high-impact decisions to the user instead of guessing.

## Related documentation

- [Project setup and API reference](../README.md)
- [Current user story](../userstory.md)
- [Python code-quality standards](instructions/code-quality.instructions.md)
- [Test conventions](instructions/tests.instructions.md)
- [SDLC artifact standards](instructions/sdlc-artifacts.instructions.md)
