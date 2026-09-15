# Requirements — Customer Login for Ecommerce Application

- **Story ID:** US-LOGIN-001
- **Source:** `userstory.docx` (Title: *Login to Ecommerce Account*)
- **Priority:** High
- **Status:** Confirmed (clarifications resolved with stakeholder on 2026-09-15)

## 1. User Story & Business Objective

> **As a** registered ecommerce customer,
> **I want** to securely log in to my account using my email address or mobile
> number and password,
> **So that** I can access my personal account, view order history, manage my
> cart and wishlist, update shipping details, and complete purchases faster.

**Business objective:** Provide secure, low-friction authentication that lets
registered customers resume shopping and complete purchases quickly, reducing
checkout abandonment while protecting customer accounts from unauthorized access.

## 2. Scope

### In Scope
- Login page/form UI (email **or** mobile number + password).
- Credential authentication for registered users via an authentication
  service/API.
- Client- and server-side field validation and error messaging.
- Password masking with optional show/hide toggle.
- "Remember Me" persistent session option.
- Account lockout / brute-force protection.
- Secure session establishment via JWT (access + rotating refresh tokens).
- Post-login redirect, including return to a prior checkout/cart destination.
- Navigation entry points (links) to Forgot Password and Registration.
- Audit logging of login attempts.

### Out of Scope
- User registration flow (assumed to exist; only linked from login).
- Forgot-password / password-recovery flow (only linked from login).
- Multi-factor authentication (MFA/2FA) — deferred to a future story.
- Social / federated login (Google, Facebook, etc.).
- Mobile OTP-based login (mobile uses the same password as email login).
- Native mobile applications (web app only for this story).
- Account dashboard, cart, wishlist, and order-history feature internals
  (login only guarantees authenticated access to them).
- Localization / multi-language support (English only).

## 3. Actors & Stakeholders

| Actor | Role |
| --- | --- |
| Registered Customer | Primary user authenticating to access their account. |
| Authentication Service/API | Validates credentials, issues/rotates tokens, enforces lockout. |
| Ecommerce Web Frontend (SPA) | Renders the login form and manages client-side session state. |
| Security / Compliance | Owns OWASP, GDPR, and audit-logging obligations. |
| Product Owner | Approves scope and acceptance criteria. |

## 4. Confirmed Decisions (Clarifications)

| Topic | Decision |
| --- | --- |
| Platform / stack | Web app only — SPA frontend + REST API backend. |
| Auth mechanism | Password login with JWT access + rotating refresh tokens. |
| Mobile login | Password-based (same password as email login); no OTP. |
| Lockout policy | 5 failed attempts → 15-minute temporary lockout. |
| Remember Me | Persists session for 30 days. |
| MFA/2FA | Out of scope (future story). |
| Token lifetimes | Access token 15 min; refresh token 30 days, rotating. |
| Performance | Auth API p95 < 500 ms; login page interactive < 2 s. |
| Accessibility | WCAG 2.1 AA. |
| Localization | Out of scope (English only). |
| Compliance | OWASP Top 10, GDPR-aligned PII handling, audit all login attempts. |

## 5. Functional Requirements

| ID | Requirement |
| --- | --- |
| **FR-001** | The system shall display a login page/form when the user selects **Login** / **Sign In** from the web app. |
| **FR-002** | The login form shall accept a single identifier field that supports **either** a registered email address **or** a registered mobile number, plus a password field. |
| **FR-003** | On submit with a valid registered identifier and correct password, the system shall authenticate the user via the authentication service/API. |
| **FR-004** | On successful authentication, the system shall establish a secure session and issue a JWT access token (15 min) and a rotating refresh token (30 days). |
| **FR-005** | On successful login, the system shall redirect the user to their prior checkout/cart destination if one exists, otherwise to the homepage or account dashboard. |
| **FR-006** | On invalid credentials (wrong identifier or password), the system shall display a single generic error message — *"Invalid email/mobile number or password."* — that does **not** reveal which field was incorrect. |
| **FR-007** | When the identifier field is empty on submit, the system shall display *"Email/mobile number is required."* |
| **FR-008** | When the password field is empty on submit, the system shall display *"Password is required."* |
| **FR-009** | The password field shall mask input by default and provide a user-toggleable show/hide control. |
| **FR-010** | The login page shall provide a **Forgot Password** link that navigates to the password-recovery flow (flow itself out of scope). |
| **FR-011** | The login page shall provide a **Register / Sign Up** link that navigates to the registration flow (flow itself out of scope). |
| **FR-012** | The login form shall provide a **Remember Me** option; when selected and login succeeds, the session shall persist for 30 days. |
| **FR-013** | After 5 consecutive failed login attempts for an account, the system shall temporarily block further login attempts for that account for 15 minutes and display a lockout message without revealing account existence. |
| **FR-014** | Only registered users shall be able to authenticate; unregistered identifiers shall yield the generic invalid-credentials message (FR-006), not an account-not-found message. |
| **FR-015** | On successful login, the system shall present the user as authenticated consistently across the application (persistent authenticated state until logout or session expiry). |
| **FR-016** | The system shall record an audit log entry for every login attempt (success and failure) including timestamp, identifier reference, source IP, and outcome — without storing the password. |

