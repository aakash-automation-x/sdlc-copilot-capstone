---
description: "Single entry point: Orchestrate the entire Agentic SDLC Pipeline end-to-end with human review gates at each step."
agent: agent
---

# /00-orchestrator

**SDLC Pipeline Orchestrator** — The single entry point to run the entire 8-step Agentic SDLC Pipeline end-to-end with human-in-the-loop approval gates.

This is the **only prompt** you need. The orchestrator invokes all agents sequentially and manages the full pipeline.

## Commands

### Start the Full Pipeline
```
/00-orchestrator
```
Runs all 8 steps in sequence:
1. Requirements Agent → `artifacts/requirements.md`
2. Architect Agent → `artifacts/architecture.md`
3. Design Review Agent → `artifacts/design-review.md`
4. Planner Agent → `artifacts/impl-plan.md`
5. Implementation Agent → code + tests
6. Review Agent → review notes / fixes
7. Verify Agent → test suite + content check
8. PR Agent → Pull Request + `artifacts/CHANGELOG.md`

After each step completes:
- ✅ Approve & Proceed to next step
- 🔄 Request Changes (provide feedback to re-run current step)
- ⏸️ Pause Pipeline (save state, resume later)

### Resume at a Specific Step
```
/00-orchestrator resume step=<N>
```
Resume the pipeline at step N (1–8), skipping earlier completed steps.

Example:
```
/00-orchestrator resume step=5
```
Resumes at Step 5 (Implementation Agent), assuming Steps 1–4 have been completed and approved.

### Check Pipeline Status
```
/00-orchestrator status
```
Display the current `ORCHESTRATION_LOG.md`:
- Completed steps and their artifacts
- Current step status
- Option to continue, jump, or restart

### Restart the Pipeline
```
/00-orchestrator restart
```
Clear the orchestration log and begin from Step 1 (Requirements).

## What Happens at Each Review Gate

After each agent completes:

1. **Summary Card** shows:
   - Step name and agent
   - Key artifacts produced
   - 2–3 bullet summary of outputs
   - Changes from the previous step (if any)

2. **Your Decision:**
   - ✅ **Approve & Proceed** — Move to next step automatically
   - 🔄 **Request Changes** — Provide specific feedback; agent re-runs with your input
   - ⏸️ **Pause** — Pipeline pauses; resume anytime with `/00-orchestrator resume step=<N>`

3. **State is Tracked** in `ORCHESTRATION_LOG.md`:
   - Step number, agent name, completion status
   - Artifact path and timestamp
   - Reviewer notes / approval decision

## Example Flow

```
User: /00-orchestrator

Orchestrator: Pre-flight checks...
✅ Repository structure valid
ℹ️ No existing artifacts found
→ Starting fresh from Step 1

---

Orchestrator: Invoking Requirements Agent (/01-requirements)...
[Requirements Agent runs...]
✅ artifacts/requirements.md created

---

## Step 1 Review Gate: Requirements Agent

**Artifact:** artifacts/requirements.md

**Summary:**
- 12 functional requirements (FR-001 to FR-012)
- 8 non-functional requirements (NFR-001 to NFR-008)
- 42 acceptance criteria across all requirements

**Status:** ✅ Complete

---

**What would you like to do?**
1. ✅ Approve & Proceed to Step 2
2. 🔄 Request Changes
3. ⏸️ Pause Pipeline

User: ✅ Approve & Proceed

Orchestrator: Updating ORCHESTRATION_LOG.md...
→ Moving to Step 2 (Architect Agent)

Orchestrator: Invoking Architect Agent (/02-architecture)...
[Architect Agent runs...]
✅ artifacts/architecture.md created

---

## Step 2 Review Gate: Architect Agent

**Artifact:** artifacts/architecture.md

**Summary:**
- Microservices architecture (4 primary services)
- PostgreSQL for persistent data, Redis for caching
- REST API with OpenAPI 3.0 spec

**Changes from Step 1:**
- Architecture supports all 12 functional requirements
- Addresses all 8 non-functional requirements

**Status:** ✅ Complete

---

**What would you like to do?**
1. ✅ Approve & Proceed to Step 3
2. 🔄 Request Changes
3. ⏸️ Pause Pipeline

User: 🔄 Request Changes

User: We need to add an event bus for async messaging. Can you include that?

Orchestrator: Captured feedback. Re-invoking Architect Agent with your input...
[Architect Agent runs with event bus requirement...]
✅ artifacts/architecture.md updated

---

## Step 2 Review Gate (Revised): Architect Agent

**Artifact:** artifacts/architecture.md

**Summary:**
- Microservices architecture (4 primary services)
- PostgreSQL for persistent data, Redis for caching
- **Event bus (Apache Kafka) for async messaging between services**
- REST API with OpenAPI 3.0 spec

**Changes from previous revision:**
- Added Kafka cluster for event streaming
- Updated deployment topology
- Added event flow diagrams

**Status:** ✅ Complete

---

**What would you like to do?**
1. ✅ Approve & Proceed to Step 3
2. 🔄 Request Changes
3. ⏸️ Pause Pipeline

User: ✅ Approve & Proceed

Orchestrator: Updating ORCHESTRATION_LOG.md...
→ Moving to Step 3 (Design Review Agent)
[... and so on ...]
```

## Pipeline State Tracking

The orchestrator maintains `ORCHESTRATION_LOG.md` in your repository:

```markdown
# SDLC Pipeline Orchestration Log

| Step | Agent | Status | Artifact | Started | Completed | Notes |
|------|-------|--------|----------|---------|-----------|-------|
| 1 | Requirements | ✅ Approved | artifacts/requirements.md | 2024-01-15 10:00 | 2024-01-15 10:15 | No changes requested |
| 2 | Architect | ✅ Approved | artifacts/architecture.md | 2024-01-15 10:16 | 2024-01-15 10:45 | Requested: add event bus; 1 revision |
| 3 | Design Review | in-progress | artifacts/design-review.md | 2024-01-15 10:46 | — | — |
```

## When to Use Each Command

| Goal | Command |
|------|---------|
| Start fresh pipeline | `/00-orchestrator` |
| Resume after pause | `/00-orchestrator resume step=3` |
| Check current progress | `/00-orchestrator status` |
| Restart entire pipeline | `/00-orchestrator restart` |
| Jump to Step 5 (skip 1–4) | `/00-orchestrator resume step=5` |

Follow `.claude/agents/orchestrator.agent.md` for full orchestrator logic and error handling.
