# Delivery sequence by dependency

1. **Foundation and first visible slice:** repository structure, local containers, API conventions, and FastAPI endpoint discovery on a bundled fixture. Add the project model and PostgreSQL migrations as results become durable. Add authentication and project authorization before multi-user or public repository access; they do not need to delay the local fixture demonstration.
2. **Static understanding:** safe import, Python scanner, AST extraction, versioned IR, FastAPI route discovery, fixture tests, API catalog, and graph navigation.
3. **Source-grounded AI guide:** explain a selected feature step by step, answer learner questions with file and line citations, and label inferred or unresolved paths. This first useful flow works without a running app.
4. **Observed behavior:** isolated example target, OpenTelemetry collection, trace summaries, waterfall, honest source mapping, and AI explanations of measured issues.
5. **Optional experiments:** repeatable baseline and stress runs, selected edge cases, one bounded fault, metrics comparison, and evidence-backed findings.
6. **Expansion:** Flask and Django depth, more faults and rules, architecture views, distributed event transport, cloud deployment, and additional language analyzers when justified.

The recommended repository layout is `frontend`, `backend`, `workers/analyzer`, `workers/traffic`, `workers/ai` when needed, `packages/ir`, `packages/schemas`, `analyzers/python`, `infra`, `fixtures`, `tests`, and `docs`. Modules should remain separable without forcing service boundaries before operational need exists.
