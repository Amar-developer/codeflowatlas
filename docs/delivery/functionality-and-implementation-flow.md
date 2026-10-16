# Functionality and implementation flow

This document is the practical map for building CodeFlowAtlas. It explains what the user does, what the system must produce, and the order in which to implement the features. It is ordered by dependency and has no day-based schedule. The [project specification](../project-specification.md) remains the full product contract; the [developer guide](../developer-guide.md) defines technical and safety details.

## Product in one sentence

CodeFlowAtlas helps a student or AI-assisted builder understand a small real application visually: paste a supported repository link, select an API or feature, explore its source-linked flow graph and mind map, and ask an AI guide about selected steps. If a supported application can run safely against a disposable synthetic dataset, an AI test bot can propose a reviewed student journey and a controlled runner can produce replayable issues, trace waterfalls, timing and error views, and optional load charts to investigate and test an improvement.

## Where login fits

There are two distinct meanings of login:

1. **CodeFlowAtlas account login:** lets a person access their own projects, repository revisions, traces, and experiments. This is an access-control feature, not the main product result. A single-user local fixture demonstration can precede it; account and project authorization must be in place before a multi-user or public service accepts private repositories. The active backend now has auth models and routes under development; the code preserved in `legacy-auth-foundation/` is a separate earlier prototype.
2. **Login in an imported application:** an endpoint such as `POST /login` may be discovered and displayed like any other route. Static analysis can report its handler and detectable dependencies; it must not execute the target app, attempt to sign in, collect credentials, or claim the route works. A later approved runtime experiment may use a controlled fixture account in an isolated target.

Login alone does not demonstrate the CodeFlowAtlas idea. The first visible product result should be a discovered endpoint with a real source location.

## User-facing product flow

```text
Open workspace
  → sign in when account access is enabled
  → create a project
  → paste a supported GitHub or Bitbucket link and pin one revision
  → run safe static analysis
  → select an API or feature and explore its graph or mind map
  → click a node or edge to inspect source and ask the AI guide about it
  → see unresolved steps and unsupported code clearly
  → optionally prepare a disposable schema and synthetic seed data
  → review an AI-proposed test journey against an approved isolated target
  → run that finite journey with a deterministic test runner
  → inspect a real trace waterfall, database timings, and errors
  → ask the AI guide to explain one observed issue and a testable change
  → optionally run bounded load or fault experiments and inspect charts
  → rerun the same scenario after a change and compare results
```

The main navigation path is **repository link → revision → API or feature → interactive flow graph or mind map → selected source evidence → AI explanation and questions**. Supported runtime evidence can extend that path to **trace waterfall → issue → improvement idea → optional load charts → before/after comparison**. Every screen should make the current project and repository revision clear.

## Functionality list

| Functionality | User action and visible result | System responsibility | Current state |
| --- | --- | --- | --- |
| Workspace status | Open the home page and see API/database status | Next.js checks FastAPI health endpoints | Implemented foundation |
| Account and project access | Sign in and see only authorized projects | Authenticate users and enforce project membership in every query and job | Auth models and routes under development; project authorization planned |
| Project and revision | Create a project and select a pinned source revision | Store project, source fingerprint or commit SHA, and import status | Planned |
| Safe repository import | Paste a supported public GitHub or Bitbucket URL and see the pinned revision and any skipped files | Bound size/time, validate host and paths, isolate source, never run imported code during analysis | Planned |
| Python analysis | Start analysis and inspect progress and warnings | Parse source with `ast` as data; record supported and unresolved cases | Standalone fixture analyzer prototype; product integration planned |
| API catalog | Browse methods and paths, select an endpoint, jump to its handler | Discover FastAPI routes, preserve source line, confidence, and analyzer version | Standalone route discovery prototype; product UI planned |
| Flow graph, mind map, and source | Navigate one feature's route, calls, dependencies, data access, and response; click nodes and edges to open source | Render focused slices from versioned IR; show uncertainty and provenance; provide search and a text step view | Planned |
| Visualization levels | Move from repository overview to a feature flow and function calls | Build bounded views from the same revision and IR; preserve source links, confidence, and incomplete areas | Planned |
| Natural-language query and suggestions | Ask a code question, choose an editable suggestion, and open cited code and a focused graph | Retrieve project-scoped evidence; suggest questions from known entities; label unsupported answers | Planned |
| Diagram export | Download the selected diagram for documentation | Export SVG or PNG with revision, title, evidence legend, uncertainty, and text outline under project authorization | Planned |
| LLM prompt draft | Inspect and edit a prompt containing the selected question and supporting code | Bound and filter cited evidence; show exactly what is copied or sent; exclude secrets | Planned |
| Full-stack source flow | Select a frontend action and follow a supported HTTP call into its backend route and response | Analyze React/Next.js and FastAPI source, match resolvable HTTP contracts, retain both call-site locations, and show unknown links | Planned after FastAPI source flow |
| AI code-flow guide | Ask what each step does, why it is reached, and where a value comes from | Answer with inspected file and line citations; label inferred and unresolved steps; work without a database | Planned |
| Synthetic target setup | Review a disposable schema, generated sample records, test accounts, and test doubles | Validate source models/migrations/fixtures against the runnable target; never use original or production data; explain unsupported setup | Planned |
| AI test bot | Review a student-like API journey and inspect a replayable issue report | Propose finite actions and assertions from verified endpoints; enforce saved target/actions/limits; execute with deterministic runner; cite requests and traces | Planned |
| Trace waterfall and database timing | Send an approved request and view total request time, query count, query durations, and errors | Run only an isolated instrumented target; ingest sanitized OpenTelemetry spans; link to graph only with reliable mapping | Planned |
| Traffic charts | Optionally run a saved baseline or bounded 100-concurrent-virtual-user scenario and compare metrics | Bound target, rate, duration, resources, and chart configured versus achieved load with units and sample counts | Planned |
| Failure experiment | Inject one approved delay or failure and compare behavior | Apply bounded fault to an isolated target and guarantee cleanup | Planned |
| Finding | Open a bottleneck or error finding and its evidence | Apply deterministic, versioned rules to measured spans and metrics | Planned |
| Optimization options | Open a finding and compare relevant query, index, cache, pool, or concurrency ideas | Link each option to evidence, tradeoffs, and a testable before/after scenario | Planned |
| AI runtime explanation | Ask why a measured request failed or slowed down and open supporting records | Retrieve project-scoped source and runtime evidence; distinguish observation, inference, and unknowns | Planned |
| History and rerun | Reopen a revision or rerun a saved scenario | Keep immutable run records and show differences between comparable runs | Planned |
| Learning and flow comparison | Predict a step or compare one endpoint across revisions | Reveal evidence-backed answers; distinguish changed source edges from changed observed behavior | Later extension |

