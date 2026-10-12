# Delivery sequence by dependency

1. **Foundation:** repository structure, project model, PostgreSQL migrations, API conventions, local containers, authentication, and CI.
2. **Static understanding:** safe import, Python scanner, AST extraction, versioned IR, FastAPI route discovery, fixture tests, API catalog, and graph navigation.
3. **Observed behavior:** isolated example target, OpenTelemetry collection, trace summaries, waterfall, and honest source mapping.
4. **Experiments:** repeatable baseline and stress runs, selected edge cases, one bounded fault, metrics comparison, and evidence-backed findings.
5. **Explanation:** retrieval over approved project evidence and an assistant that cites records and labels hypotheses.
6. **Expansion:** Flask and Django depth, more faults and rules, architecture views, distributed event transport, cloud deployment, and additional language analyzers when justified.

The recommended repository layout is `frontend`, `backend`, `workers/analyzer`, `workers/traffic`, `workers/ai` when needed, `packages/ir`, `packages/schemas`, `analyzers/python`, `infra`, `fixtures`, `tests`, and `docs`. Modules should remain separable without forcing service boundaries before operational need exists.
