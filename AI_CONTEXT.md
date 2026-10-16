# CodeFlowAtlas Context for Humans and Coding Assistants

## What this project is

CodeFlowAtlas is a visual code-flow learning and diagnosis tool for students and AI-assisted builders, including people who describe themselves as vibe coders. Its primary workflow is **GitHub or Bitbucket URL → pinned revision → selected API or feature → interactive source-linked graph or mind map → inspect a step and ask the AI guide → optional synthetic isolated target and AI-proposed test journey → measured issue and improvement experiment**. The graph is a main product surface, not a decorative overview: it links each supported node and edge to source and evidence. A pasted link enables supported source analysis and grounded source-only explanations. Timings, bottlenecks, and load results require a supported application running in an approved isolated environment with disposable synthetic data. The 100-user system design lab is a deeper feature, not a prerequisite for understanding code.

The complete product vision and technical requirements are in `docs/project-specification.md`. The implementation approach is in `docs/developer-guide.md`, and the user-facing feature order is in `docs/delivery/functionality-and-implementation-flow.md`. Read these before planning substantial work. The current repository includes a Next.js frontend, FastAPI backend, PostgreSQL, Docker Compose, and a standalone FastAPI analyzer/IR prototype for a fixture; repository import, connected graph UI, AI, and runtime experiments remain planned. This context file is a quick handoff, not a replacement for the specification or running code.

## Why it exists

Students and AI-assisted builders may have a working project without understanding how its pieces connect. CodeFlowAtlas should answer: Which endpoint starts this feature? Which functions are called? Where is data read, changed, and returned? What could fail? The AI guide explains each step in plain language with file and line references, and labels inferred or unresolved calls. If the project can be run safely with instrumentation, the guide can add real timings and errors, explain a measured issue, and suggest a change to test. A recommendation about caching, indexing, query shape, concurrency, or connection pooling must identify the evidence, the tradeoff, and a way to compare before and after. Do not infer execution time from source code or assume that a cache is the right fix.

## Non-negotiable product rules

1. Static analysis of imported repositories must not execute their code.
2. Python/FastAPI is the first deep analyzer. The next full-stack source path joins a React or Next.js frontend action to a FastAPI route; Express is the next separate backend family. Other frameworks and languages must earn support through fixtures and explicit capability claims. See `docs/analysis/framework-support-roadmap.md`.
3. The versioned, language-neutral IR separates analyzers from the graph UI and runtime features.
4. Static relationships, runtime observations, and AI hypotheses are different evidence classes. Never merge them into one unqualified claim.
5. Imported text, archives, URLs, and documentation are untrusted. Enforce project isolation, bounded processing, secret controls, and prompt/data separation.
6. Bot journeys, traffic, and fault experiments run only against approved isolated targets with limits, cleanup, and recorded configuration. Runtime targets use disposable databases and synthetic records, never the imported application's original or production data.
7. Findings and AI responses cite inspectable evidence IDs. Timings come from telemetry, not an LLM.
8. Prefer a complete reproducible FastAPI workflow over adding infrastructure or language breadth without user value.
9. A pasted repository URL provides source analysis only. Runtime, database timings, and 100-user results require a supported instrumented target in an approved isolated environment.
10. Recommendations about caching or other changes are hypotheses until a comparable rerun measures their effect. Store configured and achieved load separately.
11. The AI guide must be useful with source evidence alone. It cites files and lines, explains uncertainty, and never invents runtime behavior when no trace exists.
12. Visualizations must distinguish source-inferred paths, observed runtime paths, and AI hypotheses. Every shown relationship needs provenance or a visible unknown state; large graphs need bounded slices and a text alternative.
13. AI may propose a journey or synthetic schema/seed plan, but the runner executes only a reviewed finite scenario; schema and data proposals must validate against the target before any measured claim.
14. A local test lab requires a user-installed runner; a browser alone cannot launch containers on a learner's machine. Hosted execution is a later design.
15. Report framework support by achieved level: detected, catalogued, source flow, observed flow, or test lab. A source link across frontend and backend requires a resolvable HTTP contract and source evidence on both sides; unresolved calls stay visible.
16. The planned visual workspace spans repository overview, feature flow, and function calls. Natural-language answers pair relevant source excerpts with evidence-backed graph slices; live suggestions are editable questions, and diagram exports retain revision and uncertainty.
17. Optional LLM prompt drafts are user-triggered, inspectable, and limited to authorized, secret-filtered evidence. Generated prompts and answers do not establish facts without cited source or runtime evidence.

## Initial architecture

- Next.js frontend and FastAPI API/BFF.
- Modular backend domains for repository import, analysis, graph, tracing, experiments, findings, and AI.
- PostgreSQL for durable product records; Redis for justified short-lived state.
- Background workers for analysis and isolated experiments.
- OpenTelemetry for target traces; dedicated telemetry storage for high-volume raw data.
- k6 for repeatable traffic scenarios.
- Kafka, vector search, cloud deployment, and service decomposition are extensions when justified by a concrete need.

## First complete demonstration

Submit a supported public GitHub or Bitbucket URL for a small FastAPI fixture and pin its revision. Select `POST /checkout`; show an interactive graph and mind-map view of its handler, downstream functions, and detectable database access, with clickable source links and confidence. Ask the AI guide to explain a selected node and an unresolved edge using only inspected source. Then create a disposable database from validated fixture models or migrations, generate synthetic records, and run the approved isolated target. Review and execute one AI-proposed student journey; add a trace waterfall and query timings linked to the same flow, explain one measured issue, and test a proposed improvement. A later bounded 100-user run and dependency fault add charts and comparisons. Retain the source revision, dataset version, scenario, evidence, and configuration so another developer can repeat each supported step.

## What to inspect before changing code

Read the specification, current README, repository layout, IR schema, analyzer fixtures, migrations, API contracts, security policy, CI, and architecture decision records. Check what is implemented versus planned. If a proposed change affects untrusted code execution, network access, data retention, or cross-project access, document the trust boundary and tests.

## Useful implementation order

Foundation → safe import and static analysis → API and feature flow with grounded AI explanation → controlled runtime tracing → repeatable experiments and findings → justified extensions.

## Definition of a trustworthy feature

A capability is complete when it has a visible user outcome, stored provenance, explicit limits, deterministic or reproducible tests, safe failure behavior, and documentation that matches what the software actually does. Unsupported cases should be shown as unsupported or uncertain instead of guessed.
