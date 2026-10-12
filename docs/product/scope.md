# Product scope

### Core product capabilities

1. Create projects and import a Git revision or validated archive into an isolated workspace.
2. Analyze Python source without importing or executing it. Discover symbols, imports, resolvable calls, framework routes, and selected infrastructure usage.
3. Normalize findings into a versioned, language-neutral intermediate representation (IR), then persist an API catalog and code graph.
4. Navigate from an endpoint or graph node to its file and line, with confidence and source provenance on inferred edges.
5. Collect OpenTelemetry traces from a supported instrumented example application and connect spans to known entities when mapping evidence exists.
6. Run repeatable traffic and edge-case scenarios against an allowlisted isolated target. Record configuration and results.
7. Inject at least one controlled dependency failure or delay, compare behavior, and generate rule-based bottleneck findings with evidence.
8. Explain selected code paths, traces, and findings with an AI assistant that cites evidence IDs and distinguishes observation from hypothesis.
9. Retain revisions and experiment runs so users can compare and reproduce results.

### Explicit boundaries

The initial complete workflow targets FastAPI and a fixture application. Flask and Django route discovery can follow as separate analyzers. JavaScript/TypeScript, Java, and Go are future analyzers using the same IR contract. Production deployment, large-scale distributed processing, automatic architecture classification, and broad fault injection are extensions. Imported applications are never run on the host during analysis. CodeFlowAtlas does not autonomously modify a user's repository or claim that an LLM can prove runtime behavior.