## Implementation flow by dependency

Each slice ends with a user-visible result and a verification gate. The order below is conceptual, not a calendar.

### 0. Keep the running foundation reliable — implemented

The existing repository has a Next.js home page, FastAPI health endpoints, PostgreSQL, Dockerfiles, and one Compose stack. Keep its run instructions and health checks working while adding features. The frontend currently shows platform status, not repository analysis.

### 1. Prove endpoint discovery on a bundled fixture — first new functionality

- Add a small FastAPI fixture under `fixtures/fastapi-basic/` with known routes, including a route that calls another function.
- Read its Python files without importing, installing, or executing fixture code. Parse with Python `ast`.
- Return method, normalized path, handler name, repository-relative file, line number, and warnings for unresolved cases.
- Show the discovered endpoints on a simple frontend page. Selecting an endpoint opens its source location or a source excerpt.
- Verify expected routes and source ranges with a fixture regression test; show parse failures as warnings instead of losing the whole result.

**Done when:** a developer can point CodeFlowAtlas at the bundled fixture, open a route such as `POST /checkout`, and see the correct handler and source line. This first slice may use a local single-user workflow and need not accept arbitrary repository URLs.

### 2. Make projects and analysis runs durable

- Add the first PostgreSQL tables for projects, repository revisions, analysis runs, endpoints, and warnings. Add migrations when these tables are introduced.
- Tie every endpoint to one immutable source revision and analyzer version. Keep run status and failures visible.
- Add API and frontend project views so a restart does not erase the analysis result.

**Done when:** the same stored run can be reopened after a container restart, and changing the source revision creates a distinct result.

### 3. Add account login and project authorization before multi-user use

- Design user, session, and project membership rules for the active `backend/` API. Review the earlier prototype before reusing any of it.
- Protect every project-scoped endpoint and background job, not only the UI pages.
- Test that one account cannot read another account's source, endpoints, traces, or findings.

**Done when:** authorized users can access their projects and cross-project requests are rejected. A public or multi-user launch must not precede this gate.

### 4. Accept external repositories safely

- Add supported public GitHub and Bitbucket URL import at a pinned Git revision, plus validated archive import where appropriate, with allowlisted network behavior, path normalization, and file/byte/time limits.
- Store an isolated read-only analysis workspace and a content fingerprint. Treat repository text as untrusted input.
- Surface rejected files and unsupported syntax to the user.

**Done when:** a supported public GitHub or Bitbucket repository imports reproducibly without executing its code, the UI shows the pinned revision and skipped or unsupported files, and traversal, symlink, oversized, and disallowed-source cases are rejected.

### 5. Build the source-linked API and code graph

- Expand Python extraction to modules, classes, functions, imports, and resolvable calls. Discover FastAPI routers and prefixes.
- Normalize entities and edges into the versioned, language-neutral IR. Keep static confidence and provenance on every inferred relationship.
- Render a focused, interactive endpoint graph with route, functions, dependency calls, detectable database operations, and response. Let users select nodes and edges to open source lines; provide a text step view. Do not invent edges for dynamic behavior.

**Done when:** a learner can follow the fixture's known `POST /checkout` path in a graph or mind-map view from route to response, open supporting source from each supported step, and see unresolved relationships visibly labeled.

