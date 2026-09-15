---
description: "Kick off Step 3: senior design review of architecture.md."
agent: agent
---

# /03-design-review

Run the **Design Review Agent** for Step 3 of the Agentic SDLC pipeline.

1. Read `architecture.md` and cross-check it against `requirements.md`.
2. Review it as a senior architect: alignment with requirements, missing or
   unclear components, data-flow gaps, security/privacy/access-control risks,
   reliability, scalability, observability, deployment, and testability.
3. Classify each finding `Critical` / `High` / `Medium` / `Low`. Escalate
   high-impact decisions to me instead of assuming defaults.
4. Write `design-review.md` with a findings table (ID, severity, area, finding,
   impact, recommendation, decision, status) and agreed design decisions.
5. Update `architecture.md` for every accepted finding and keep the two
   documents consistent. Commit after my confirmation.

Follow `.github/instructions/sdlc-artifacts.instructions.md` and use the
`sdlc-traceability` skill. Hand off to `/04-impl-plan`.
