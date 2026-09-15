---
description: "Kick off Step 2: design the high-level architecture from requirements.md."
agent: agent
---

# /02-architecture

Run the **Architect Agent** for Step 2 of the Agentic SDLC pipeline.

1. Read the approved `requirements.md`. Do not proceed if it is missing.
2. Propose a high-level architecture: components and responsibilities,
   technology choices with rationale, data flow, and integration points.
3. Ask me focused questions about any architecture-impacting decision that
   cannot be safely assumed (hosting, persistence, auth, deployment, scale).
4. Write `architecture.md` in the repo root with a component diagram and data
   flow in Mermaid, and a section on which Copilot agents, prompts,
   instructions, skills, and hooks drive the pipeline.
5. Ensure every component traces to an `FR`/`NFR`. Summarize and commit after my
   confirmation.

Follow `.github/instructions/sdlc-artifacts.instructions.md` and use the
`sdlc-traceability` skill. Hand off to `/03-design-review`.
