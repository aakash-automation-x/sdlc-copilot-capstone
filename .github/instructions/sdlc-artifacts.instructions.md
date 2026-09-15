---
description: "Authoring standards for the Agentic SDLC deliverable documents (requirements, architecture, design review, implementation plan, changelog)."
applyTo: "requirements.md,architecture.md,design-review.md,impl-plan.md,CHANGELOG.md"
---

# SDLC Artifact Standards

These standards apply to every Markdown deliverable produced by the pipeline.

## Structure and traceability

- Give each requirement a stable, unique ID: functional as `FR-###`,
  non-functional as `NFR-###`. Never renumber an existing ID.
- Every downstream artifact must reference the IDs it satisfies:
  - `architecture.md` components cite the `FR`/`NFR` they realize.
  - `impl-plan.md` tasks cite the requirement(s) and architecture section they
    implement.
  - `design-review.md` findings cite the architecture section under review.
- Keep a single source of truth. Do not restate requirements verbatim in later
  documents — reference their IDs instead.

## Writing quality

- Use precise, testable, unambiguous language. Prefer measurable targets
  (thresholds, timeouts, availability) for non-functional requirements.
- Separate **confirmed decisions** from **assumptions** and **open questions**
  with clear headings.
- Write requirements as outcomes, not implementation guesses, unless the user
  mandates a technical constraint.

## Formatting

- Use `##`/`###` headings, tables for structured data, and Mermaid fenced blocks
  for diagrams and data flows.
- Keep documents self-contained and readable by the next agent without
  reinterpretation.
- Mark anything that could not be found or confirmed as `Not Found` rather than
  inventing content.
