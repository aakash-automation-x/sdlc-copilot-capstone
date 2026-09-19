# Car Portal — Agentic SDLC Pipeline

**Project:** Car Portal Recommendation System  
**Purpose:** A Python FastAPI-based application that helps users discover and get recommendations for vehicles based on their preferences, answers, and search criteria.

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
| **Entry Point** | **SDLC Orchestrator** | **`ORCHESTRATION_LOG.md`** (state tracking) |
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
- Maintains `ORCHESTRATION_LOG.md` tracking all step statuses and approvals
- Supports resume from any step: `/00-orchestrator resume step=4`

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

## Working agreements

- Read the upstream artifact before producing the next one.
- Keep the SDLC deliverables (`artifacts/requirements.md`, `artifacts/architecture.md`,
  `artifacts/design-review.md`, `artifacts/impl-plan.md`, `artifacts/CHANGELOG.md`) in the `artifacts/` directory.
- Prefer small, reviewable commits with messages that reference the task or
  requirement ID.
- Escalate ambiguous or high-impact decisions to the user instead of guessing.
