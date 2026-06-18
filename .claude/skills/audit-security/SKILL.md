---
name: audit-security
description: Security analysis for source code: OWASP Top 10:2025, injection, access control, supply chain, crypto failures, insecure deserialization. Returns severity-classified findings. Does not modify files.
updated: 2026-06-13
---

# Audit — Security

## 1§ Purpose
Identify security vulnerabilities in source code, configuration files, and dependency
manifests. Covers all 10 OWASP Top 10:2025 categories, credential exposure, insecure
deserialization, supply chain risks, and security logging gaps. Returns a
severity-classified findings table.

Scope boundary: security vulnerabilities only — the adversarial lens.
General code quality, waste, and artifact review are out of scope — this skill is the adversarial security lens only.
Runtime credential prevention → `check-credentials` hook (already active).

## 2§ Use when
- User asks for a security audit, OWASP scan, or vulnerability check
- Before a public launch or before handling real user data
- After adding new auth, payment, file handling, or external API integration code
- User says "is this secure?", "check for vulnerabilities", "security review"

## 3§ Hard constraints
- Never modify source files. Analysis only. Fixes go through the main session.
- Report specific locations: file + line number. Never say "the auth module is weak" without
  a specific location.
- Check configuration files, `.env.example`, `package.json`, `requirements.txt`,
  `Cargo.toml`, and CI/CD definitions — not only source files.
- Always check for hardcoded credentials even if `check-credentials` hook is active —
  the hook prevents future writes; this audit catches what already exists.
- Distinguish confirmed findings from suspected ones in the output.
- False-positive discipline: do not flag parameterized queries, intentional non-sensitive
  logging, `yaml.safe_load()`, or mock credentials in test fixtures as vulnerabilities.

