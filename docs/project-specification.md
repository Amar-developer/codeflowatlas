# CodeFlowAtlas Project Specification

## Purpose and reader guide

CodeFlowAtlas helps students and AI-assisted builders understand and improve small real applications through interactive visualizations. A supported GitHub or Bitbucket link leads to a source-linked flow graph or mind map and an AI guide that explains selected steps; an approved isolated runtime can add trace waterfalls, request and database timings, measured issues, and testable optimization options. Bounded load and fault experiments add charts in a deeper learning mode. This specification defines the product vision, complete system concept, delivery boundaries, architecture, data contracts, safety controls, and acceptance criteria. It is written so a developer, reviewer, or coding assistant can understand the intended product without relying on prior conversation.

The central workflow is: **repository link → pinned source → select an API or feature → explore its flow graph and mind map → inspect code and ask the AI guide → optionally view trace and timing visualizations → investigate an issue → test an improvement**. A useful implementation must make each transition inspectable and reproducible. The interface should never imply that a statically inferred call was observed at runtime, or that an AI hypothesis is a measured fact.

## 1 Product vision

### Problem

Students and AI-assisted builders can produce working small applications without understanding how a feature moves through routes, functions, data access, and responses. When something breaks or slows down, they may not know where to start. A repository link does not explain the code flow, and a generic AI answer can guess about source or runtime behavior it has not inspected.

### Vision

CodeFlowAtlas lets a learner submit a supported GitHub or Bitbucket URL, select an API or feature, and explore a source-linked flow graph or mind map of its handler, functions, dependencies, database access, and response. An integrated AI guide explains selected nodes and edges in plain language, answers questions, cites inspected source, and identifies unresolved relationships. This source-only visual path is useful even when the repository has no runnable database. When a supported application runs in an approved isolated environment, the same workspace adds an observed trace waterfall, timings, and errors; the AI guide can explain a measured issue and a testable fix. A separate controlled lab uses charts to show what happens under bounded concurrent traffic or a dependency fault.

### Target users and value

The primary users are students and AI-assisted builders, including vibe coders, working on small real Python applications. They need to move from “AI wrote this, but I do not understand the flow” to a verifiable explanation of one feature and a place to ask follow-up questions. When a supported runtime exists, they can also diagnose an error or slowdown and test a change. Educators, onboarding teams, and developers reviewing unfamiliar code are secondary users.

### Product principles

- **Evidence before explanation.** Source locations, analyzer output, traces, metrics, and experiment results are first-class records.
- **Learning through evidence.** Explain a concept using an inspected code path or measured experiment, then show the relevant tradeoff and a next check.
- **Useful without a running target.** Source-linked feature flows and grounded AI explanations must work before runtime instrumentation or load testing exists.
- **Graph-first learning.** Interactive flow graphs and mind maps are primary navigation; each node and edge opens evidence, with inferred paths visually separate from observed spans and AI hypotheses.
- **One reproducible path first.** A complete FastAPI demonstration is more valuable than superficial support for many frameworks.
- **Uncertainty is visible.** Static relationships carry confidence and provenance; missing telemetry remains missing.
- **Safety is part of the workflow.** Repository inspection does not execute imported code. Runtime tests use isolated targets and explicit authorization.
- **Language independence at the data boundary.** Python is the first deep analyzer; the shared intermediate representation supports later analyzers.

## 2 Product scope

### Core product capabilities

1. Create projects and import a supported public GitHub or Bitbucket repository URL at a pinned Git revision, or a validated archive, into an isolated workspace. Private access requires separate authorization controls.
2. Analyze Python source without importing or executing it. Discover symbols, imports, resolvable calls, framework routes, and selected infrastructure usage.
3. Normalize findings into a versioned, language-neutral intermediate representation (IR), then persist an API catalog and code graph.
4. Let a learner select an API or feature and navigate an interactive flow graph and mind map of its route, handler, functions, dependency calls, detectable database access, and response, with file and line references, confidence, and provenance.
5. Provide an integrated AI guide for source-only explanations and follow-up questions. It cites inspected files and lines, distinguishes exact from inferred relationships, and works without a runnable database.
6. Collect OpenTelemetry traces from a supported instrumented application. Show endpoint duration, errors, sanitized database query counts and timings, and source links when mapping evidence exists.
7. Explain observed issues with cited runtime evidence and turn findings into testable optimization options, including query, index, cache, connection-pool, and concurrency changes where relevant.
8. Offer optional repeatable, bounded traffic and edge-case scenarios against an allowlisted isolated target, including a configurable 100-concurrent-virtual-user learning scenario. Record configuration, achieved load, timings, errors, and resource metrics.
9. Inject at least one controlled dependency failure or delay, compare behavior, and generate rule-based bottleneck findings with evidence.
10. Retain revisions and experiment runs so users can compare and reproduce results.

