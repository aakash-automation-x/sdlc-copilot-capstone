---
name: implement-task
description: "Implement approved tasks from artifacts/impl-plan.md into production-ready code with human-in-the-loop approval at each step, traceable commits, and passing tests. Use in Step 5 of the SDLC pipeline (Implementation Agent) after the implementation plan is approved."
user-invocable: true
---

# Skill: Implement Task

This skill is loaded by the **Implementation Agent** (Step 5 of the Agentic SDLC
Pipeline) to turn approved implementation plan tasks into working, production-ready
code with explicit human review at each step. Follow these steps exactly.

## Step 1 — Read the approved implementation plan

1. Read `artifacts/impl-plan.md` before writing any code.
2. Cross-check each task against `artifacts/architecture.md` and
   `artifacts/requirements.md` so work stays traceable.
3. Use the `sdlc-traceability` skill (`.github/skills/sdlc-traceability/SKILL.md`)
   to link every commit to `TASK-###` / `FR-###`.
4. Identify task IDs, priorities, dependencies, blockers, expected outputs, and
   validation approaches.
5. Do not implement anything not backed by an approved task in `artifacts/impl-plan.md`.

## Step 2 — Select the next task

- Work in the dependency-ordered, prioritized sequence from `artifacts/impl-plan.md`.
- Start only tasks whose dependencies are complete and blockers are cleared.
- Never start a task marked as blocked — escalate the blocker to the user.
- Confirm the selected task and its scope with the user before making code changes
  when the task materially affects architecture, security, data, or public contracts.

## Step 3 — Propose the change

For each task, produce a reviewable change summary before touching any file:

```markdown
### TASK-###: <task title>

- **Task source:** artifacts/impl-plan.md (TASK-###)
- **FR/NFR:** FR-### | N/A
- **Files to change:** <paths>
- **Change summary:** <what the code does and why>
- **Tests to add or update:** <test files or cases>
- **Validation plan:** <build, lint, and test commands to run>
- **Risks or trade-offs:** None | <description>
- **Approval status:** Pending human review
```

Present this summary to the user and **wait for explicit approval** before applying
any change. Never treat an unreviewed suggestion as approved.

## Step 4 — Apply the approved change

After approval:

1. Apply changes following existing project structure, naming, and coding conventions.
2. Add or update automated tests as specified in the task's validation plan.
3. Keep changes small and scoped to the single approved task.
4. Run the validation commands and fix failures before considering the task complete:
   ```bash
   # Project-specific — update for your test runner and test files
   pytest test/test_vehicle.py -v
   ```
5. Do not add features, refactors, or abstractions beyond the task scope.
6. Never commit secrets, tokens, or credentials — review all output for sensitive data.

## Step 5 — Update progress

After each task completes:

- Mark the task as done in `artifacts/impl-plan.md` or an agreed progress log.
- Note its outcome so downstream Verify, Review, and PR agents have accurate state.
- Surface any newly discovered work, risks, or blockers to the user rather than
  silently expanding scope.

## Step 6 — Commit approved work

Commit only human-approved, validated changes:

```bash
git add <specific files>
git commit -m "feat: implement TASK-### <task title>

Co-Authored-By: GitHub Copilot <noreply@github.com>"
```

- Scope each commit to a single task or logical unit of work.
- The commit message must reference the `TASK-###` ID for traceability.
- Report the commit result, tests run, and any remaining tasks, risks, or open
  questions before moving to the next task or handing off to the **Review Agent**
  (Step 6).

## Quality gates (must pass before commit)

| Gate | Check |
| --- | --- |
| Scope | Only changes approved by the human in the loop are included |
| Tests | All existing and new tests pass |
| Security | No secrets, tokens, or credentials in code or output |
| Conventions | Existing project structure, naming, and style are followed |
| Traceability | Commit message references `TASK-###` |
