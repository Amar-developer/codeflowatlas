# ADR 0005 Synthetic runtime and reviewed AI test bot

## Status

Accepted product direction; implementation planned.

## Context

CodeFlowAtlas must help students understand a repository even when its original database is unavailable. The product also aims to measure real API and SQL behavior and let an AI bot propose student-like tests. A source repository does not include its production data or guarantee that it can run from a link. Letting AI execute arbitrary actions or connect to original systems would make results unsafe and hard to reproduce.

## Decision

Source analysis is the default and never executes imported code. Runtime capability is a separate opt-in path for supported targets. Each target run gets an isolated application copy, a new disposable database, and synthetic records. Build the schema from validated target migrations, models, or test fixtures; AI may propose missing schema adapters and seed values, but proposals must pass target startup, readiness, and contract checks before any test claims are made. If validation fails, preserve the source walkthrough and report runtime setup as unsupported. Never request or use the imported application's original or production database, credentials, dump, or customer records.

The AI bot proposes a finite test journey from the selected revision's discovered endpoints, schemas, and fixtures. A learner reviews target identity, actions, expected outcomes, synthetic data, network destinations, request and time limits, and state-changing steps once. A deterministic runner freezes and revalidates that plan, executes it only on the approved disposable target, and records request, assertion, trace, dataset, and revision IDs. AI explanations cite those records and keep suspected causes separate from observed failures. A local lab requires a user-installed runner; hosted execution is a later design.

## Alternatives considered

- Connect to a user's existing database: rejected because it may contain private or production data and would make destructive tests unacceptable.
- Let AI infer and execute any schema or journey without validation: rejected because source does not prove business data or runtime behavior.
- Require every repository to run before offering value: rejected because source-linked walkthroughs must work without runtime setup.
- Run tests against an arbitrary pasted live URL: rejected because target ownership, side effects, and load limits cannot be established from a URL alone.

## Consequences

The first runtime target is the bundled FastAPI fixture, followed by explicitly supported project shapes. Some repositories remain source-only. The system needs dataset versioning, teardown, target allowlists, deterministic runners, and UI states for unsupported setup. Measurements apply to the synthetic dataset and recorded environment; they are not predictions for an original production system. Hosted execution adds a separate cost and isolation decision later.

## Verification

Fixture tests must prove that a fresh target can be created from validated schema and deterministic synthetic seed, then torn down. Security tests must reject original database credentials, unapproved targets/actions, external side effects, and attempts to widen a saved scenario. A bot journey must be replayable with its revision, dataset version, action list, assertions, requests, and trace IDs. Source-only analysis must still succeed when runtime setup fails.
