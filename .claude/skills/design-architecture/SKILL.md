---
name: design-architecture
description: "Design a high-level system architecture from artifacts/requirements.md and document it in artifacts/architecture.md with component diagrams, technology choices, data flows, and traceability to FR/NFR IDs. Used by the Architect Agent (Step 2)."
---

# Skill: Design Architecture

This skill is loaded by the **Architect Agent** (Step 2 of the Agentic SDLC Pipeline)
to produce a documented, traceable system architecture from approved requirements.
Follow these steps exactly.

## Step 1 — Read the approved requirements

1. Read `artifacts/requirements.md` before proposing any architecture.
2. Load the [[sdlc-traceability]] skill to link every architectural component to its
   `FR-###` or `NFR-###` driver.
3. Identify: functional requirements, non-functional requirements, constraints,
   integrations, data needs, security requirements, operational expectations,
   assumptions, risks, and unresolved questions.
4. Do not invent architectural drivers absent from `artifacts/requirements.md`.
   Document any assumption clearly.

## Step 2 — Clarify architecture-impacting questions

Before designing, identify any missing or ambiguous decisions that materially affect
the architecture. Ask focused questions when a decision cannot be safely assumed:

- Hosting model (cloud, on-prem, serverless)
- Persistence (SQL, NoSQL, file-based, in-memory)
- Authentication and authorisation mechanism
- Deployment target (container, VM, managed service)
- Compliance or regulatory constraints
- Scale and performance expectations
- Integration boundaries (third-party APIs, internal services)

Record confirmed decisions, assumptions, trade-offs, and unresolved questions.

## Step 3 — Define the architecture

Propose and evaluate:

| Area | Questions to answer |
| --- | --- |
| **Components** | What are the key system components and what is each one responsible for? |
| **Data flow** | How does data move from input to output across components? |
| **Technology choices** | What stack satisfies the requirements? Why? What are the trade-offs? |
| **Security** | How is authentication, authorisation, input validation, and secret management handled? |
| **Reliability** | How are failures, timeouts, and retries handled? What is the recovery path? |
| **Observability** | How is the system monitored, logged, and debugged in production? |
| **Scalability** | How does the system handle increased load? What are the bottlenecks? |
| **Deployment** | How is the system built, packaged, and deployed? What does CI/CD look like? |
| **SDLC pipeline** | Which agents, prompts, rules, skills, and hooks participate? |

Prefer simple, evolvable architecture over unnecessary complexity. Make technology
recommendations based on requirements, constraints, maintainability, security, and
delivery risk.

## Step 4 — Write artifacts/architecture.md

Create or update `artifacts/architecture.md` using this exact structure:

```markdown
# Architecture

## Overview
<2-3 sentence summary of the proposed architecture>

## Architectural Goals and Drivers
<trace to FR-### / NFR-### from artifacts/requirements.md>

## Recommended Architecture
<description of the overall approach>

## Component Diagram
```mermaid
<component or C4 diagram>
```

## Key Components and Responsibilities
| Component | Responsibility | FR/NFR |
| --- | --- | --- |

## Data Flow
```mermaid
<sequence or flow diagram>
```

## Technology Choices
| Decision | Choice | Rationale | Trade-offs |
| --- | --- | --- | --- |

## SDLC Pipeline Components
| Type | Name | Purpose |
| --- | --- | --- |
| Agent | ... | ... |
| Skill | ... | ... |
| Rule | ... | ... |

## Security Considerations
<auth, input validation, secrets management, OWASP mitigations>

## Reliability and Observability
<failure handling, logging, monitoring>

## Scalability and Performance
<bottlenecks, scaling strategy>

## Deployment
<build, package, CI/CD>

## Assumptions and Constraints
- <assumption or constraint>

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |

## Open Questions
- <question requiring user or stakeholder input>
```

### Rules

- Keep the document clear enough for the Design Review, Planner, Implementation,
  and Verify agents to continue without reinterpreting the architecture.
- Ensure diagrams and written sections are consistent with each other.
- Separate confirmed decisions from assumptions and open questions.
- Escalate high-impact uncertainties to the user instead of silently choosing defaults.

## Step 5 — Review and commit

1. Verify `artifacts/architecture.md` traces back to `artifacts/requirements.md`
   and does not conflict with approved requirements.
2. Present a concise summary and note any open questions.
3. Ask for user confirmation before committing if unresolved architectural decisions
   materially affect implementation.
4. Commit with:
   ```bash
   git add artifacts/architecture.md
   git commit -m "docs: define architecture for <feature-name>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
   ```
5. Report the commit result, remaining risks, and open questions before handing
   off to the **Design Review Agent** (Step 3).
