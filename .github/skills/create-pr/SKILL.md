---
name: create-pr
description: "Create a Pull Request with a complete description (Summary, Changes Made, Test Evidence, Known Limitations, Reviewer Checklist), changelog entry, and reviewer checklist. Use in Step 8 of the SDLC pipeline (PR Agent) after the Verify Agent has passed."
user-invocable: true
---

# Skill: Create PR

This skill is loaded by the **PR Agent** (Step 8 of the Agentic SDLC Pipeline) to
package the verified implementation into a pull request ready for human review.
Follow these steps exactly.

## Step 1 — Establish PR context

1. Read `artifacts/requirements.md` to collect all `FR-###` and `NFR-###` IDs,
   acceptance criteria, and traceability identifiers.
2. Use the `sdlc-traceability` skill (`.github/skills/sdlc-traceability/SKILL.md`)
   to build the traceability matrix that goes into the PR description.
3. Determine the source branch, target branch, and full change set:
   ```bash
   git status
   git diff main...HEAD
   ```
4. Gather the verification results from the Verify Agent and the outcome from the
   Review Agent — the PR must carry real evidence, not assumptions.

## Step 2 — Generate the PR description

Produce a description that fills in **all five** required sections below, in this
order. Base every section on the actual diff, test run, and requirements. Mark
anything that cannot be located or confirmed as `Not Found` — never invent files,
results, or behavior.

```markdown
## Summary
<2-3 sentence overview of what was built and why>

## Changes Made
- `<path/to/file>` — <what changed and why>
- `<path/to/file>` — <what changed and why>

## Test Evidence
```
<pasted test run output>
```
<or a link to CI results>

## Known Limitations
- <anything marked 'Not Found', deferred, or out of scope>

## Reviewer Checklist
- [ ] Requirements in `artifacts/requirements.md` are met and traceable
- [ ] All tests pass with adequate coverage for critical paths
- [ ] Security and error handling were reviewed; no secrets are committed
- [ ] Changelog entry added and accurate
- [ ] Known limitations are understood and acceptable
```

### Rules for each section

| Section | Rule |
| --- | --- |
| **Summary** | 2-3 sentences; state what was built and why it was needed. |
| **Changes Made** | List every added or modified file with the reason for the change. |
| **Test Evidence** | Paste the actual test run output or a CI link — never claim tests pass without proof. |
| **Known Limitations** | Carry forward every `Not Found` item, deferred task, and out-of-scope item from prior steps. |
| **Reviewer Checklist** | Each item must be objective, independently verifiable, and tied to an acceptance criterion or quality gate. |

## Step 3 — Add the changelog entry

1. Open (or create) `artifacts/CHANGELOG.md`.
2. Add a concise, user-facing entry under the correct version / Unreleased heading.
3. Follow the project's existing changelog convention (Keep a Changelog + semantic
   versioning) — do not introduce a new format.
4. Reference the relevant `FR-###` / `NFR-###` IDs and, where applicable, the
   user-story name for traceability.

## Step 4 — Create the pull request

1. Create the PR from the source branch to the target branch using the GitHub CLI:
   ```bash
   gh pr create \
     --title "<descriptive title under 70 chars>" \
     --body "$(cat <<'EOF'
   <generated description from Step 2>
   EOF
   )"
   ```
2. Confirm the PR opened successfully and report the **PR URL**, **title**, and
   **target branch** to the user.
3. Never push directly to a protected branch or self-merge — the PR must remain
   open for human review and approval.
4. Escalate any ambiguous or high-impact decisions to the user rather than
   resolving them silently.

## Step 5 — Final report

After the PR is created, report:

- PR URL and title
- Traceability matrix (FR/NFR → TASK → code → test → PR)
- Any remaining `Not Found` items, open questions, or deferred work so the
  reviewer has full context
