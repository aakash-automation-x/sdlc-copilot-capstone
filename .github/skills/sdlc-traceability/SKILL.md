---
name: sdlc-traceability
description: "Maintain end-to-end traceability across the SDLC artifacts using stable requirement IDs. Use whenever writing or updating requirements, architecture, plan, code, tests, review findings, or the PR."
---

# Skill: SDLC Traceability

Keep a single, unbroken thread from the user story to the merged PR so every
piece of work can be traced to a requirement and back.

## ID conventions

- **Functional requirement:** `FR-###` (e.g. `FR-001`)
- **Non-functional requirement:** `NFR-###` (e.g. `NFR-001`)
- **Implementation task:** `TASK-###`
- **Design-review finding:** `DR-###`

Assign IDs once and never reuse or renumber them. When something is removed,
mark it deprecated rather than reassigning its ID.

## The traceability chain

```
User story ──▶ FR-### / NFR-### (requirements.md)
            ──▶ architecture component (architecture.md, cites FR/NFR)
            ──▶ DR-### finding + decision (design-review.md)
            ──▶ TASK-### (impl-plan.md, cites FR/NFR + arch section)
            ──▶ code change (commit message cites TASK-###)
            ──▶ test (name/comment cites FR/NFR)
            ──▶ review finding (cites file + FR/NFR)
            ──▶ PR (Changes Made + Reviewer Checklist cite FR/NFR)
```

## How to apply it

- When creating an artifact, reference the upstream IDs it satisfies instead of
  restating their content.
- Commit messages reference the `TASK-###` (and, where useful, the `FR`/`NFR`).
- Test names or one-line comments reference the requirement they verify.
- Before finishing a step, confirm every upstream ID is covered downstream and
  flag any orphan (a requirement with no task/test, or a task with no
  requirement).

## Traceability matrix (optional, recommended for the PR)

| FR/NFR | Architecture | TASK | Code | Test | Status |
| --- | --- | --- | --- | --- | --- |
| FR-001 | Auth component | TASK-003 | `auth/login.ts` | `login.spec.ts` | ✅ |

Report any row that cannot be completed as `Not Found` so gaps are visible.
