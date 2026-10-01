---
description: "Secure, clear, DRY coding standards enforced during implementation and review."
applyTo: "**/*.{js,jsx,ts,tsx,py,java,cs,go,rb,php}"
---

# Code Quality Standards

Applies to all production source code generated or modified in this repository.

## Security (OWASP Top 10)

- Never hard-code, log, or return secrets, tokens, passwords, or credentials.
  Read them from environment variables or a secrets manager.
- **Before every commit:** Review all staged changes for secrets:
  - API keys, tokens, auth credentials (GitHub, Jira, Confluence, MCP, AWS, etc.)
  - MCP configuration files (`mcp.json`, `.mcp.json`)
  - Environment files (`.env`, `.env.local`)
  - SSL/TLS certificates and private keys (`.pem`, `.key`, `.pfx`, `.p12`)
  - Database passwords, connection strings, or connection configs
  - Any hardcoded bearer tokens, API keys, or session identifiers
  - When in doubt, add the pattern to `.gitignore` before committing
- Ensure all secrets are listed in `.gitignore` with clear patterns to prevent
  accidental commits. Never trust a file to be "already ignored" — verify with
  `git status` and `git check-ignore -v <filename>`.
- Validate and sanitize all external and user-supplied input at the boundary.
  Guard against injection (SQL, command, XSS) and broken access control.
- Enforce authentication and authorization on every protected operation.
- Use parameterized queries and safe, maintained libraries. Flag and avoid
  known-vulnerable package versions.
- For the login use case specifically: mask passwords, never store or transmit
  them in plain text, use HTTPS, and return generic auth errors that do not
  reveal whether the identifier or the password was wrong.

## Error handling

- Handle API failures, timeouts, missing files, empty inputs, and `Not Found`
  states gracefully with clear messages — no unhandled exceptions.
- Fail closed on security-relevant errors.

## Clarity and DRY

- Use self-explanatory function and variable names; keep control flow readable
  without relying on comments.
- Extract duplicated logic into a single shared, well-named function or module.
- Add a comment only to explain *why* something non-obvious is done — never to
  restate what the code already shows.

## Scope discipline

- Implement only what an approved task in `impl-plan.md` requires.
- Do not add features, refactors, or abstractions beyond the task scope.
- Follow existing project structure, naming, and style conventions.
