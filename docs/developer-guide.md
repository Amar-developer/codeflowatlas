# CodeFlowAtlas Developer Guide

## 1 Purpose and implementation status

CodeFlowAtlas is a developer engineering laboratory that connects repository source, API discovery, code relationships, observed traces, controlled load and failure experiments, bottleneck findings, and evidence-grounded explanations. This guide translates the [project specification](project-specification.md) into implementable boundaries and contracts. It is intended for engineers and coding assistants who will build or review the system.

**Current status:** the repository has a Next.js foundation page, FastAPI health API, PostgreSQL readiness check, and a three-service Compose stack. The remaining product components, database schema, and API payloads in this guide are **proposed designs**, not claims that working software exists. Before implementing a feature, inspect the current repository and record any design change in `docs/decisions/`.

The product path to preserve is:

```text
Pinned repository revision
  → safe static analysis
  → API catalog and confidence-labeled code graph
  → isolated instrumented target
  → observed request trace
  → repeatable traffic and fault experiment
  → deterministic finding with evidence
  → AI explanation that cites the evidence
```

The initial complete path supports a FastAPI fixture. Flask and Django, additional languages, Kafka, vector search, broad failure injection, and hosted deployment are extensions with their own acceptance criteria.

## 2 Repository map and ownership

| Path | Planned responsibility | Main boundary |
| --- | --- | --- |
| `frontend` | Next.js views, navigation, graph and trace visualizations | Consumes public API schemas; does not parse source or compute findings |
| `backend` | FastAPI API/BFF and modular domain services | Authorizes requests, owns durable state transitions, exposes stable APIs |
| `workers/analyzer` | Bounded static analysis jobs | Reads imported source as data; never imports or executes target modules |
| `workers/traffic` | k6 orchestration and controlled fault runs | Can reach only approved isolated targets |
| `workers/ai` | Evidence selection and explanation jobs | Receives scoped evidence; cannot execute repository instructions |
| `packages/ir` | Versioned entity and edge contract | Language analyzers emit this shape; graph consumers do not depend on Python AST nodes |
| `packages/schemas` | Shared API and event contracts | Changes require compatibility review and contract tests |
| `analyzers/python` | Python parser, symbol resolution, FastAPI discovery | Emits IR and warnings with provenance and confidence |
| `infra` | Local containers and later infrastructure definitions | Defines resource, network, and secret boundaries |
| `fixtures` | Known target repositories and expected analysis results | Enables deterministic regression checks |
| `tests` | Unit, integration, contract, security, and end-to-end checks | Verifies behavior visible to users |

Keep repository import, analysis, graph, tracing, experiments, findings, and AI as separate modules even while they run in one API deployment. Shared utilities must not create circular dependencies. Prefer module interfaces that exchange IDs and versioned data contracts instead of direct access to another module's tables.

## 3 Runtime components and trust zones

```text
Browser
  │ authenticated project requests
  ▼
FastAPI API/BFF ─────── PostgreSQL product records
  │        │
  │        ├────── job queue / progress channel
  │        └────── trace-summary query
  ▼
Workers: analyzer, experiment, AI
  │          │             │
  │          │             └── scoped evidence and approved model provider
  │          └── isolated target network and fault controller
  └── read-only imported source workspace

Instrumented target ── OpenTelemetry collector ── raw trace backend
```

There are three important trust zones. **Imported source** is untrusted input for parsing. **Runtime target** is executable code and must be isolated from the host, product database, and unauthorized network destinations. **AI context** may contain malicious text from a repository and must remain data, not instructions. Every API, job, and storage query is scoped to a project and pinned repository revision where applicable.

PostgreSQL is the system of record. Redis may support progress, cache, rate limits, and live update fan-out; a Redis loss must not erase completed results. Raw high-volume telemetry belongs in a trace backend with stable references from PostgreSQL. Kafka is introduced only after a concrete need for durable event streams and independent consumers has been demonstrated.

## 4 Domain identifiers and evidence classes

Use opaque IDs for `project_id`, `repository_id`, `revision_id`, `analysis_run_id`, `entity_id`, `edge_id`, `endpoint_id`, `trace_id`, `span_id`, `scenario_id`, `experiment_run_id`, and `finding_id`. Store `repository_sha` or a content fingerprint with every derived analysis or experiment record. Do not silently reuse results after the source revision or analyzer version changes.

The system handles three evidence classes:

| Class | Meaning | Example | Allowed claim |
| --- | --- | --- | --- |
| Static inference | Derived from source without execution | AST call edge at `orders/service.py:42` | “This call may occur on this path” |
| Runtime observation | Measured from an instrumented execution | Span `abc` lasted 140 ms | “This operation ran and took 140 ms in this trace” |
| Hypothesis | Interpretation of evidence | Database contention may explain p99 growth | “This is a possible cause requiring a check” |