### 6. Add the source-grounded AI guide

- Build an evidence bundle from the selected endpoint, graph path, source ranges, warnings, and revision ID.
- Let the learner select a graph node or edge and ask what a function does, why a call may happen, where a value comes from, or what can fail. Cite the inspected files and lines in every answer and highlight supporting graph elements.
- Separate facts found in source from inferred edges and unknown behavior. Treat repository content as data, not instructions to the assistant.
- Make the guide useful without a database, running target, trace, or load test.

**Done when:** a student can select one endpoint, ask a follow-up question about its flow, verify the answer against source lines, and see uncertainty where the analyzer cannot resolve a relationship.

### 7. Add observed runtime tracing

- Launch only the approved fixture in an isolated target environment with a validated disposable schema, synthetic seed data, and supported local test doubles. Never accept an original or production database connection.
- Send a controlled request, retain trace and span IDs, total request duration, database query counts and durations, status, timing, parent-child relationships, and project/revision links. Redact query parameters and row values.
- Show a trace waterfall beside the static graph, including database spans. Link a span to a source node only when mapping evidence is reliable; keep inferred and observed paths visibly distinct.

**Done when:** a learner can distinguish a statically possible path from what actually happened in one request, including which instrumented database operations consumed time. The AI guide can explain a measured error or slowdown with cited spans.

### 8. Add a reviewed AI test journey

- Let AI propose a short student-like path from the selected API catalog, verified schemas, source evidence, and fixtures. Include synthetic accounts and records, expected checks, and any state-changing effects.
- Show target identity, action list, synthetic dataset, maximum requests, duration, and allowed network destinations before the learner authorizes the run once.
- Execute the frozen plan through a deterministic runner, capture responses, assertions, errors, trace IDs, and replay configuration. The bot cannot add actions or widen limits during execution.
- If schema or dependencies cannot be validated, show exactly why runtime testing is unsupported while retaining source-only analysis.

**Done when:** one approved fixture journey can be repeated on a fresh synthetic dataset and any reported issue links to an actual failed check, request, trace, revision, and scenario version.

### 9. Add optional repeatable experiments and measured findings

- Save bounded baseline and stress scenarios against an allowlisted isolated target, including a configurable 100-concurrent-virtual-user example; chart configured and achieved load, latency percentiles, errors, timeouts, database timing, and resource metrics with units and sample counts.
- Add one bounded dependency delay or failure, automatic cleanup, and before/after comparison.
- Generate rule-based findings from recorded spans and metrics, with thresholds, rule version, measured values, and evidence IDs.

**Done when:** a learner who chooses the deeper lab can rerun the documented 100-user scenario, inspect where latency or errors increased, and trace any finding to measured data.

### 10. Extend the AI guide to optimization comparisons

- Retrieve only the current project's approved endpoint, graph, trace, experiment, and finding records.
- Require explanations and optimization options to cite evidence IDs, label observations, interpretations, and unknowns separately, and state tradeoffs. A caching option must discuss eligibility, invalidation, consistency, and a comparison run.
- Treat repository content as data, never as instructions to the assistant.

**Done when:** an explanation of a measured slowdown links to the relevant source, database and request spans, metrics, and finding, and gives at least one testable improvement option without inventing results. The earlier source-only guide remains available when runtime evidence is missing.

## Learning layer across the flow

Each completed feature should help answer a learner's concrete question. The endpoint and graph explain request flow and database access; the AI guide translates those links into plain language and supports follow-up questions. Traces measure request and query timing only when an approved target runs. Optional 100-user and fault runs expose latency, throughput, bottlenecks, and resilience. Findings lead to design tradeoffs such as query optimization versus caching or synchronous work versus a queue. A concept view should show the supporting evidence, explain what is inferred, and suggest an experiment that could change the conclusion. These learning views are planned; the current frontend does not yet generate them.

### 11. Add full-stack framework support in verified slices

After the full FastAPI path works, add React and Next.js source analysis for a frontend action that calls a FastAPI route. Show page or component, action or data loading, HTTP call, backend route, downstream source flow, and response handling where each link can be resolved. Preserve unknown links and frontend-only or backend-only partial flows. Next add Express as a separate backend family; evaluate NestJS, Flask, Django, and later languages through their own fixtures and user-facing limits. Detection, catalog, source flow, observed flow, and test lab are distinct support levels. The [framework support roadmap](../analysis/framework-support-roadmap.md) lists their order and verification rules. More fault types, Redis, Kafka, vector retrieval, and hosted deployment remain later choices with their own acceptance criteria.

## Evidence rule across the whole flow

Keep three claims separate in storage, APIs, and UI: **static inference** (what source suggests may happen), **runtime observation** (what an instrumented request did), and **hypothesis** (an explanation to test). AI cannot convert a hypothesis into a measurement. See the [golden demonstration flow](../product/golden-flow.md) for the complete example and the [acceptance criteria](acceptance-criteria.md) for the final product gate.
