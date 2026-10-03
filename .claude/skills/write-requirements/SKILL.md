---
name: write-requirements
description: "Extract the single functional requirement from a user story and document it in artifacts/requirements.md with a unique FR-001 ID, one acceptance criterion, traceability, and out-of-scope items. Used by the Requirements Agent (Step 1)."
---

# Skill: Write Requirements

This skill is loaded by the **Requirements Agent** (Step 1 of the Agentic SDLC Pipeline)
to turn an ingested user story into a clear, testable functional requirement captured
in `artifacts/requirements.md`. Follow these steps exactly.

## Step 1 — Read and extract the user story

1. Load the [[read-user-story]] skill to ingest the story from `userstory.md` (or
   a Jira/Confluence source).
2. Extract the **primary functional requirement** — the single, core behavior the
   story is asking for.
3. Extract the **acceptance criteria** explicitly stated in the story. Do not infer
   criteria that are not written down.
4. Identify any explicitly stated constraints (security, compliance, HTTPS, masking,
   etc.) — capture them as out-of-scope notes if not part of the core FR.

## Step 2 — Distill the single functional requirement

- Express exactly **one** functional requirement in clear, testable language.
- Assign it the identifier `FR-001` using the [[sdlc-traceability]] ID convention.
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
**Source:** userstory.md
**Priority:** High | Medium | Low

## Acceptance Criterion

### AC-001 (FR-001)
**Given** <precondition>
**When** <action>
**Then** <expected outcome>

## Traceability
| ID | Source | Status |
| --- | --- | --- |
| FR-001 | userstory.md | Approved |

## Out of Scope
- <anything the story does not ask for>
- <non-functional, integration, security, operational requirements unless explicit>
```

### Rules

| Field | Rule |
| --- | --- |
| FR statement | Must be independently testable; one behavior only |
| Acceptance criteria | Limit to exactly **one** primary criterion that validates FR-001 |
| Out of scope | List every inferred or implied behavior that is NOT in the story |
| Language | Precise and unambiguous — avoid "should", prefer "shall" |

## Step 4 — Review and commit

1. Verify the document captures the single FR accurately and traceably.
2. Confirm the acceptance criterion is directly testable without interpretation.
3. Commit with:
   ```bash
   git add artifacts/requirements.md
   git commit -m "docs: capture requirements for <user-story-name>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
   ```
4. Report the commit result and any open questions before handing off to the
   **Architect Agent** (Step 2).
