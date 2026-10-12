# Product vision

### Problem

Developers frequently inherit unfamiliar repositories or generate code with AI. They can read individual files, but it is harder to see which API starts a behavior, which functions and dependencies it reaches, what actually runs, and why latency or errors appear under stress. Static diagrams alone can be incomplete. Traces alone can lack source context. Load tests alone identify symptoms without a path back to code.

### Vision

CodeFlowAtlas joins those forms of evidence in one workspace. A user imports a repository, inspects discovered APIs and a source-linked code graph, runs a supported application in a controlled environment, views real request traces, repeats traffic and fault experiments, and receives findings whose supporting spans and metrics can be opened. An AI assistant may explain those findings, but must identify its evidence and label uncertainty.

### Target users and value

The primary user is a developer learning or diagnosing a Python web application, including AI-generated or inherited code. Engineering leads, educators, interview candidates, and onboarding teams are secondary users. The product should shorten the path from “what does this endpoint do?” to a verifiable answer and make performance or failure behavior teachable through repeatable experiments.

### Product principles

- **Evidence before explanation.** Source locations, analyzer output, traces, metrics, and experiment results are first-class records.
- **One reproducible path first.** A complete FastAPI demonstration is more valuable than superficial support for many frameworks.
- **Uncertainty is visible.** Static relationships carry confidence and provenance; missing telemetry remains missing.
- **Safety is part of the workflow.** Repository inspection does not execute imported code. Runtime tests use isolated targets and explicit authorization.
- **Language independence at the data boundary.** Python is the first deep analyzer; the shared intermediate representation supports later analyzers.