### Explicit boundaries

The first implementation proves the path on a FastAPI fixture before accepting external repository URLs. The intended complete workflow supports public GitHub and Bitbucket links for supported Python/FastAPI repositories. Importing source does not guarantee that an arbitrary application can be executed or instrumented. Runtime tracing and load tests require approved isolated targets with resource, duration, and destination limits. Flask and Django route discovery can follow as separate analyzers. JavaScript/TypeScript, Java, and Go are future analyzers using the same IR contract. Production deployment, large-scale distributed processing, automatic architecture classification, and broad fault injection are extensions. Imported applications are never run on the host during analysis. CodeFlowAtlas does not autonomously modify a user's repository, expose raw database values or secrets, or claim that an LLM can prove runtime behavior.

## 3 User journeys

### Repository understanding

The learner creates a project, submits a supported GitHub or Bitbucket URL, pins a revision, and starts analysis. The UI shows progress, detected language and framework, warnings, discovered endpoints, and the graph. Selecting `POST /checkout` reveals its handler, source location, request and response models when resolvable, authentication indicators, downstream calls, detectable database reads or writes, and confidence for each relationship. The learner can ask the AI guide why a function is called or where a value comes from. Answers link to inspected source lines and say when the path is inferred or unresolved. This experience works without a running target; source analysis does not prove that a call executed.

### Runtime diagnosis

The user launches a supported target in isolation with tracing, sends a request, and opens the waterfall. The trace contains total request timing, status, errors, parent-child relationships, and sanitized database query spans with counts and durations where instrumentation supports them. Source mapping is shown only when instrumentation or reliable metadata identifies a file, function, or entity. The user can compare trace evidence with the static graph and see where they differ. Raw row values and sensitive query parameters are not displayed.

### Controlled experiment

The user selects an isolated target, records a baseline, then runs a bounded profile such as 100 concurrent virtual users sending real HTTP requests against one API. The lab records achieved traffic, p50/p95/p99 latency, throughput, errors, timeouts, database timing, and resource pressure from that run. A supported dependency delay or failure can be injected in a separate approved run. CodeFlowAtlas retains the scenario definition, target revision, environment label, metrics, traces, and findings so the developer can identify what slowed or failed and repeat the same conditions after a change.

### Evidence-grounded explanation

The user asks why the endpoint slowed down or failed. The assistant retrieves the relevant endpoint, code nodes, database and request spans, metrics, and findings. Its response separates observed facts, likely explanations, unknowns, and suggested next checks. It may compare query optimization, indexing, caching with invalidation, connection-pool tuning, or moving work to a queue when the evidence makes those options relevant. Each factual claim points to a source, span, metric series, or finding ID, and the developer can rerun the saved scenario to test a change.

## 4 System architecture

The starting architecture is a modular FastAPI application with clear repository, analysis, graph, trace, experiment, finding, and AI modules; a Next.js frontend; and one or more background workers for expensive or isolated jobs. PostgreSQL is the durable application store. Redis may hold short-lived job state, rate limits, and WebSocket fan-out. A trace backend stores high-volume raw telemetry; PostgreSQL stores searchable trace summaries and links. Object storage is appropriate for repository archives and large artifacts when local storage is insufficient.

The frontend communicates through a stable API/BFF boundary. Analysis, traffic, and AI work can move to independently scaled workers without changing the product contract. Kafka is a later event transport when durable high-volume streams, independent consumers, or replay justify its cost. A local queue and transactional job records are adequate for the initial workflow. The system should document any transition to Kafka, including idempotency, retry, dead-letter handling, ordering assumptions, and outbox or equivalent publication guarantees.

### Logical flow

```text
Next.js UI → FastAPI API/BFF → PostgreSQL
                         → analysis worker → IR and graph
                         → trace ingestion → trace backend
                         → traffic/failure worker → isolated target
                         → findings engine → AI explanation service
```

