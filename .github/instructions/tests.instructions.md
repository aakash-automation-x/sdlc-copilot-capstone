---
description: "Conventions for automated tests generated during implementation and verification."
applyTo: "**/*.{test,spec}.*,**/tests/**,**/__tests__/**,**/test/**"
---

# Test Standards

Applies to every automated test in the repository.

## Coverage

- Derive test cases directly from acceptance criteria and requirement IDs.
  Reference the ID in the test name or a one-line comment (e.g. `// FR-002`).
- Cover the **happy path AND** the edge cases: `Not Found`, missing fields,
  empty inputs, invalid states, timeouts, and error branches.
- Every functional and non-functional requirement must map to at least one
  passing test.

## Structure

- Provide **unit tests** for individual functions/modules (logic, boundaries,
  error branches) with external dependencies mocked or stubbed.
- Provide **integration tests** for interactions between components, services,
  and files, exercising real boundaries via fixtures — never production
  resources.
- Follow the project's existing framework, runner, naming, and directory layout.
  Do not introduce a new framework without cause.

## Quality

- Keep tests independent, deterministic, and clearly named. No hidden ordering
  or timing dependencies.
- Never make a test pass by weakening assertions, deleting coverage, or masking
  a real defect. Fix the root cause.
- Report coverage honestly, including any untested critical paths.
