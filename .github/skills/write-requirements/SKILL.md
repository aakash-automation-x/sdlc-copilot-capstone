---
name: write-requirements
description: "Extract functional requirements from a user story and document them in artifacts/requirements.md with unique FR-### IDs, acceptance criteria, traceability, and out-of-scope items. Use in Step 1 of the SDLC pipeline (Requirements Agent) to turn an ingested user story into clear, testable requirements."
user-invocable: true
---

# Skill: Write Requirements

This skill is loaded by the **Requirements Agent** (Step 1 of the Agentic SDLC Pipeline)
to turn an ingested user story into a clear, testable functional requirement captured
in `artifacts/requirements.md`. Follow these steps exactly.

## Step 1 — Read and extract the user story

1. Use the `read-user-story` skill (`.github/skills/read-user-story/SKILL.md`) to
   ingest the story from Jira issue `CAP-13` using the `jira_get_issue` MCP tool.
2. Extract the **minimum complete set of functional requirements** — the core behaviors
   the story is asking for. Prefer one; include more only when the story explicitly
   requires distinct behaviors.
3. Extract the **acceptance criteria** explicitly stated in the story. Do not infer
   criteria that are not written down.
4. Identify any explicitly stated constraints (security, compliance, HTTPS, masking,
   etc.) — capture them as out-of-scope notes if not part of the core FR.

## Step 2 — Distill the single functional requirement

- Express the minimum complete set of functional requirements in clear, testable language.
  Prefer a single requirement; add more only when the story explicitly requires multiple
  distinct behaviors.
- Assign sequential identifiers starting from `FR-001` using the `sdlc-traceability`
  skill (`.github/skills/sdlc-traceability/SKILL.md`) ID convention.
- The requirement must be independently verifiable — a tester must be able to
  confirm it passes or fails without interpretation.
- Do not infer additional requirements from the story. If the story implies
  multiple behaviors, document only the one explicitly asked for and list the
  rest as out-of-scope.

**Good:** `FR-001: The system shall return a vehicle record by its unique ID via GET /vehicles/{vehicle_id}.`
**Bad:** `FR-001: The system shall manage vehicles.` (not testable)

## Step 3 — Write artifacts/requirements.md

Create or update `artifacts/requirements.md` using this exact structure:

```markdown
# Requirements

## User Story Reference
<paste or summarise the "As a … I want … so that …" statement>

## Business Objective
<one sentence on why this requirement matters>

## Functional Requirement

### FR-001: <requirement title>
**Statement:** <clear, testable requirement statement>
**Source:** Jira CAP-13
**Priority:** High | Medium | Low

## Acceptance Criterion

### AC-001 (FR-001)
**Given** <precondition>
**When** <action>
**Then** <expected outcome>

## Traceability
| ID | Source | Status |
| --- | --- | --- |
| FR-001 | Jira CAP-13 | Approved |

## Out of Scope
- <anything the story does not ask for>
- <non-functional, integration, security, operational requirements unless explicit>
```

### Rules

| Field | Rule |
| --- | --- |
| FR statement | Must be independently testable; one behavior per requirement |
| Acceptance criteria | One primary criterion per FR; add more only when the story states multiple conditions |
| Out of scope | List every inferred or implied behavior that is NOT in the story |
| Language | Precise and unambiguous — avoid "should", prefer "shall" |

## Step 4 — Review and commit

1. Verify the document captures the single FR accurately and traceably.
2. Confirm the acceptance criterion is directly testable without interpretation.
3. Commit with:
   ```bash
   git add artifacts/requirements.md
   git commit -m "docs: capture requirements for <user-story-name>

   Co-Authored-By: GitHub Copilot <noreply@github.com>"
   ```
4. Report the commit result and any open questions before handing off to the
   **Architect Agent** (Step 2).
