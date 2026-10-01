---
name: plan-implementation
description: "Break approved artifacts/architecture.md into a prioritized, dependency-ordered TASK-### list captured in artifacts/impl-plan.md, including blocked tasks and parallelization opportunities. Use in Step 4 of the SDLC pipeline (Planner Agent) after the design review is approved and before any coding begins."
user-invocable: true
---

# Skill: Plan Implementation

This skill is loaded by the **Planner Agent** (Step 4 of the Agentic SDLC Pipeline)
to turn the approved architecture into a concrete, dependency-ordered task list.
Follow these steps exactly.

## Step 1 — Read the approved architecture

1. Read `artifacts/architecture.md` before creating any tasks.
2. Cross-check against `artifacts/requirements.md` so planned work stays traceable
   to approved requirements.
3. Use the `sdlc-traceability` skill (`.github/skills/sdlc-traceability/SKILL.md`)
   to assign `TASK-###` IDs and link each task to its `FR-###` / `NFR-###` and
   architecture section.
4. Do not plan work for features or behaviors not supported by the approved
   architecture or requirements.

## Step 2 — Derive the task breakdown

From the architecture, identify:

- **Major epics or workstreams** — the high-level delivery threads
- **Concrete engineering tasks** — one independently deliverable unit of work each
- **Dependencies** — which tasks must complete before another can start
- **Blocked tasks** — tasks that cannot start until a specific task finishes or a
  decision is resolved
- **Parallelization opportunities** — tasks with no shared prerequisite that can
  run concurrently
- **Validation activities** — the verification step for each major deliverable

Sequence foundational work (data model, auth, environment setup, API contracts)
before dependent application, integration, and release tasks. Prefer small,
independently verifiable tasks over broad ambiguous items.

## Step 3 — Prioritize

Assign a priority to each task:

| Priority | Definition |
| --- | --- |
| **High** | Required for core functionality, risk reduction, or unblocks other tasks |
| **Medium** | Important but not blocking; can follow High tasks |
| **Low** | Nice-to-have; defer if time-constrained |

Security, authentication, data-model, API-contract, and environment-setup tasks are
always **High** priority and come before dependent UI, workflow, and integration tasks.

## Step 4 — Task format

Use this format for every task in `artifacts/impl-plan.md`:

```markdown
### TASK-###: <task title>

- **Priority:** High | Medium | Low
- **FR/NFR:** FR-### | NFR-### | N/A
- **Architecture section:** <section from artifacts/architecture.md>
- **Depends on:** None | TASK-###
- **Blocked by:** None | TASK-### | <open decision description>
- **Target agent:** Implementation Agent | Verify Agent | Review Agent | PR Agent
- **Description:** <clear, specific implementation work to complete>
- **Expected output:** <code, config, test, or documentation artifact>
- **Validation:** <how completion will be verified>
```

## Step 5 — Write artifacts/impl-plan.md

Create or update `artifacts/impl-plan.md` using this exact structure:

```markdown
# Implementation Plan

## Overview
<summary of scope, key epics, and delivery sequence>

## Source References
- Architecture: `artifacts/architecture.md`
- Requirements: `artifacts/requirements.md`

## Assumptions and Constraints
- <assumption or constraint>

## Task List

<TASK-### blocks in dependency order>

## Parallelization Opportunities
- TASK-### and TASK-### can run concurrently once TASK-### completes

## Blocked Tasks
| Task | Blocked by | Unblock criteria |
| --- | --- | --- |

## Risks and Open Questions
- <risk or unresolved question>

## Recommended First Task for Implementation Agent
TASK-### — <title>
```

## Step 6 — Review and commit

1. Verify every task traces back to `artifacts/architecture.md` and, where
   relevant, to `artifacts/requirements.md`.
2. Confirm the task order is dependency-safe and blocked tasks are labeled.
3. Present a concise summary: highest-priority tasks, critical dependencies, blockers.
4. Escalate unresolved planning decisions that materially affect scope or sequence
   to the user before committing.
5. Commit with:
   ```bash
   git add artifacts/impl-plan.md
   git commit -m "docs: add implementation plan for <feature-name>

   Co-Authored-By: GitHub Copilot <noreply@github.com>"
   ```
6. Report the commit result, remaining blockers, and open questions before handing
   off to the **Implementation Agent** (Step 5).