## 6. Non-Functional Requirements

| ID | Category | Requirement (Measurable Target) |
| --- | --- | --- |
| **NFR-001** | Performance | Authentication API responses shall have p95 latency < 500 ms under expected load. |
| **NFR-002** | Performance | The login page shall reach interactive state in < 2 s on a standard broadband connection. |
| **NFR-003** | Security — Transport | All login traffic shall use HTTPS/TLS 1.2+; non-HTTPS requests shall be redirected or rejected. |
| **NFR-004** | Security — Credentials | Passwords shall be stored only as salted, adaptive one-way hashes (e.g. bcrypt/argon2) and shall never be logged, displayed, or returned in any response. |
| **NFR-005** | Security — Enumeration | Error messages and response timing shall not reveal whether an identifier is registered (uniform response for invalid identifier vs. wrong password). |
| **NFR-006** | Security — Brute Force | The system shall enforce lockout per FR-013 and apply rate limiting on the login endpoint to mitigate automated credential-stuffing attacks. |
| **NFR-007** | Security — Session | Access tokens shall expire in 15 min; refresh tokens shall rotate on use, expire in 30 days, and be revocable server-side; tokens shall be stored to mitigate XSS/CSRF (e.g. httpOnly, Secure, SameSite cookies for refresh). |
| **NFR-008** | Security — Standards | The implementation shall adhere to the OWASP Top 10, with particular attention to A01 (Access Control), A02 (Cryptographic Failures), and A07 (Identification & Authentication Failures). |
| **NFR-009** | Privacy | Personal data (email, mobile) shall be handled in a GDPR-aligned manner: minimal collection, masked in logs, and protected at rest and in transit. |
| **NFR-010** | Accessibility | The login page shall conform to WCAG 2.1 Level AA (labels, focus order, contrast, keyboard operability, screen-reader-announced errors). |
| **NFR-011** | Availability | The login capability shall target 99.9% monthly availability. |
| **NFR-012** | Usability | Validation and authentication errors shall be shown inline near the relevant field and announced to assistive technology. |
| **NFR-013** | Observability | Login attempts, lockouts, and token issuance shall be audit-logged (FR-016) and retained per policy for security investigation, without PII in plain text. |
| **NFR-014** | Compatibility | The login page shall function on current versions of major browsers (Chrome, Edge, Firefox, Safari) and be responsive across desktop and mobile viewports. |

## 7. Data Requirements

| Data element | Notes |
| --- | --- |
| Identifier (email or mobile) | Input; validated for format (email pattern or mobile pattern). PII — masked in logs (NFR-009). |
| Password | Input only; never persisted in plaintext or logged (NFR-004). |
| Remember Me flag | Boolean; controls refresh-token/session persistence (FR-012). |
| Access token (JWT) | Short-lived (15 min); carries authenticated identity/claims. |
| Refresh token | Rotating, 30-day, revocable server-side. |
| Failed-attempt counter & lockout state | Per-account counter + lockout expiry timestamp (FR-013). |
| Audit log record | Timestamp, identifier reference, source IP, outcome, no secrets (FR-016). |

## 8. Integration Requirements

| ID ref | Integration |
| --- | --- |
| FR-003, FR-004 | Authentication service/API for credential verification and token issuance. |
| FR-014 | User account store (registration is upstream dependency) for identity lookup. |
| FR-010 | Password-recovery flow (link target only). |
| FR-011 | Registration flow (link target only). |
| FR-005 | Session/redirect state to return users to a prior checkout/cart destination. |

## 9. Security & Privacy Requirements

Covered by NFR-003 through NFR-009 and NFR-013. Key mandates:
- HTTPS-only transport (NFR-003).
- Hashed, never-displayed passwords (NFR-004).
- Non-enumerable, generic error responses (FR-006, FR-014, NFR-005).
- Lockout + rate limiting against brute force (FR-013, NFR-006).
- Secure, rotating, revocable tokens (NFR-007).
- OWASP Top 10 adherence and GDPR-aligned PII handling (NFR-008, NFR-009).
- Full audit trail of login attempts (FR-016, NFR-013).

