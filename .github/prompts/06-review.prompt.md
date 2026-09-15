---
description: "Kick off Step 6: structured peer code review before the PR."
agent: agent
---

# /06-review

Run the **Review Agent** for Step 6 of the Agentic SDLC pipeline.

Review the current implementation against `requirements.md` as an impartial peer
reviewer. Evaluate each area below and cite the file, function, and requirement
ID for every finding. Classify each as **Blocker / Major / Minor / Nit**.

| Review Area | Review Question |
| --- | --- |
| Correctness | Does each component behave as specified in `requirements.md`? |
| Security | Are secrets excluded from output? Is user input validated? |
| Error Handling | Are API failures, missing files, and empty repos handled gracefully? |
| Test Coverage | Do tests cover the happy path AND `Not Found` / missing-field edge cases? |
| Code Clarity | Are function names self-explanatory? Is logic easy to follow without comments? |
| DRY Principle | Is there duplicated logic to refactor into a shared function? |
| Dependency Safety | Are any known-vulnerable package versions present? |

Apply fixes that are clearly correct and in scope, re-run tests, and re-review.
Do not signal PR-ready while any **Blocker** or **Major** finding is unresolved.

Follow `.github/instructions/code-quality.instructions.md`. Hand off to
`/07-verify`.
