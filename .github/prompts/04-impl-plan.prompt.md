---
description: "Kick off Step 4: break architecture.md into a dependency-ordered task plan."
agent: agent
---

# /04-impl-plan

Run the **Planner Agent** for Step 4 of the Agentic SDLC pipeline.

1. Read the approved `architecture.md` (and `design-review.md` decisions).
2. Generate a task breakdown: epics, concrete engineering tasks, dependencies,
   priorities, and validation activities.
3. Order tasks by dependency so foundational work (security, data model, API
   contracts, environment) comes before dependent work. Mark parallelizable
   tasks and explicitly list **blocked** tasks with their unblock criteria.
4. Write `impl-plan.md` using the `TASK-###` format with priority, depends-on,
   blocked-by, target agent, description, expected output, and validation. Every
   task must trace to an `FR`/`NFR` and an architecture section.
5. Summarize highest-priority and blocked tasks, then commit after my
   confirmation.

Follow `.github/instructions/sdlc-artifacts.instructions.md` and use the
`sdlc-traceability` skill. Hand off to `/05-implementation`.
