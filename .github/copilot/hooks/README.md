# Copilot Hooks

Lifecycle automation that enforces the Agentic SDLC pipeline gates. Hooks are
declared in [`hooks.json`](../hooks.json) and implemented as small, dependency-free
Node.js scripts in this folder.

## Events

| Event | Hook | Purpose |
| --- | --- | --- |
| `SessionStart` | `validate-artifacts.js` | Print the pipeline status (which SDLC artifacts exist) so no step starts without its upstream deliverable. |
| `PreToolUse` (shell / git) | `check-secrets.js` | Scan pending changes and **block** any shell/commit action that would introduce a secret, token, or key. |
| `Stop` | `check-secrets.js --staged` | Final secret scan of staged changes before the turn ends. |

A hook that exits non-zero **blocks** the action; exit `0` allows it.

## Scripts

- **`check-secrets.js`** — regex scan of the git diff for AWS keys, private keys,
  GitHub/Slack tokens, generic `key/secret/token/password` assignments, and Jira/
  Confluence tokens. Use `--staged` to scan only staged changes.
- **`validate-artifacts.js`** — reports which pipeline artifacts
  (`requirements.md` → `impl-plan.md`) exist. Use `--strict <step>` to fail when a
  step's upstream artifacts are missing (e.g. block `05-implementation` if
  `impl-plan.md` is absent).

## Run manually

```powershell
node .github/copilot/hooks/check-secrets.js
node .github/copilot/hooks/validate-artifacts.js --strict 05-implementation
```

## Requirements

- Node.js on `PATH` (scripts use only the standard library).
- Run from the repository root so relative artifact paths resolve.

> These hooks complement the `code-quality` instructions (secure-by-default code)
> and the human-in-the-loop rule: they are guardrails, not a replacement for
> human review.
