---
name: error-handling
description: Error handling rules: no silent catches, fail-fast, retry transient failures with backoff, circuit breakers, structured observability context. Load when writing error handling or retry logic.
updated: 2026-06-13
---

# Error Handling

## 1§ Scope
Applies when writing code that contains exception handling, error propagation, async
error flows, retry logic, circuit breakers, or resource cleanup. Load before implementing
`try/catch` blocks, promise rejection handlers, retry mechanisms, or resource-acquiring
operations.

## 2§ Rules

### 2.1§ Catch specificity
- Catch specific exception types, not base `Exception`, `Error`, or `Throwable` unless
  the handler genuinely applies to all subtypes.
- Never use an empty catch block — `catch {}`, `except: pass`, `catch (e) {}`. Every
  catch must either recover, log, or re-throw.
- If the exception type cannot be narrowed (e.g., third-party boundary code), log the
  full exception including type and message, then decide explicitly to recover or re-throw.

### 2.2§ Fail-fast for programmer errors
- Do not catch and recover from errors that indicate a programming mistake: null
  dereferences, type errors, assertion failures, out-of-bounds access, or invalid state
  invariants.
- A crash with a clear message is better than silent corruption propagating through the
  system. Use assertions or explicit `throw`/`panic` for invariant violations.

### 2.3§ Transient failure handling
- Retry only on genuinely transient failures: network timeouts, HTTP 408, HTTP 429
  (rate limit), HTTP 503 (temporary unavailability), database connection drops.
- Never retry: HTTP 4xx (except 408/429), authentication failures (401/403), or errors
  caused by programmer mistakes — these are deterministic and will not resolve on retry.
- Exponential backoff formula: `delay = min(base × 2^attempt ± jitter, MAX_BACKOFF)`.
  Recommended values: base=100ms, jitter=±50% random variation, MAX_BACKOFF=32s. Jitter
  is mandatory — without it, concurrent retries synchronize and cause a thundering herd.
- Cap both retry count and total retry duration. Always propagate the final failure after
  exhausting retries — never silently succeed with a degraded result.
- Non-idempotent operations (writes, payments, state mutations) require an idempotency
  token with every retry so the server can detect and deduplicate duplicate requests.
- Check the `Retry-After` response header on HTTP 429 and honor its value before retrying.
- Implement circuit breakers for systemic failure: when error rate exceeds a threshold
  (e.g., >50% failures in 60 seconds), open the circuit and stop sending requests. Use a
  half-open probe to detect recovery. This prevents cascading failures.
- Apply retry budgets in high-traffic systems: cap retries to a fixed percentage of total
  traffic (e.g., max 10%) to prevent retry storms from overwhelming a degraded service.

### 2.4§ Error messages and observability context
- Include context in every error message: what operation was attempted, on what entity or
  resource, and what constraint was violated.
- Bad: `"Database error"`. Good: `"Failed to insert user: duplicate email 'x@y.com'"`.
- Error messages in logs are for operators — include technical detail.
- Error messages shown to users are for users — no stack traces, internal paths, query
  details, or credential fragments. Map technical errors to user-facing messages at the
  boundary.
- All logged errors must carry structured fields: `error_code`, `message`, `trace_id`,
  `span_id`, `timestamp`, `service`, and `operation`. Use structured JSON logging, not
  plain-text string interpolation.
- Include a trace ID or correlation ID in both log entries and user-facing errors so
  operators can navigate from a user-reported incident to the corresponding log line.
- Never log sensitive data: passwords, tokens, PII, card numbers, API keys.

### 2.5§ Async and promise errors
- Every Promise chain must have a `.catch()` handler or be awaited inside a try-catch.
  Unhandled promise rejections are programming errors and must not be silently swallowed.
- For concurrent async operations where individual failures should not abort the rest,
  use `Promise.allSettled()` instead of `Promise.all()`. `Promise.all` rejects on the
  first failure; `allSettled` waits for all and returns individual results with status.
- In Python: use `asyncio.gather(..., return_exceptions=True)` for the same isolation.
- Do not fire-and-forget unless the operation is genuinely independent and its failure
  is acceptable — document this explicitly when done intentionally.
- Always `await` Promises before the function returns.

### 2.6§ Resource cleanup
- Guarantee resource cleanup even when errors occur. Use language-idiomatic mechanisms:
  `finally` blocks (JS/Java/Python), `defer` statements (Go), `async with` context
  managers (Python async), RAII destructors (Rust/C++), `using` statements (C#).
- Never leave file handles, database connections, network sockets, or locks open on the
  error path. Resource leaks are invisible until they cause system degradation under load.
- Do not suppress errors inside cleanup code (`finally`, `defer`, destructors) — a
  cleanup error that swallows the original exception makes the root cause unreachable.

## 3§ Preferred patterns
- Re-throw enriched errors: catch, add context, re-throw — preserves the original stack
  trace while adding context at each layer. Language idioms:
  - JS/TS: `throw new Error("context", { cause: e })`
  - Go: `fmt.Errorf("context: %w", err)` — the `%w` verb enables `errors.Is`/`errors.As`
    chain inspection; use `errors.Is(err, target)` or `errors.As(err, &typed)`
  - Python: `raise DomainError("context") from original_error`
  - Rust: `?` operator for propagation; `thiserror` for library error types, `anyhow`
    for application-level aggregation where preserving the full error chain matters
- Structured error types (enums, discriminated unions, sealed classes) over raw strings —
  callers can match on error category without fragile string parsing.
- Result types (`Result<T, E>`, `Either`, `Option`) for expected failure paths — the
  error case is explicit in the function signature, not invisible.
- Circuit breaker over naked retry loop — prevents runaway retries on dead services.
- Structured JSON at every error site: `{ "level": "error", "error_code": "...",
  "trace_id": "...", "span_id": "...", "operation": "...", "message": "..." }`.
- Centralized error mapping at service boundaries: one place translates domain exceptions
  to HTTP status codes or API payloads, keeping business logic free of transport concerns.

## 4§ Avoid
- Empty catch blocks in any language.
- Catching `Exception` / `Error` / `Throwable` and continuing as if nothing happened.
- Retrying on non-transient errors (4xx except 408/429).
- Fixed-interval retries without backoff — causes thundering herds under load.
- Retries without jitter — synchronized retries overwhelm recovering services.
- Retrying non-idempotent operations without an idempotency token.
- Ignoring retry budgets — unbounded retries amplify failures into cascading outages.
- `console.error(e)` as the only error handling — log then recover, propagate, or terminate.
- Plain-text error logging without structured fields or trace context.
- Swallowing errors in cleanup code that masks the original failure.
- Fire-and-forget async operations without documenting that failure is acceptable.
- Leaking file handles, connections, or locks on the error path.
