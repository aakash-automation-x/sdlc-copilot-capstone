---
description: "Kick off Step 1: turn the user story into testable requirements.md."
agent: agent
---

# /01-requirements

Run the **Requirements Agent** for Step 1 of the Agentic SDLC pipeline.

1. Use the `read-user-story` skill to read the user story from `userstory.docx`
   (or a Jira/Confluence source if provided).
2. Analyze it for missing, vague, conflicting, or untestable details and ask me
   focused clarifying questions one topic at a time. Wait for my answers.
3. When I confirm, write `requirements.md` in the repo root with:
   - user story and business objective, scope / out-of-scope, actors
   - functional requirements (`FR-###`) and non-functional requirements
     (`NFR-###`) with measurable targets
   - data, integration, security, privacy, and operational requirements
   - testable acceptance criteria, assumptions, dependencies, open questions
4. Summarize, then commit with `docs: capture requirements for <story>` after my
   confirmation.

Follow `.github/instructions/sdlc-artifacts.instructions.md` and use the
`sdlc-traceability` skill. Hand off to `/02-architecture`.
