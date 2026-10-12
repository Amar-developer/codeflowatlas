# CodeFlowAtlas Context for Humans and Coding Assistants

## What this project is

CodeFlowAtlas is a developer engineering laboratory. It helps a user understand an unfamiliar repository by connecting static source analysis to observed request traces, controlled traffic and fault experiments, evidence-backed bottleneck findings, and grounded AI explanations. Its central flow is **repository → analysis → API and code graph → trace → load or failure → finding → explanation**.

The complete product vision and technical requirements are in `docs/project-specification.md`. The implementation approach is in `docs/developer-guide.md`. Read both before planning substantial work. The current repository includes a Next.js frontend, FastAPI backend, PostgreSQL, and a Docker Compose stack; analysis and experiment capabilities remain planned. This context file is a quick handoff, not a replacement for the specification or running code.

## Why it exists

Source code, traces, and load metrics each show only part of an application's behavior. CodeFlowAtlas joins them so a developer can answer which endpoint starts a path, which code and dependencies it may reach, what actually ran, and what changed under stress or a controlled failure.

## Non-negotiable product rules

1. Static analysis of imported repositories must not execute their code.
2. Python/FastAPI is the first deep analyzer. Other frameworks and languages must earn support through fixtures and explicit capability claims.
3. The versioned, language-neutral IR separates analyzers from the graph UI and runtime features.
4. Static relationships, runtime observations, and AI hypotheses are different evidence classes. Never merge them into one unqualified claim.
5. Imported text, archives, URLs, and documentation are untrusted. Enforce project isolation, bounded processing, secret controls, and prompt/data separation.
6. Traffic and fault experiments run only against approved isolated targets with limits, cleanup, and recorded configuration.
7. Findings and AI responses cite inspectable evidence IDs. Timings come from telemetry, not an LLM.
8. Prefer a complete reproducible FastAPI workflow over adding infrastructure or language breadth without user value.

## Initial architecture

- Next.js frontend and FastAPI API/BFF.
- Modular backend domains for repository import, analysis, graph, tracing, experiments, findings, and AI.
- PostgreSQL for durable product records; Redis for justified short-lived state.
- Background workers for analysis and isolated experiments.
- OpenTelemetry for target traces; dedicated telemetry storage for high-volume raw data.
- k6 for repeatable traffic scenarios.
- Kafka, vector search, cloud deployment, and service decomposition are extensions when justified by a concrete need.

## First complete demonstration

Import a supported FastAPI fixture at a pinned revision. Discover `POST /checkout`, show its handler and downstream graph with confidence, run the isolated instrumented target, display a trace, compare baseline and stress runs, inject one bounded dependency delay, generate a bottleneck finding from measured spans and metrics, and explain it with cited evidence. Retain the configuration so the experiment can be repeated.

## What to inspect before changing code

Read the specification, current README, repository layout, IR schema, analyzer fixtures, migrations, API contracts, security policy, CI, and architecture decision records. Check what is implemented versus planned. If a proposed change affects untrusted code execution, network access, data retention, or cross-project access, document the trust boundary and tests.

## Useful implementation order

Foundation → safe import and static analysis → API catalog and graph → controlled runtime tracing → repeatable experiments and findings → grounded AI → justified extensions.

## Definition of a trustworthy feature

A capability is complete when it has a visible user outcome, stored provenance, explicit limits, deterministic or reproducible tests, safe failure behavior, and documentation that matches what the software actually does. Unsupported cases should be shown as unsupported or uncertain instead of guessed.
