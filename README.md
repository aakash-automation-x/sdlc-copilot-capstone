# Agentic SDLC Pipeline

An **Agentic Software Development Lifecycle (SDLC) pipeline** driven entirely by
GitHub Copilot. Every phase of software delivery — from a raw user story to a
merged pull request — is orchestrated through Copilot **Agents, Prompts,
Instructions, Skills, and Hooks**.

## Overview

This repository is a capstone project that demonstrates how Copilot's
customization primitives can be composed into an end-to-end, traceable delivery
pipeline. Each SDLC step is owned by a dedicated autonomous agent that reads the
previous step's committed artifact and produces the next one.

## How the Copilot capabilities fit together

| Capability | Location | Role in the pipeline |
| --- | --- | --- |
| **Agents** | `.github/agents/*.agent.md` | One autonomous agent per SDLC step. Each agent owns a phase and hands off to the next. |
| **Prompts** | `.github/prompts/*.prompt.md` | Reusable slash-commands that kick off or repeat a step (e.g. `/01-requirements`). |
| **Instructions** | `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` | Always-on and path-scoped standards that shape every generation. |
| **Skills** | `.github/skills/*/SKILL.md` | On-demand domain knowledge (reading a user story, keeping traceability). |
| **Hooks** | `.github/copilot/hooks.json` + `.github/copilot/hooks/*` | Lifecycle automation that enforces gates (secret scanning, artifact ordering). |

## Pipeline stages

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

## Getting started

1. Open this repository in VS Code with GitHub Copilot enabled.
2. Provide a user story (see `userstory.docx`) as the pipeline input.
3. Run the pipeline one step at a time using the slash-command prompts, starting
   with `/01-requirements`.
4. Review and approve each artifact before moving to the next step — the pipeline
   is human-in-the-loop by design.

## Core principles

- **Traceability first.** Every requirement gets an ID (`FR-001`, `NFR-001`).
  Architecture, plan, code, tests, review findings, and the PR trace back to
  those IDs via the `sdlc-traceability` skill.
- **Human-in-the-loop.** Code is never committed, pushed, or opened as a PR
  without explicit human approval. No self-merges or pushes to protected branches.
- **Gate before you proceed.** Each step reads the previous step's committed
  artifact. A step never starts while its upstream artifact is missing.
- **Secure by default.** The pipeline follows the OWASP Top 10 and never prints,
  logs, or commits secrets, tokens, or credentials.
- **No speculative scope.** Only what an approved artifact requires is implemented.

## Repository structure

```
.github/
  agents/         # One .agent.md per SDLC step
  prompts/        # Slash-command prompts (/01-requirements … /08-pr)
  instructions/   # Path-scoped coding, test, and artifact standards
  skills/         # On-demand domain knowledge (read-user-story, sdlc-traceability)
  copilot/        # Lifecycle hooks and hooks.json
  copilot-instructions.md
userstory.docx    # Pipeline input
```

## SDLC deliverables

The following artifacts are produced in the repository root as the pipeline runs:
`requirements.md`, `architecture.md`, `design-review.md`, `impl-plan.md`, and
`CHANGELOG.md`.
