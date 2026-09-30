---
name: verify-implementation
description: "Generate and run a comprehensive verification suite (unit + integration tests) and a content quality check of the final output document against artifacts/requirements.md. Used by the Verify Agent (Step 7) after Review has passed."
---

# Skill: Verify Implementation

This skill is loaded by the **Verify Agent** (Step 7 of the Agentic SDLC Pipeline)
to confirm the implementation satisfies all agreed requirements through automated
tests and a document quality check. Follow these steps exactly.

## Step 1 — Establish verification context

1. Read `artifacts/requirements.md` to collect all `FR-###` and `NFR-###` IDs,
   acceptance criteria, and traceability identifiers.
2. Load the [[sdlc-traceability]] skill to map every test to the requirement it
   verifies.
3. Identify the components, modules, and files that make up the current
   implementation, and the final output document to quality-check.
4. Detect the project's language, test framework, runner, and existing test layout.
   Reuse established conventions — do not introduce a new framework without cause.

## Step 2 — Plan the verification suite

Before generating any test, list:

- **Unit tests** — individual functions and modules (logic, boundaries, error
  branches, tested in isolation)
- **Integration tests** — interactions between components, external services,
  files, and end-to-end flows (using fixtures or a controlled environment, not
  production resources)
- **Edge cases** — `Not Found`, missing fields, empty inputs, invalid states,
  timeouts, and concurrent access
- **Document quality checks** — structure, completeness, accuracy, and formatting
  of the final output document

Every `FR-###` and `NFR-###` must map to at least one planned test case.

## Step 3 — Generate the tests

For each test:

- Give it a **descriptive name** that encodes what it verifies
  (e.g. `test_get_vehicle_by_id_success_FR001`)
- Keep tests **independent and deterministic** — no hidden ordering or timing
  dependencies
- Reference the requirement ID in the test name or a one-line comment
- Mock or stub external dependencies in unit tests; use real boundaries in
  integration tests

## Step 4 — Verification checklist

Work through every area below before reporting results:

| Area | Verification Question |
| --- | --- |
| **Requirement coverage** | Does every `FR-###` and `NFR-###` map to at least one passing test? |
| **Unit tests** | Is each function and module tested for logic, boundaries, and error branches in isolation? |
| **Integration tests** | Are the interactions between components, services, and files verified end to end? |
| **Edge cases** | Do tests cover `Not Found`, missing fields, empty inputs, and error branches? |
| **Determinism** | Do tests pass reliably and independently, without hidden ordering or timing? |
| **Coverage** | Is coverage sufficient for critical paths? Are gaps explicitly reported? |
| **Document quality** | Is the final output document complete, accurate, well-structured, and correctly formatted? |
| **Traceability** | Can each test and content check be traced to a requirement identifier? |

## Step 5 — Run the suite and triage

1. Run the full test suite and capture results and coverage:
   ```bash
   pytest test/test_vehicle.py -v
   pytest --tb=short
   ```
2. For each failure, determine whether the defect is in the code or in the test.
3. Fix the root cause and re-run until the suite is green.
4. **Never** weaken assertions, delete coverage, or mask a real defect to make a
   test pass — fix the underlying issue.
5. Report coverage against each acceptance criterion and flag any requirement
   without a passing test.

## Step 6 — Verify the output document

Run the content quality check against the final output document:

- **Complete** — all required sections are present
- **Accurate** — facts, file paths, and behavior descriptions match the code
- **Consistent** — no internal contradictions
- **Formatted** — follows the project's document conventions
- **Traceable** — references the `FR-###` / `NFR-###` IDs it fulfills

Apply fixes when the correction is clearly in scope. Escalate ambiguous content
decisions to the user.

## Step 7 — Gate and report

Report a concise summary:

```markdown
## Verification Report

- Total tests: X  |  Passed: X  |  Failed: X
- Requirements covered: FR-### ✅  FR-### ✅  FR-### ❌ (no test)
- Coverage: X% overall  |  Critical paths: X%
- Document quality: Pass | Fail — <issues>
- Open gaps: <deferred or skipped items>

**Verdict: Pass ✅ | Fail 🚫**
```

| Verdict | Condition |
| --- | --- |
| ✅ **Pass** | All tests green, every FR/NFR covered, document quality passes |
| 🚫 **Fail** | One or more tests failing, an FR/NFR uncovered, or document quality fails |

Hand off to the **PR Agent** (Step 8) only on ✅ Pass.
