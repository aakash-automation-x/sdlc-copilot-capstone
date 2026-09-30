---
name: design-review
description: "Conduct a structured senior design review of artifacts/architecture.md, classify findings by severity (Critical/High/Medium/Low), agree design decisions, and document everything in artifacts/design-review.md. Use in Step 3 of the SDLC pipeline (Design Review Agent) before any production code is written."
user-invocable: true
---

# Skill: Design Review

This skill is loaded by the **Design Review Agent** (Step 3 of the Agentic SDLC
Pipeline) to review the proposed architecture before any production code is written.
Follow these steps exactly.

## Step 1 — Read the architecture

1. Read `artifacts/architecture.md` before starting the review.
2. Cross-check against `artifacts/requirements.md` when available.
3. Use the `sdlc-traceability` skill (`.github/skills/sdlc-traceability/SKILL.md`)
   to tie every finding to an architecture section and, where relevant, a `FR-###`
   or `NFR-###`.
4. Do not assume the architecture is correct because it was produced by a prior agent.

## Step 2 — Review areas

Evaluate every area in the table below. For each finding, record:

- **Finding ID** — `DR-###` (assign sequentially)
- **Area** — from the table below
- **Severity** — see definitions in Step 3
- **Finding** — what is wrong or missing
- **Impact** — what goes wrong downstream if not resolved
- **Recommendation** — specific change or decision needed

| Review Area | Review Question |
| --- | --- |
| **Requirements alignment** | Does the architecture satisfy every `FR-###` and `NFR-###`? Are any requirements missing a component? |
| **Components and responsibilities** | Are component boundaries clear and non-overlapping? Does any component have too many responsibilities? |
| **Data flow** | Is the data flow complete, correct, and consistent with the written architecture? |
| **Security and access control** | Are auth, authorisation, input validation, secret management, and OWASP mitigations covered? |
| **Reliability and fault tolerance** | Are failures, timeouts, retries, and recovery paths addressed? |
| **Scalability and performance** | Are bottlenecks identified? Does the architecture handle projected load? |
| **Observability and operations** | Is there a clear logging, monitoring, and debugging strategy? |
| **Deployment and CI/CD** | Is the build, package, and deploy path realistic and complete? |
| **SDLC pipeline coverage** | Are the agents, prompts, instructions, skills, and hooks sufficient to drive the full pipeline? |
| **Technology choices** | Are choices justified? Are there known risks, vulnerabilities, or better alternatives? |
| **Testability and maintainability** | Can the architecture be tested in isolation? Is it easy to evolve? |

## Step 3 — Severity definitions

| Severity | Definition |
| --- | --- |
| **Critical** | Blocks implementation or creates unacceptable security, data, reliability, or delivery risk. Must be resolved before any coding begins. |
| **High** | Must be resolved before production coding begins. Materially affects correctness, security, or delivery. |
| **Medium** | Should be resolved or explicitly accepted before implementation planning. Represents a meaningful gap or risk. |
| **Low** | Useful improvement or clarification that does not block the next SDLC step. |

## Step 4 — Agree design decisions

For each accepted finding:

1. Define a concrete design decision or mitigation.
2. Escalate to the user when the decision materially affects scope, cost, security
   posture, delivery timeline, or user-visible behavior.
3. Record confirmed decisions, assumptions, trade-offs, and unresolved questions.
4. Never silently choose defaults for high-impact architecture decisions.

## Step 5 — Write artifacts/design-review.md

Create or update `artifacts/design-review.md` using this exact structure:

```markdown
# Design Review

## Review Summary
<overall assessment, key themes, readiness recommendation>

## Review Inputs
- `artifacts/architecture.md` (version / commit)
- `artifacts/requirements.md` (version / commit)

## Findings

| ID | Severity | Area | Finding | Impact | Recommendation | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DR-001 | Critical | Security | ... | ... | ... | ... | Open |

## Agreed Design Decisions
| Decision | Rationale | Owner |
| --- | --- | --- |

## Rejected or Deferred Findings
| ID | Finding | Rationale |
| --- | --- | --- |

## Required Architecture Updates
- <list changes needed in artifacts/architecture.md>

## Open Questions
- <question requiring user or stakeholder input>

## Readiness Recommendation
Ready for planning | Blocked — resolve DR-### before proceeding
```

## Step 6 — Update artifacts/architecture.md

Update `artifacts/architecture.md` for every accepted finding that changes:
components, data flow, technology choices, security controls, operational behavior,
or SDLC pipeline structure.

Keep `artifacts/architecture.md` and `artifacts/design-review.md` consistent.
Do not update for rejected findings unless the rejection itself requires clarification.

## Step 7 — Gate and commit

1. Confirm no unresolved **Critical** or **High** findings remain before signaling
   readiness for the Planner Agent (Step 4).
2. Present a concise summary: finding counts by severity, decisions agreed, blockers.
3. Ask for user confirmation before committing if any Critical or High item is
   unresolved.
4. Commit with:
   ```bash
   git add artifacts/design-review.md artifacts/architecture.md
   git commit -m "docs: capture architecture design review

   Co-Authored-By: GitHub Copilot <noreply@github.com>"
   ```
5. Report whether the architecture is ready for the next SDLC step.