OpenTelemetry collects traces, Prometheus-compatible metrics describe platform and experiment health, and structured logs connect jobs to project, revision, and trace IDs. WebSocket or server-sent updates report job progress; polling remains a fallback.

## 5 Repository import and analysis

An import creates a repository revision record containing source type, canonical URL or archive identity, commit SHA or content fingerprint, import status, and workspace path. The intended link flow accepts supported public GitHub and Bitbucket Git repositories and reads the repository tree at the pinned revision, within explicit file, byte, depth, and time limits. The importer validates archive entries, symlinks, path traversal, and remote URL policy before writing files. Analysis reads source files as data. It does not invoke package installers, import target modules, execute setup scripts, or run target tests. Unsupported files and skipped paths are visible so “full repository analysis” is not claimed when limits or language coverage exclude content.

The analyzer pipeline is: file scan → language and framework detection → parser → symbol extraction → route discovery → import and call resolution → infrastructure indicators → IR validation → graph persistence → findings and warnings. Python's `ast` module is the first parser. Resolution should distinguish exact references from likely or unresolved dynamic calls. Decorators, dependency injection, dynamic imports, reflection, and framework registration require explicit confidence and limitations.

FastAPI analysis covers route decorators, `APIRouter` inclusion and prefixes, HTTP methods and paths, handler symbols, dependency declarations, and request/response models when statically resolvable. Flask and Django analyzers have separate fixture suites and should not be described as deeply supported until those suites pass.

### Analyzer outputs

Every analysis run records repository revision, analyzer and schema versions, start and completion states, warnings, counts, and reproducible inputs. Output includes files, entities, edges, endpoints, source locations, confidence, and findings. The UI must show incomplete analysis and parse failures rather than silently omitting unsupported code.

## 6 Common intermediate representation

The IR is the contract between language analyzers and the rest of CodeFlowAtlas. Each entity has a stable ID scoped to a repository revision, type, display name, qualified name where available, source location, analyzer version, and properties. Suggested types are Repository, File, Module, Class, Function, APIEndpoint, Database, Table, Cache, Queue, Topic, ExternalService, Middleware, Worker, and Test.

Each directed edge has source and target IDs, relationship type, source location, confidence (`exact`, `high`, `medium`, `low`), provenance, and analyzer version. Suggested relationships are CONTAINS, IMPORTS, CALLS, EXPOSES, READS_FROM, WRITES_TO, PUBLISHES, CONSUMES, DEPENDS_ON, MIDDLEWARE_BEFORE, and TRIGGERS. An edge may be unknown or unresolved; it must not be invented to make a diagram look complete.

For example, `GET /orders → OrderRouter.get_orders → OrderService.list_orders → OrderRepository.find → PostgreSQL` represents an analysis path. Runtime traces may confirm only some steps. Keep static edges and observed span links distinct so the interface can compare them.

The IR schema must be versioned. Graph IDs should remain stable across repeat analysis of the same revision and analyzer version. Adding a language analyzer should require a parser and mapper to the IR, plus fixtures, without changes to generic graph visualization or experiment storage.

## 7 API catalog and application interfaces

The endpoint record includes HTTP method, normalized path, handler entity, file and line, framework, auth indicators, request and response schema references, downstream graph links, confidence, and analysis warnings. The detail view can attach recent traces, latency and error summaries, and relevant scenarios when those records exist.

Representative product APIs include project and repository creation, starting and checking analysis, listing endpoints and graph slices, querying traces and findings, creating traffic and failure runs, and asking a grounded AI question. All collection APIs use pagination and project scoping. Mutating APIs validate roles and return consistent errors. Long-running operations return a job or run ID immediately, with progress events and a polling endpoint.

## 8 Runtime tracing and visualization

The supported target application exports OpenTelemetry spans for inbound HTTP requests and instrumented downstream operations such as database, Redis, messaging, and external HTTP. A span contains trace ID, span ID, parent span ID, service and operation names, timestamps, duration, status, error details, and selected sanitized attributes. Trace collection is the source of truth for observed timings.

The trace explorer presents a request timeline, waterfall, error markers, service map, database query count and duration, and links to code where mapping is supported. It can show the route from endpoint to a database operation and response only to the extent the static and runtime evidence supports each connection. An auto-instrumented database span may identify a query and service without an exact source line; the UI must say so. Span retention and sampling are explicit. Avoid storing secrets, personal data, raw row values, full request bodies, or unbounded SQL parameters in span attributes.

