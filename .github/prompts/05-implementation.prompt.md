---
description: "Kick off Step 5: implement approved tasks with human-in-the-loop approval."
agent: agent
---

# /05-implementation

Run the **Implementation Agent** for Step 5 of the Agentic SDLC pipeline.

1. Read `impl-plan.md`; cross-check tasks against `architecture.md` and
   `requirements.md`. Only work tasks whose dependencies are complete and that
   are not blocked.
2. For the selected `TASK-###`, propose the code and supporting tests. Present a
   reviewable diff/summary and **wait for my explicit approval** before applying
   or committing anything.
3. Apply approved changes following existing conventions, then run build, lint,
   and tests and fix failures before marking the task done.
4. Keep commits small and task-referencing (`feat: implement TASK-001 <title>`).
   Update task status so downstream agents see accurate state.

Copilot features to use in this step:
- **Instructions:** `.github/instructions/code-quality.instructions.md` and
  `tests.instructions.md` enforce OWASP-safe, DRY, well-tested code.
- **Skills:** `sdlc-traceability` keeps every change tied to a requirement ID.
- **Hooks:** the `check-secrets` pre-commit hook blocks credentials from being
  committed; the `validate-artifacts` hook confirms `impl-plan.md` exists first.
- **Human-in-the-loop:** never commit an unreviewed suggestion.

Hand off to `/06-review`.
