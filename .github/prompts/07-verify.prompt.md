---
description: "Kick off Step 7: generate and run the verification suite + content check."
agent: agent
---

# /07-verify

Run the **Verify Agent** for Step 7 of the Agentic SDLC pipeline.

1. Read `requirements.md` for acceptance criteria and requirement IDs.
2. Plan and generate **unit tests** (logic, boundaries, error branches) and
   **integration tests** (component/service/file interactions) that follow the
   project's framework and conventions. Every requirement maps to at least one
   test; cover the happy path AND edge cases (`Not Found`, missing fields,
   empty inputs, timeouts).
3. Run the full suite, capture results and coverage, and fix root causes of
   failures — never weaken a test to make it pass.
4. Run a **content-quality check** on the final output document(s): complete,
   accurate, well-structured, correctly formatted, and traceable.
5. Report totals, pass/fail, coverage, requirements verified, and the content
   outcome. Do not signal Pass while any test fails or the document check fails.

Follow `.github/instructions/tests.instructions.md` and use the
`sdlc-traceability` skill. Hand off to `/08-pr`.