Persist provenance and confidence beside static edges. Link observed spans to source entities only when instrumentation or a reliable mapping establishes the relationship. AI responses must cite the IDs of evidence records and label hypotheses.

## 5 Data model and invariants

The proposed relational core is documented in [database model](data/database-model.md). The first migrations should create only records required by implemented flows. A sensible dependency order is identity and projects, repository revisions, analysis runs and IR, then traces, experiments, findings, and conversations.

Important invariants:

- A repository revision is immutable after its source fingerprint is recorded.
- An analysis run is tied to exactly one revision, analyzer version, and IR schema version.
- A code entity or edge belongs to a revision and the run that produced it. Stable logical IDs may be derived from revision, qualified name, type, and source range, but collisions and renames must be handled explicitly.
- An endpoint points to a handler entity only when resolution succeeds; unresolved handlers retain the route record and a warning.
- An experiment run retains scenario configuration, target revision, environment label, tool versions, and resource limits. A rerun creates a new run record rather than overwriting prior evidence.
- A finding stores its rule version, input window, sample count, measured values, and evidence IDs. Its evidence cannot be silently replaced by a later run.
- A conversation and every retrieved chunk are project-scoped. Cross-project retrieval is a security failure.

Indexes should follow query shapes: project and revision, endpoint method/path, entity qualified name and type, trace ID, run timestamp, and finding severity. Apply retention policies to raw telemetry and large artifacts separately from durable project metadata.

## 6 Static import and analyzer pipeline

### Import boundary

The importer accepts a configured Git source or archive and produces an isolated revision workspace. Validate the source URL against outbound policy, pin the revision, and record its SHA or fingerprint. For archives, reject absolute paths, `..` traversal, unsafe symlinks, unsupported file types when relevant, excessive file count, excessive expanded size, and suspicious compression ratios. Normalize paths before comparing them with workspace boundaries. Apply file size, total byte, depth, and analysis time limits.

Static analysis must never run `pip install`, import a target Python module, execute a setup script, invoke a test runner on imported code, or evaluate repository-supplied commands. Only the explicitly supported runtime workflow may execute target code, inside an isolated environment.

### Analyzer stages

1. Enumerate safe source files and apply documented ignore rules.
2. Detect language and framework from files and syntax, recording uncertainty.
3. Parse Python files with `ast`, retaining parse errors as visible warnings.
4. Extract modules, classes, functions, imports, decorators, and source ranges.
5. Resolve direct symbols and calls within the supported resolution rules.
6. Discover FastAPI app/router declarations, route decorators, router inclusion and prefixes, methods, handlers, dependencies, and resolvable models.
7. Detect selected database, cache, queue, worker, and external HTTP indicators without claiming execution.
8. Normalize entities and edges into the versioned IR, validate references, persist results, and compute summary counts.
9. Publish progress and completion with a durable status record.

Dynamic imports, reflection, decorator-generated routes, aliases, and dependency injection can defeat static resolution. Preserve the endpoint or symbol when possible and expose an unresolved relationship or warning. Do not invent an edge to make a graph complete.

### Fixture expectations

For every supported syntax pattern, add a small fixture repository and expected endpoints, entities, edges, source ranges, confidence, and warnings. Include negative cases such as malformed files, dynamic registration, aliasing, and deliberately unresolved calls. Repeat analysis of the same revision should yield equivalent normalized output for the same analyzer version.

## 7 Intermediate representation contract

The IR is language-neutral. An entity needs a stable ID, type, display name, optional qualified name, source reference, properties, analyzer version, and schema version. An edge needs source and target IDs, relationship type, source location, confidence, provenance, and analyzer version. Use the entity and relationship types listed in [IR design](analysis/intermediate-representation.md).

The following is a **proposed illustrative shape**, not a finalized schema:

```json
{
  "schema_version": "1",
  "revision_id": "rev_123",
  "entity": {
    "id": "ent_checkout_handler",
    "type": "Function",
    "qualified_name": "shop.api.checkout",
    "display_name": "checkout",
    "source": {"path": "shop/api.py", "line_start": 28, "line_end": 46},
    "analyzer_version": "python-analyzer-v1"
  },
  "edge": {
    "id": "edge_checkout_inventory",
    "source_id": "ent_checkout_handler",
    "target_id": "ent_inventory_reserve",
    "type": "CALLS",
    "confidence": "high",
    "provenance": {"path": "shop/api.py", "line_start": 34},
    "analyzer_version": "python-analyzer-v1"
  }
}
```

Reject dangling IDs and unknown schema versions at the IR boundary. Keep static graph edges distinct from runtime span links. Schema migrations must define how old persisted runs remain readable; do not silently reinterpret their confidence or relationship meaning.

## 8 API design and job lifecycle

