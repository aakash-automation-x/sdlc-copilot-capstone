# Agentic SDLC Pipeline — Repository Instructions

This repository implements an **Agentic SDLC Pipeline** driven entirely by GitHub
Copilot. Every phase of the software delivery lifecycle — from requirements to a
merged pull request — is orchestrated through Copilot **Agents, Prompts,
Instructions, Skills, and Hooks**.

## How the Copilot capabilities fit together

| Capability | Location | Role in the pipeline |
| --- | --- | --- |
| **Agents** | `.github/agents/*.agent.md` | One autonomous agent per SDLC step. Each agent owns a phase and hands off to the next. |
| **Prompts** | `.github/prompts/*.prompt.md` | Reusable, invocable slash-commands that kick off or repeat a step (e.g. `/01-requirements`). |
| **Instructions** | `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` | Always-on and path-scoped standards that shape every generation. |
| **Skills** | `.github/skills/*/SKILL.md` | On-demand domain knowledge (reading a user story, keeping traceability). |
| **Hooks** | `.github/copilot/hooks.json` + `.github/copilot/hooks/*` | Lifecycle automation that enforces gates (secret scanning, artifact ordering). |

## Pipeline stages, agents, and artifacts

| Step | Agent | Prompt | Output artifact |
| --- | --- | --- | --- |
| 1. Requirements | Requirements Agent | `/01-requirements` | `requirements.md` |
| 2. Architecture | Architect Agent | `/02-architecture` | `architecture.md` |
| 3. Design Review | Design Review Agent | `/03-design-review` | `design-review.md` |
| 4. Implementation Planning | Planner Agent | `/04-impl-plan` | `impl-plan.md` |
| 5. Implementation | Implementation Agent | `/05-implementation` | source code + tests |
| 6. Review | Review Agent | `/06-review` | review notes / fixes |
| 7. Verify | Verify Agent | `/07-verify` | passing test suite + content check |
| 8. PR | PR Agent | `/08-pr` | Pull Request + `CHANGELOG.md` |

## Core principles

- **Traceability first.** Every requirement gets an ID (`FR-001`, `NFR-001`).
  Architecture, plan, code, tests, review findings, and the PR must trace back to
  those IDs. Use the `sdlc-traceability` skill.
- **Human-in-the-loop.** Never commit code, push, or open a PR without explicit
  human approval. Never self-merge or push to a protected branch.
- **Gate before you proceed.** Each step reads the previous step's committed
  artifact. Do not start a step whose upstream artifact is missing.
- **Secure by default.** Follow the OWASP Top 10. Never print, log, or commit
  secrets, tokens, or credentials.
- **No speculative scope.** Implement only what an approved artifact requires.

## Working agreements

- Read the upstream artifact before producing the next one.
- Keep the SDLC deliverables (`requirements.md`, `architecture.md`,
  `design-review.md`, `impl-plan.md`, `CHANGELOG.md`) in the repository root.
- Prefer small, reviewable commits with messages that reference the task or
  requirement ID.
- Escalate ambiguous or high-impact decisions to the user instead of guessing.