## 10. Operational Requirements

- **Availability:** 99.9% monthly for the login capability (NFR-011).
- **Monitoring/Alerting:** Alert on abnormal failed-login or lockout rates
  (potential credential-stuffing).
- **Logging:** Structured, PII-masked audit logs retained per security policy.
- **Configurability:** Lockout threshold (5), lockout window (15 min), and token
  lifetimes should be configurable without code changes.

## 11. Acceptance Criteria (Testable)

Preserved from the source story and made measurable. Each criterion cites the
requirement(s) it verifies.

| AC | Given / When / Then | Verifies |
| --- | --- | --- |
| **AC-01** | **Given** a user on the web app, **when** they click Login/Sign In, **then** the login form is displayed. | FR-001 |
| **AC-02** | **Given** a registered user, **when** they enter a valid email/mobile and correct password and click Login, **then** they are authenticated and redirected to the homepage, dashboard, or prior checkout/cart page. | FR-002, FR-003, FR-004, FR-005 |
| **AC-03** | **Given** an incorrect identifier or password, **when** the user clicks Login, **then** the message *"Invalid email/mobile number or password."* is shown without indicating which field failed. | FR-006, FR-014, NFR-005 |
| **AC-04** | **Given** an empty identifier and/or password, **when** the user clicks Login, **then** *"Email/mobile number is required."* and/or *"Password is required."* is shown. | FR-007, FR-008 |
| **AC-05** | **Given** the user types a password, **then** it is masked by default and can be toggled visible/hidden. | FR-009 |
| **AC-06** | **Given** the user clicks Forgot Password, **then** they are navigated to the password-recovery flow. | FR-010 |
| **AC-07** | **Given** the user selects Remember Me and logs in successfully, **then** the session persists for 30 days across visits. | FR-012 |
| **AC-08** | **Given** 5 consecutive failed attempts on an account, **when** a 6th attempt is made within the window, **then** login is temporarily blocked for 15 minutes with a non-enumerating message. | FR-013, NFR-006 |
| **AC-09** | **Given** a successful login, **then** a secure session is created and the user appears logged in across the application until logout or expiry. | FR-004, FR-015, NFR-007 |
| **AC-10** | **Given** any login interaction, **then** it occurs over HTTPS and the attempt is recorded in the audit log without exposing the password. | NFR-003, FR-016, NFR-004 |
| **AC-11** | **Given** the login page, **when** evaluated against WCAG 2.1 AA, **then** it passes (labels, contrast, keyboard nav, screen-reader error announcements). | NFR-010, NFR-012 |
| **AC-12** | **Given** expected load, **then** the auth API p95 latency is < 500 ms and the login page is interactive in < 2 s. | NFR-001, NFR-002 |

## 12. Assumptions

- A registration flow and populated user account store already exist; login only
  authenticates existing users.
- A password-recovery flow exists (or is being built separately) as the target of
  the Forgot Password link.
- The authentication service/API is available and exposes credential
  verification and token issuance/rotation.
- Mobile-number login authenticates with the same password as email login.
- English-only UI; no localization required for this story.
- "Remember Me" persistence (30 days) aligns with the refresh-token lifetime.

## 13. Dependencies

- User registration functionality (upstream).
- Authentication service/API.
- Password-recovery functionality (link target).
- User account/dashboard module (post-login destination).
- Cart/checkout state for post-login redirect (FR-005).

## 14. Open Questions

| ID | Question | Impact |
| --- | --- | --- |
| **OQ-01** | Should the identifier be a single combined field or two distinct email/mobile fields? Assumed single combined field (FR-002). | UI/validation design. |
| **OQ-02** | Is there an existing mobile-number format/region standard (E.164?) to validate against? | Validation rules for FR-002. |
| **OQ-03** | What is the audit-log retention period required by security policy? | NFR-013 operational config. |
| **OQ-04** | Is the SPA framework and auth library already mandated (e.g. React + specific auth SDK), or open to the Architect? | Architecture (Step 2). |
| **OQ-05** | Should lockout notify the account owner (e.g. email alert) on repeated failures? | Potential added FR if required. |

---

### Traceability

Requirement IDs (`FR-###`, `NFR-###`) established here are the single source of
truth. Downstream artifacts (`architecture.md`, `impl-plan.md`, tests, review,
PR) must reference these IDs rather than restating them. See the
`sdlc-traceability` skill.

**Next step:** hand off to `/02-architecture` (Architect Agent).