The proposed routes are listed in [HTTP API](api/http-api.md). Implement authorization centrally, with project membership checks before exposing a repository, graph, trace, experiment, or AI response. Use versioned Pydantic models, pagination, stable error codes, and a request ID. Do not expose internal workspace paths or full secrets.

Long-running operations use a run record with states such as `queued → running → completed`, with `failed` and `cancelled` terminal states where supported. Persist state changes in PostgreSQL. Progress messages are advisory and may be replayed or missed; clients recover by reading the run status endpoint. Workers must be safe to retry after a crash. A duplicate request should either return the existing idempotent operation or create a clearly separate run according to its API contract.

Illustrative start response:

```json
{
  "run_id": "analysis_123",
  "status": "queued",
  "revision_id": "rev_123",
  "status_url": "/projects/proj_1/analysis/analysis_123"
}
```

Illustrative error envelope:

```json
{
  "error": {
    "code": "UNSUPPORTED_SOURCE",
    "message": "This archive contains an unsupported entry.",
    "request_id": "req_123",
    "details": [{"field": "archive", "reason": "unsafe_symlink"}]
  }
}
```

Version event payloads and document ordering scope if a separate event bus is added. PostgreSQL remains authoritative for job state. An event ID, project ID, revision or run ID, schema version, correlation ID, and idempotent consumer behavior are required for durable asynchronous events.

## 9 Runtime instrumentation and trace mapping

The supported fixture runs in an isolated target environment and exports OpenTelemetry spans through a collector. Instrument inbound HTTP, meaningful service operations, database access, Redis or messaging if used, and outbound HTTP. Preserve `trace_id`, `span_id`, `parent_span_id`, service, operation, timestamps, duration, status, errors, and sanitized attributes.

The trace explorer reads span relationships and shows a waterfall. It may link a span to an IR entity when instrumentation records a stable symbol or a verified mapping rule resolves it. An automatic database span may reveal a dependency and timing without identifying the exact source line. Show the strongest supported location and indicate when it is approximate or unavailable. Sampling and retention must be visible before results are used as evidence.

Do not send full bodies, credentials, raw authorization headers, or unbounded query parameters to the trace backend. A trace summary in PostgreSQL can provide search and project scoping while raw spans remain in specialized storage.

## 10 Traffic, edge-case, and fault runs

A traffic scenario includes approved target ID, environment label, HTTP method/path, payload reference, virtual users or arrival rate, ramp-up, duration, headers/auth strategy, success criteria, and safety limits. k6 is the proposed runner. Save tool version, exact scenario definition, target revision, resource limits, start/end status, and output artifacts. Each run generates new immutable results for comparison.

The first product flow needs a baseline and one stress scenario, not every load profile. Record throughput, p50/p95/p99, error rate, timeouts, CPU/memory, and relevant dependency metrics with sample counts and collection windows. Treat a configured request rate as a test input, not a guaranteed achieved rate.

Edge cases are deterministic tests generated from resolvable schemas or supplied manually. Save input, expected outcome, actual outcome, trace ID, and verdict. A missing schema or authentication strategy should prevent a case from being claimed as executed.

Failure injection is opt-in and permitted only against an isolated target. Start with one bounded dependency delay or error. A run must include authorization, target allowlist validation, maximum duration, resource limits, cleanup action, and audit record. Fault state must be cleaned even after timeout or worker failure. An arbitrary URL pasted into the UI is not an acceptable fault target.

## 11 Findings and AI explanation contract

Start with deterministic finding rules: dominant cumulative/exclusive span duration, repeated database spans, concentrated errors, and p99 growth across comparable runs. Each rule needs defined inputs, minimum sample requirements, calculation, threshold or ranking logic, version, and limitations. A finding contains the actual measured values, supporting IDs, scenario or trace window, severity, confidence or uncertainty, and a human-readable statement.

AI is a reader of evidence, not a measurement system. Build an evidence bundle from project-authorized source ranges, IR paths, endpoint metadata, trace summaries, metrics, findings, and documentation. Exclude secrets before indexing or retrieval. The assistant response should have:

1. **Observed facts:** direct measurements or source facts with IDs.
2. **Inferences:** reasoned explanations with confidence and supporting facts.
3. **Unknowns:** missing instrumentation, unsupported analysis, or insufficient samples.
4. **Next checks:** tests or inspection steps the developer can run.

Repository documentation and source comments may contain prompt-injection instructions. Treat them as quoted data. The assistant must not execute commands, change project settings, reveal another project's content, or cite evidence it did not receive. Structured retrieval may be enough at first; embeddings and a vector store need a demonstrated retrieval problem before adoption.

## 12 Frontend workflow

The UI should guide users through project creation, import, analysis progress, endpoint discovery, graph inspection, tracing, experiments, findings, and explanation. The [frontend specification](frontend/frontend-experience.md) lists planned screens. Keep the endpoint page as the central navigation point: source and graph links on one side, observed traces and experiments on the other.