## 4§ OWASP Top 10:2025 coverage
Reference: [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
Apply all relevant dimensions. Skip dimensions with no applicable code in scope.

A01 Broken Access Control — missing authorization checks on routes or endpoints; insecure
direct object references (sequential or guessable IDs); path traversal in file operations;
CORS misconfiguration; horizontal privilege escalation (user A accessing user B's resource);
force-browsing to privileged pages.

A02 Security Misconfiguration — debug mode or verbose errors enabled in production paths;
default credentials not changed; directory listing enabled; unnecessary exposed endpoints;
missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options); overly
permissive IAM or cloud service roles; publicly exposed cloud storage (S3 buckets, blobs).

A03 Software Supply Chain Failures — dependency manifests (`package.json`, `requirements.txt`,
`Cargo.toml`, `pom.xml`): flag packages at major versions known for CVEs; missing lock
files; wildcard version ranges (`*`, `^latest`, `>=x`); unverified build scripts or
unsafe npm/pip lifecycle hooks; CI/CD pipelines that execute untrusted code on pull
requests; missing SBOM or dependency review step.

A04 Cryptographic Failures — hardcoded API keys, passwords, tokens, or private keys;
weak or deprecated algorithms (MD5/SHA-1 for passwords, DES, 3DES, RC4); AES-ECB mode
(no semantic security); HTTP where HTTPS is required; weak key derivation (single hash
without salt or iterations); predictable IVs or nonces; sensitive data (PII, tokens)
stored unencrypted.

A05 Injection — SQL built by string concatenation or f-string interpolation; command
injection via `system()`, `exec()`, `subprocess` shell=True with user input; template
injection; LDAP/XPath injection; `eval()` or `Function()` on user-controlled strings;
second-order injection (stored input later used in a query without re-sanitization).

A06 Insecure Design — absence of rate limiting on auth, password reset, or sensitive
endpoints; missing input validation at trust boundaries (service-to-service calls treated
as trusted without verification); business logic flaws (negative quantities, skipped
workflow steps, replay attacks on one-time tokens); single security control as sole
defense (failure = full bypass).

A07 Authentication Failures — missing MFA on admin or sensitive routes; session tokens
in URLs or logs; no token expiry or rotation on privilege change; weak JWT validation
(`alg:none`, missing signature check, insufficient claims validation); session fixation;
passwords hashed with MD5, SHA-1, or SHA-256 without a slow KDF; `random` module instead
of `secrets` (Python) or `SecureRandom` (Java) for token generation.

A08 Software and Data Integrity Failures — insecure deserialization: `pickle.loads()` or
`pickle.load()` on untrusted input; Java `ObjectInputStream.readObject()` without class
filter (`ObjectInputFilter`); `yaml.load()` without `Loader=yaml.SafeLoader`; unmarshaling
of user-supplied data into privileged objects; auto-update or plugin loading without
cryptographic integrity check; unsigned or unreviewed CI/CD pipeline changes.

A09 Security Logging and Alerting Failures — no logging of authentication events (login,
logout, repeated failed attempts); sensitive data (passwords, tokens, PII, card numbers)
in log entries; missing audit trail for privilege changes or sensitive data access; log
injection (unsanitized user data written to log lines); no alerting or escalation path for
security events; logs not retained or accessible for incident response.

A10 Mishandling of Exceptional Conditions — unvalidated user-controlled URLs passed to
HTTP clients (SSRF — Server-Side Request Forgery); open redirect vulnerabilities (user
controls redirect target without validation); DNS rebinding exposure in calls to internal
services; exception messages exposing internal paths, stack traces, or credentials to
users; silent exception swallowing that masks security events.

## 5§ Additional checks
Apply in addition to OWASP dimensions when relevant to the scope.

Credential exposure (entropy-based) — strings with vendor key prefixes (`sk-ant-`,
`ghp_`, `AKIA`) or high-entropy alphanumeric values in source or config; JWT tokens
(`eyJ...`) as constants; PEM private keys embedded in code; `.env.example` containing
real values instead of placeholders.

Client-side exposure (Web) — secrets or internal paths reflected in HTML/JS output;
sensitive data in `localStorage` or `sessionStorage` without encryption; `innerHTML`
assignments with user-controlled content; `dangerouslySetInnerHTML` without explicit
sanitization; missing Content-Security-Policy headers.

Unsafe reflection — `Class.forName(userInput)` without allowlist; dynamic method
invocation from user-supplied method names; classpath manipulation from user input;
Ruby `constantize` or Python `importlib.import_module` on user-controlled strings.

## 6§ Severity levels
- `critical` — exploitable in production with significant impact (RCE, auth bypass, mass data exfiltration)
- `major` — exploitable with preconditions, or significant data exposure with a realistic attack path
- `minor` — security weakness that reduces defense-in-depth but is not directly exploitable
- `info` — observation or configuration note with no immediate impact

## 7§ Workflow
1. Identify scope — ask if not clear: specific files, directory, or entire codebase.
2. Read all in-scope source files. Also read:
   - Dependency manifests (`package.json`, `requirements.txt`, `pyproject.toml`, etc.)
   - Environment config templates (`.env.example`, `config/`)
   - Route definitions and middleware
   - CI/CD pipeline definitions (`.github/workflows/`, `Jenkinsfile`, `*.yaml` under `.github/`)
3. Apply A01→A10 in order. Record each finding with OWASP category, location, and evidence.
4. Apply §5 additional checks.
5. Group by severity: critical → major → minor → info.
6. Deliver findings. State scope covered, count per severity, and the single highest-priority action.
7. For each critical/major finding: state whether a direct fix can be suggested or manual review is needed.

## 8§ Output contract
Must include:
- Scope statement (files, config, dependencies, and OWASP dimensions covered)
- Findings table: OWASP 2025 dimension | severity | location | description | recommendation
- Summary: count per severity, single highest-priority action

Must not include:
- File modifications
- Findings without a specific location
- `critical` severity for theoretical vulnerabilities with no realistic exploit path
- Duplicate entries for the same vulnerability at different locations (group and list locations)
- False positives for parameterized queries, `safe_load`, or intentional non-sensitive logging