## 9 Traffic, edge cases, and failure experiments

Scenarios define an allowlisted target endpoint, method, payload, virtual users or arrival rate, duration, ramp-up, headers and authentication strategy, success criteria, and environment label. Profiles include smoke, baseline, stress, spike, and soak, but the initial complete workflow needs only a repeatable baseline and one bounded stress profile. A 100-concurrent-virtual-user profile is the reference learning example; it is a configured test level, not a promise that the target served 100 simultaneous successful requests. k6 is the planned traffic engine. Runs store the exact configuration, achieved traffic, target revision, tool version, aggregate metrics, and artifact links.

Metrics include requests per second, throughput, p50/p95/p99 latency, errors, timeouts, CPU and memory, and relevant dependency indicators such as database connections, cache hit ratio, or queue lag. Measurements are meaningful only when the target environment and its resource limits are recorded. CodeFlowAtlas should not promise that an arbitrary target can sustain a specified request rate.

The edge-case engine starts with deterministic inputs derived from resolvable schemas: missing required fields, invalid enum values, nulls, malformed IDs, boundary values, duplicate requests, pagination extremes, wrong content type, and expired tokens when a safe test credential exists. Every case stores expected outcome, actual outcome, trace ID, and verdict.

Failure injection is opt-in and restricted to isolated test targets. The first supported fault can be dependency latency or an HTTP dependency error. Later faults may include database or Redis unavailability, message delay or duplication, connection-pool pressure, and resource pressure. Each run requires a bounded duration, cleanup, environment label, and audit record. The UI must not inject faults into arbitrary external systems.

## 10 Findings and AI assistant

The findings engine is deterministic before any AI interpretation. Initial rules include dominant cumulative or exclusive span duration, repeated or slow database calls, high error concentration, and p99 growth under load. Later rules can cover queue lag, pool saturation, cache misses, and retry amplification. A finding contains rule ID and version, severity, evidence IDs, sample size, comparison window, measured values, uncertainty, and a plain-language conclusion. A finding such as “database spans represented 78% of measured request duration across 1,000 traces” is valid only when those records exist. Optimization options follow findings and remain hypotheses until a comparable rerun measures the effect.

The AI guide accepts a constrained evidence bundle. Its first mode uses repository metadata, selected source snippets, IR paths, endpoint details, and analysis warnings to explain a selected feature and answer learner questions without any runtime setup. It cites inspected file and line references, labels inferred or unresolved calls, and does not claim a function ran merely because a static edge exists. When traces, metrics, and findings are available, the guide can also explain an observed bottleneck, likely causes, test ideas, and architecture tradeoffs. It labels observations, inferences, and unknowns separately.

Retrieval can index README files, architecture documentation, selected source ranges, endpoint descriptions, and findings using metadata including project ID, revision SHA, path, line range, entity ID, and document type. Secret scanning and access checks run before indexing and retrieval. Embeddings and a vector store are optional until keyword or structured retrieval proves insufficient.

## 11 Data and event design

Core relational records are users, projects, repositories, revisions, analysis runs, files, code entities and edges, API endpoints, findings, trace sessions and summaries, experiment scenarios and runs, architecture models, AI conversations, and knowledge chunks. Index by project and revision, endpoint method/path, trace ID, timestamp, and finding severity as needed. Raw high-volume spans and traffic samples can live in dedicated telemetry storage with stable references from PostgreSQL.

If the architecture adopts Kafka, candidate events include analysis requested/progress/completed, trace received, traffic started/completed, failure started, finding created, and AI requested/completed. Every event needs an ID, schema version, project and revision context where applicable, correlation ID, and idempotent consumer behavior. The database remains the system of record; Redis does not become the source of truth.

## 12 Frontend experience

The primary screens are project dashboard, repository link import, analysis progress, API or feature selector, interactive flow graph and mind map, source viewer, and grounded AI question panel. The first useful interface works with source evidence alone. Later screens add a trace waterfall and database timing explorer, issue explanation, optional 100-user traffic and failure charts, findings, optimization options, run comparison, and project settings. The [visualization system](frontend/visualization-system.md) defines evidence styling, node interactions, and graph limits. React Flow can render focused graph slices; charts should expose units, sample sizes, and comparison conditions.