Graphs need filtering and bounded slices. Every inferred edge shows confidence and source provenance. Trace waterfalls show real durations and errors. Comparison charts show units, sample sizes, target revision, environment, and scenario configuration. Empty and partial states explain what is missing: no instrumented target, unsupported syntax, unavailable source mapping, insufficient trace samples, or a failed run. Never turn missing evidence into a polished but unsupported diagram.

## 13 Security requirements by boundary

The [security design](security/security-and-trust-boundaries.md) covers the full threat model. Developers should use the following checks at each entry point:

| Entry point | Required controls |
| --- | --- |
| Git URL | Scheme and host policy, SSRF prevention, pin revision, size/time bounds, no credential logging |
| Archive | Path normalization, traversal and symlink checks, expanded-size and file-count limits |
| Analyzer | Parse as data, no imports or commands from target, bounded CPU/memory/time, read-only mount |
| Runtime target | Non-root isolated container, restricted network, resource and lifetime limits |
| Traffic/fault run | Explicit environment label, allowlisted target, bounded scenario, cleanup and audit |
| API query | Authentication, project authorization, pagination, data minimization |
| Trace and AI | Attribute sanitization, secret scanning, scoped retrieval, prompt/data separation |

Test these boundaries with adversarial fixtures. A feature is not complete if a happy-path demonstration works but imported source can escape its workspace or a project can read another project's evidence.

## 14 Local development contract

The current local stack contains the Next.js frontend, FastAPI API, and PostgreSQL. The root README contains the Compose commands and health URLs. The intended expanded stack adds the chosen background job mechanism, trace collection/backend, and an instrumented FastAPI fixture. Add Redis, Kafka, Prometheus, and Grafana only as corresponding features become real.

As capabilities arrive, document migrations, fixture loading, analysis, tracing, safe experiments, tests, and disposable data reset commands in the root README. Keep example environment variable names aligned with the code.

## 15 Test strategy and verification gates

| Layer | What it proves |
| --- | --- |
| Unit | Parser behavior, route resolution, IR validation, finding calculations, request schemas |
| Fixture regression | Known graph and endpoint output for supported and unsupported syntax |
| Integration | Database migrations, job state, Redis or Kafka when active, trace ingestion |
| Contract | API and event schemas remain compatible or change deliberately |
| End-to-end | Import → API/graph → trace → experiment → finding → explanation |
| Security | Archive traversal, SSRF policy, unsafe execution, cross-project access, secrets |
| Load and failure | Controlled target behavior and reproducible measurements |

The golden flow in [product demonstration](product/golden-flow.md) is the integration target. CI should run the tests relevant to implemented capabilities, lint/build checks, and appropriate dependency or container scans. Do not mark a framework or language “supported” until its fixtures and documentation reflect known limits.

## 16 Implementation sequence and completion rules

Build by dependency, with a working and testable outcome at each stage:

1. **Foundation:** project records, migrations, auth, API conventions, local container setup, CI, and a minimal UI shell.
2. **Safe source understanding:** import, bounded file scanner, Python AST extraction, IR validation, FastAPI route discovery, persisted API catalog, and fixture regression tests.
3. **Graph navigation:** filtered graph API, source links, confidence labels, warnings, and WebSocket or polling progress.
4. **Observed behavior:** isolated fixture target, OpenTelemetry collection, trace search, waterfall, and truthful source mapping.
5. **Experiment loop:** saved baseline and stress runs, one bounded fault, comparable metrics, deterministic finding, and rerun support.
6. **Grounded explanation:** scoped retrieval, evidence IDs, observed/inferred/unknown response structure, and prompt-injection tests.
7. **Extensions:** additional frameworks, deeper analyzers, distributed event transport, richer architecture views, cloud hosting, and new languages only when their acceptance checks are defined.

A feature is complete when a user can perform it, results carry provenance, unsupported cases are visible, failure is safe, tests verify the contract, and docs match the running software. The [acceptance criteria](delivery/acceptance-criteria.md) define the first complete product demonstration.

## 17 Decision log and change discipline

Before committing to a trace backend, queue, authentication model, source-mapping method, target policy, AI provider, vector store, or service split, write an architecture decision record using [ADR template](decisions/ADR_TEMPLATE.md). State the concrete need, alternatives, trust boundary, migration impact, and verification. Treat this guide and the specification as living intent: when implementation settles a proposed contract, update the guide and relevant focused document together.

Future coding assistants should read [AI context](../AI_CONTEXT.md), inspect current code and tests, and explicitly state whether a requested capability is implemented, planned, or unsupported. They should continue the smallest complete slice of the central workflow and preserve the distinction between source inference, runtime observation, and engineering hypothesis.
