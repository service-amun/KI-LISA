---
name: security
description: Security rules for source code: credential handling, input validation, injection prevention, supply chain safety, and forbidden patterns. Load before writing auth, API, or data-handling code.
updated: 2026-06-13
---

# Security

## 1§ Scope
Applies when writing source code that handles authentication, user input, external data,
file access, dependencies, or sensitive values. Load before implementing auth flows, API
endpoints, database queries, file operations, or any code that processes user-controlled
data.

## 2§ Rules

### 2.1§ Credential handling
- Never hardcode secrets, API keys, passwords, tokens, or connection strings in source
  files, config templates, test fixtures, comments, or CI/CD environment variables.
- Load credentials from a centralized secrets manager (HashiCorp Vault, AWS Secrets
  Manager, Azure Key Vault, Google Secret Manager) at runtime via API — not from
  environment variables for production credentials.
- `.env` files are local development only; list in `.gitignore`, never commit.
- Implement credential rotation with short TTLs; treat long-lived static credentials as
  security debt. Separate production credentials from dev/test credentials.
- Log files must never contain passwords, tokens, PII, card numbers, or any secret value
  — log IDs and correlation references, not values.
- Apply minimum required permission scope for every credential.

### 2.2§ Input validation and injection prevention
- Validate all user-controlled input against strict allow-lists (not deny-lists) at every
  entry point: request body, query params, headers, file uploads, cookies, and external
  environment variables.
- Never construct SQL queries by string concatenation or interpolation. Use parameterized
  queries or ORMs.
- Never pass user-controlled data to `eval()`, `exec()`, `subprocess`, `os.system()`,
  template engines that evaluate code, or any shell-execution function.
- Encode output for the correct context — each context requires a different function:
  HTML entities for HTML output; `encodeURIComponent()` for URL parameters; context-aware
  JSON encoding for JavaScript context; CSS-specific escaping for CSS. Applying the wrong
  encoding for the context does not prevent injection.
- Sanitize file paths derived from user input: canonicalize and reject paths that escape
  the intended directory (path traversal).
- Disable XML external entity (XXE) processing in all XML parsers — the default in most
  libraries is insecure. Explicitly configure the parser to disable external entities
  before parsing any XML.
- Validate redirect destinations against an explicit allow-list before issuing a redirect.
  Never pass a user-controlled URL directly to a redirect response (open redirect).

### 2.3§ Authentication and authorization
- Verify authentication before processing any sensitive operation or returning sensitive data.
- Verify authorization separately — the authenticated user must have permission for the
  specific resource, not just "any authenticated user" (horizontal privilege escalation).
- Never expose sequential or guessable internal IDs in externally accessible references.
- Session tokens must be cryptographically random (`secrets` in Python, `SecureRandom`
  in Java, `crypto.randomBytes` in Node.js), at least 128 bits, and rotated on privilege
  change.
- Passwords must use a slow key-derivation function: bcrypt (cost factor ≥12), Argon2id,
  or scrypt. Never MD5, SHA-1, or SHA-256 without a KDF. Minimum password length: 15
  characters (NIST SP 800-63-4, 2025 update). Prefer passkeys (FIDO2/WebAuthn) over
  passwords for new systems — they are phishing-resistant and NIST AAL2-compliant.
- Rate-limit all authentication endpoints, password reset flows, and OTP verification.

### 2.4§ Secure defaults
- All external HTTP communication uses HTTPS. Never fall back to HTTP for sensitive
  requests.
- Set security headers on HTTP responses: `Content-Security-Policy`,
  `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`.
- Debug mode, verbose error messages, and stack traces must be disabled in production
  paths.
- Default deny: grant minimum access explicitly rather than granting broadly and
  restricting later.
- Security exceptions must not be silently caught and discarded.

### 2.5§ Dependency and supply chain safety
- Run Software Composition Analysis (SCA) on all dependencies before adding them — both
  direct and transitive. Transitive vulnerability exposure is as real as direct.
- Use lock files (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`) and commit
  them to version control. Never omit lock files from repositories.
- Pin dependency versions in production. Avoid wildcard version ranges (`*`, `^latest`,
  `>=x`).
- Verify software provenance before adding a package: check update frequency, maintainer
  account health, and absence of typosquatting or dependency confusion indicators.
- Maintain a Software Bill of Materials (SBOM) for production systems. Version-control
  it and diff across releases to detect unexpected dependency additions.
- Never execute unreviewed CI/CD build scripts from untrusted pull requests. Audit
  npm/pip/cargo lifecycle hooks in newly added packages before use.

### 2.6§ Forbidden patterns
These patterns are prohibited on untrusted input without exception:
- `eval()`, `Function(string)`, `exec()` with user-controlled input — arbitrary code execution
- `pickle.loads()` / `pickle.load()` on untrusted data — acts as a sandboxed RCE VM
- `yaml.load()` without `Loader=yaml.SafeLoader` (Python) — executes arbitrary Python
- `ObjectInputStream.readObject()` without `ObjectInputFilter` (Java) — gadget-chain RCE
- MD5, SHA-1, or SHA-256 alone as password hash (not a KDF) — brute-forcible
- `random` module (Python) / `Math.random()` (JS) for security-sensitive token generation
- DES, 3DES, RC4, or AES-ECB mode in any cryptographic code
- XML parsers with external entity processing enabled (XXE)
- `verify=False` / `InsecureSkipVerify` in production TLS code

## 3§ Preferred patterns
- Parameterized queries / prepared statements over any form of string-built SQL.
- Vault-based secret retrieval at runtime over environment variables for production secrets.
- Short-lived tokens over long-lived credentials — expire and rotate aggressively.
- Allow-list validation over deny-list for user input — known-good is safer than known-bad.
- Allow-list for redirect destinations — validate against a known set, never open redirect.
- Principle of least privilege: request only the permissions a component actually needs.
- Fail closed: when in doubt about whether to allow an action, deny it and log the attempt.
- Cryptographic agility: design so the algorithm can be swapped without protocol changes
  — required for future post-quantum algorithm migration.

## 4§ Avoid
- Hardcoded credentials in source, config templates, test fixtures, comments, or CI/CD.
- `eval()` or any dynamic code execution with external input.
- MD5, SHA-1, or unsalted/fast hashes for passwords.
- `verify=False` / `InsecureSkipVerify` in production TLS code.
- Catching and silently discarding security exceptions.
- Verbose error messages exposing stack traces, internal paths, or query details to users.
- `yaml.load()` without `SafeLoader` or equivalent safe loader.
- XML parsers without explicit XXE-disabled configuration.
- `random` / `Math.random()` for security-sensitive randomness.
- Open redirects — always validate redirect destinations against an explicit allow-list.
- Wildcard version ranges or missing lock files in production dependency manifests.