The interface should lead a learner from a repository to a selected feature's visual code and data path, then to source evidence and AI questions for a selected node or edge. A supported runtime can extend the same workspace with an observed trace waterfall, real timings, a measured issue, and a testable improvement; the optional lab adds controlled load and fault charts. Empty states explain when a capability requires instrumentation or an isolated target. Error states name the failed step and preserve partial results when safe.

## 13 Security and trust boundaries

Treat imported repositories, archives, commit metadata, documentation, HTTP responses, and retrieved text as untrusted input. Main threats are path traversal, archive bombs, unsafe code execution, SSRF, credential leakage, prompt injection, dependency compromise, and cross-project data exposure.

Controls include archive validation, bounded scanning, non-root isolated workers, read-only source mounts where possible, CPU/memory/time limits, egress restrictions, outbound allowlists, authentication, project-level authorization, audit logs, secret scanning, and separation of data from AI instructions. Runtime target execution occurs only in a container or equivalent sandbox with explicit resource and network policy. Traffic and faults require environment labels and target allowlists. The assistant never executes commands suggested by repository content.

## 14 Quality and verification

Unit tests cover parsers, route detectors, IR validation, graph building, finding rules, and request schemas. Fixture repositories have known endpoint and edge expectations, including unresolved or dynamic behavior. Integration tests cover PostgreSQL, job processing, trace ingestion, and any Redis or Kafka integration actually used. Contract tests protect API and event schemas. End-to-end tests follow repository import through API discovery and graph display, then the controlled trace and experiment path. Security tests cover path traversal, archive limits, URL policy, authorization, secret handling, and unsafe execution. CI runs linting, tests, builds, and dependency or container checks appropriate to the implementation.

The platform itself records analysis duration, files analyzed, failures, queue depth, worker use, trace ingestion, traffic errors, latency, and AI cost or latency where available. Operational dashboards should distinguish platform failures from target-application failures.

## 15 Delivery sequence by dependency

1. **Foundation:** repository structure, project model, PostgreSQL migrations, API conventions, local containers, authentication, and CI.
2. **Static understanding:** safe import, Python scanner, AST extraction, versioned IR, FastAPI route discovery, fixture tests, API catalog, and graph navigation.
3. **Source-grounded AI guide:** explain a selected feature step by step, answer learner questions with file and line citations, and label inferred or unresolved paths without requiring a running app.
4. **Observed behavior:** isolated example target, OpenTelemetry collection, trace summaries, waterfall, honest source mapping, and AI explanations of measured issues.
5. **Optional experiments:** repeatable baseline and stress runs, selected edge cases, one bounded fault, metrics comparison, and evidence-backed findings.
6. **Expansion:** Flask and Django depth, more faults and rules, architecture views, distributed event transport, cloud deployment, and additional language analyzers when justified.

The recommended repository layout is `frontend`, `backend`, `workers/analyzer`, `workers/traffic`, `workers/ai` when needed, `packages/ir`, `packages/schemas`, `analyzers/python`, `infra`, `fixtures`, `tests`, and `docs`. Modules should remain separable without forcing service boundaries before operational need exists.

## 16 Acceptance criteria

The first useful product demonstration is accepted when a learner can import a supported FastAPI repository without executing its code; select an endpoint; follow its route, handler, functions, detectable data access, and response in an interactive graph or mind map with clickable source links; and ask the AI guide about a selected step, receiving a cited, uncertainty-aware answer without a running application or database. A text step view must provide the same essential flow. The workflow must pass automated tests in CI and show unsupported or incomplete paths.

The runtime diagnosis demonstration adds an approved isolated target, a real request trace and database timings, a measured issue, and a testable improvement option. The optional system design lab adds bounded load and fault scenarios and a reproducible before/after comparison. Neither source-only explanations nor AI suggestions may be presented as measured behavior or verified fixes.

Additional framework, language, infrastructure, or AI capabilities are complete only when their own fixtures, safety checks, and user-facing evidence meet the same standard. Resume and interview claims should reflect behavior and measurements actually demonstrated by the project.

## 17 Open design decisions

Record decisions for the first import method, trace backend and retention, source mapping, job queue, authentication, experiment target policy, AI data handling, and any move to vector retrieval or service decomposition. Each decision should state its alternatives, constraints, and effect on reproducibility and security. Future collaborators should read `../AI_CONTEXT.md` alongside this specification and verify the current implementation before changing it.
