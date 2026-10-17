# ADR 0007 Authentication mail failures and record retention

## Status

Accepted for the local development stack.

## Context

Signup, verification resend, and password recovery save single-use token hashes before sending email. SMTP can fail after the database commit. The initial implementation left failed tokens active, which delayed retries, and repeated SMTP failures used up the email request allowance. Expired tokens and sessions also need periodic removal.

## Decision

On an observed SMTP failure, expire the newly created token. For resend and password recovery, return that failed mail attempt to the Redis allowance. The HTTP response for recovery and resend remains generic. Run `app.auth.cleanup` in a separate Compose service once per day; retry cleanup after five minutes when it fails. Keep expired records for seven days before deletion to allow short-term diagnosis.

## Alternatives considered

- Run cleanup inside each API process: multiple API replicas would duplicate scheduled work.
- Delete tokens immediately on SMTP failure: retaining an expired record helps diagnose the attempted delivery without allowing that link to be used.
- Add a durable mail queue now: this needs a delivery-state model and secure handling of link tokens; it is deferred until deployment requires reliable background delivery.

## Consequences

Local users can request a fresh link after a failed SMTP send. The periodic cleanup container requires database access and another small process. SMTP delivery still occurs during the HTTP request; provider outages, timing differences, and ambiguous failures after provider acceptance remain limitations for a public launch. Rate limits at a trusted ingress and a durable delivery path should be evaluated before exposing authentication publicly.

## Verification

Python compilation, a mocked SMTP helper smoke test, and Compose configuration validation cover the current change. End-to-end signup, resend, and password recovery should be tested against the configured SMTP provider after the containers are rebuilt.
