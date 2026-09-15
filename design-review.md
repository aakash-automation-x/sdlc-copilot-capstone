# Design Review — Customer Login for Ecommerce Application

- **Story ID:** US-LOGIN-001
- **Artifact under review:** [architecture.md](architecture.md)
- **Cross-checked against:** [requirements.md](requirements.md)
- **Reviewer:** Design Review Agent (senior-architect pass)
- **Status:** Reviewed — accepted findings applied to `architecture.md`

## 1. Review Summary

The architecture is well-aligned with the requirements and traceable
(every component cites an `FR`/`NFR`). The core login happy-path, lockout, and
token design are sound. The review found **12 findings**: 1 Critical, 4 High,
5 Medium, 2 Low. The Critical and High findings centered on an
anti-enumeration conflict, protected-route access control, CSRF on the cookie
refresh endpoint, refresh-token reuse detection, and identifier normalization.
Five high-impact decisions were escalated to the stakeholder and resolved (see
§3). All accepted findings are reflected in `architecture.md`.

## 2. Findings

| ID | Severity | Area | Finding | Impact | Recommendation | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DR-001 | Critical | Security / Privacy | `423 Locked` (and locked-only messaging) is returned only for real accounts, leaking account existence — conflicts FR-013 vs NFR-005. | Attacker can enumerate valid accounts via lockout behavior. | Return a generic 401 even when locked; add IP-based lockout in addition to per-account. | Accepted (Option A): generic 401 + IP-based lockout. | Applied |
| DR-002 | High | Security / Access Control | Architecture covers login/refresh but not how protected routes verify the access token (A01). | Without a documented verification path, protected resources may be unprotected. | Add a JWT verification middleware component and describe protected-route access control. | Accepted. | Applied |
| DR-003 | High | Security | Cookie-based refresh endpoint is exposed to CSRF; SameSite alone is insufficient defense-in-depth. | CSRF could trigger silent token refresh/logout. | SameSite=Strict cookie + double-submit CSRF token on refresh/logout. | Accepted (Option A). | Applied |
| DR-004 | High | Security | Rotating refresh tokens without reuse detection cannot detect a stolen/replayed token. | Stolen refresh token stays valid until natural expiry. | Detect reuse of a rotated token and revoke the entire token family (NFR-007). | Accepted. | Applied |
| DR-005 | High | Reliability | Redis is a single dependency for lockout/rate-limit with no defined failure mode. | Redis outage could block all logins (NFR-011) or disable brute-force protection (NFR-006). | Define behavior on Redis outage. | Accepted: fail open + alert + DB-counter fallback (favor availability). | Applied |
| DR-006 | Medium | Functional | Design always issues a 30-day refresh token; FR-012 ties persistence to the Remember Me checkbox. | Sessions persist longer than the user chose — security/privacy concern. | Differentiate lifetime by rememberMe. | Accepted: Remember Me = 30d refresh; unchecked = short ~1-day session token. | Applied |
| DR-007 | Medium | Functional / Security | No identifier normalization (email case-folding, mobile to E.164) before lookup/lockout keying. | Case/format variants could bypass per-account lockout and cause duplicate identities. | Normalize identifier before lookup and before keying lockout/rate-limit. | Accepted. | Applied (ties to OQ-02) |
| DR-008 | Medium | Security / Ops | JWT signing keys and DB/Redis credentials have no defined secret-management/rotation strategy. | Hard-coded/unrotated secrets violate NFR-008/OWASP A02. | Use a secrets manager (Vault/cloud KMS); support signing-key rotation via `kid`. | Accepted. | Applied |
| DR-009 | Medium | Security | Session-loss on reload (access token in memory) implies a silent-refresh flow that is undocumented. | Ambiguous UX/impl; risk of insecure workarounds. | Document silent-refresh on app load via the refresh cookie. | Accepted. | Applied |
| DR-010 | Medium | Security / DoS | No max-length/input bounds on password/identifier (bcrypt 72-byte limit, large-input DoS). | Long inputs waste hashing CPU; bcrypt silently truncates. | Enforce input length bounds; prefer argon2id; validate identifier format. | Accepted. | Applied |
| DR-011 | Low | Observability | Only audit logging is described; no metrics/tracing or defined health probes for the auth API. | Harder to meet NFR-011/NFR-013 operationally. | Add metrics + health/readiness endpoints and login/lockout alerts. | Accepted. | Applied |
| DR-012 | Low | Data / Ops | Audit-log retention/partitioning undefined (OQ-03). | Unbounded table growth over time. | Define retention + partition/archival once policy known. | Deferred — tracked as OQ-03. | Open |

## 3. Agreed Design Decisions (Escalated)

| # | Decision | Resolves | Traces to |
| --- | --- | --- | --- |
| DD-1 | On lockout, return the **same generic 401** as invalid credentials; add **IP-based lockout** alongside per-account lockout. | DR-001 | FR-013, NFR-005 |
| DD-2 | On **Redis outage, fail open**: allow login, raise an alert, and fall back to a database-backed attempt counter. | DR-005 | NFR-006, NFR-011 |
| DD-3 | **Remember Me = 30-day rotating refresh**; **unchecked = short ~1-day session** token (session cookie), no long-lived refresh. | DR-006 | FR-012, NFR-007 |
| DD-4 | Protect cookie endpoints with **SameSite=Strict + double-submit CSRF token** on `/auth/refresh` and `/auth/logout`. | DR-003 | NFR-007, NFR-008 |
| DD-5 | Implement **refresh-token reuse detection with token-family revocation**. | DR-004 | NFR-007 |

## 4. Requirements Coverage Check

- All FR-001…FR-016 and NFR-001…NFR-014 remain covered by a component in
  `architecture.md` §4; no orphan requirements introduced.
- New components added for accepted findings (Access-Token Verifier, CSRF
  protection, reuse detection, secrets management, silent-refresh, metrics/health)
  all trace back to existing NFR IDs (NFR-006, NFR-007, NFR-008, NFR-011,
  NFR-013) — no new requirements invented.
- Open item OQ-03 (audit retention, DR-012) remains an open question for the
  Planner/operations, not a blocker for implementation planning.

## 5. Gate Decision

No Critical or High finding remains unresolved: DR-001…DR-005 are accepted and
applied; DR-012 is a non-blocking deferred Low. **Design review passes.**

---

### Traceability

Each finding cites the architecture area and the `FR`/`NFR` it affects; each
agreed decision (DD-1…DD-5) maps to the finding(s) it resolves and the
requirement IDs it satisfies, per the `sdlc-traceability` skill.

**Next step:** hand off to `/04-impl-plan` (Planner Agent).
