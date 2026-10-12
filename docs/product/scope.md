# Product scope

### Core product capabilities

1. Create projects and import a supported public GitHub or Bitbucket repository URL at a pinned Git revision, or a validated archive, into an isolated workspace. Private repository access requires a separate authorization design.
2. Analyze Python source without importing or executing it. Discover symbols, imports, resolvable calls, framework routes, and selected infrastructure usage.
3. Normalize findings into a versioned, language-neutral intermediate representation (IR), then persist an API catalog and code graph.
4. Let a learner select an API or feature and navigate an interactive flow graph and mind map of its route, handler, functions, dependencies, detectable database access, and response. Nodes and edges open file and line references, confidence, and source provenance.
5. Provide a source-grounded AI guide that explains each step in plain language, answers follow-up questions, cites inspected file and line evidence, and labels unresolved relationships. This source-only mode works without a running app or database.
6. Collect OpenTelemetry traces from a supported instrumented application, including endpoint duration, errors, and sanitized database query counts and timings; show a waterfall and link observed spans to source graph entities only when mapping evidence exists.
7. Explain observed issues with cited runtime evidence and offer testable optimization options, including query, indexing, cache, and concurrency strategies where relevant. State tradeoffs and allow a before/after rerun.
8. Offer optional repeatable, bounded traffic and edge-case scenarios against an allowlisted isolated target, including a configurable 100-concurrent-virtual-user learning scenario. Chart configured and achieved load, timings, errors, and resource metrics with units and sample counts.
9. Inject at least one controlled dependency failure or delay, compare behavior, and generate rule-based bottleneck findings with evidence.
10. Retain revisions and experiment runs so users can compare and reproduce results.

### Explicit boundaries

The first implementation proves the flow on a FastAPI fixture before accepting external repository URLs. The intended complete workflow supports safe import from public GitHub and Bitbucket links for supported Python/FastAPI repositories. Importing a repository permits source analysis; it does not imply that arbitrary applications can be started or instrumented. Runtime timing and the 100-user lab are available only for approved isolated targets with resource, duration, and destination limits. Flask and Django route discovery can follow as separate analyzers. JavaScript/TypeScript, Java, and Go are future analyzers using the same IR contract. Production deployment, large-scale distributed processing, automatic architecture classification, and broad fault injection are extensions. Imported applications are never run on the host during analysis. CodeFlowAtlas does not autonomously modify a user's repository, expose raw database values or secrets, or claim that an LLM can prove runtime behavior.
