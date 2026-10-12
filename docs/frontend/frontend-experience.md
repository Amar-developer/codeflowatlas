# Frontend experience

The current `frontend/` app is a Next.js foundation page. It checks the FastAPI liveness and PostgreSQL readiness endpoints on each request, links to the API documentation, and labels future capabilities as planned.

The primary screens are project dashboard, repository import, analysis progress, API explorer, code graph, source viewer, trace explorer, traffic lab, failure lab, findings, AI assistant, run history, and project settings. Architecture view is useful when it shows an observed or explicitly inferred model with supporting evidence. React Flow can render graph slices; charts should expose units, sample sizes, and comparison conditions. Large graphs need filtering, clustering, and source search rather than an unreadable all-node canvas.

The interface should lead users from an endpoint to its graph, then to a trace, then to an experiment and finding. Empty states explain when a capability requires instrumentation or an isolated target. Error states name the failed step and preserve partial results when safe.
