# Product vision

### Problem

Students and people building with AI often have a small project that appears to work, but they do not know how its routes, functions, database calls, and responses fit together. When an error or slowdown appears, they may not know where to look or how to verify a suggested fix. A repository link alone does not explain the feature flow, and a generic AI answer can guess at code or runtime behavior it has not inspected.

### Vision

The intended entry point is a GitHub or Bitbucket repository URL for a supported small application. CodeFlowAtlas pins a revision, safely reads its source, discovers APIs, and lets a learner select an endpoint or feature. Its main workspace is an interactive flow graph and mind map showing the path step by step: route → handler → functions and dependencies → detectable database access → response. Selecting a node or edge opens the supporting source and an AI guide that explains it in plain language, answers follow-up questions, and says when a relationship is inferred or unknown. This source-only visual experience must work without a database or runnable application.

When the application can run with approved instrumentation in an isolated target, the same workspace adds an observed path, trace waterfall, request and database timings, errors, and source mappings where reliable. A learner can switch between the inferred map and observed trace without confusing them. The AI guide can then explain a measured issue and suggest a testable change with evidence and tradeoffs. A separate, controlled lab can send bounded traffic such as 100 virtual users and show latency, error, and resource charts plus before/after comparisons. Load and fault experiments deepen learning; they are not required before a learner can understand a code flow.

### Target users and value

The primary users are students and AI-assisted builders, often called vibe coders, working on small real projects. They need to move from “AI wrote this feature, but I do not understand it” to a source-linked explanation they can inspect and question. A second use is diagnosing an actual error or slowdown when a supported runtime is available. Educators, onboarding teams, and experienced developers reviewing unfamiliar code are additional users.

### Learning model

The learning path follows one selected feature. A source-linked flow teaches how a request enters the app, reaches code and data, and returns a result. The learner can ask the AI guide “why is this function called?”, “where does this value come from?”, or “what could fail here?” and receive answers grounded in the analyzed revision. A trace, when available, shows which operations actually ran and where time was spent. A controlled load or fault experiment makes latency, throughput, bottlenecks, and resilience visible for learners who want to go deeper.

Every explanation should include a concrete source, trace, metric, or experiment reference; a plain-language explanation; what is known or uncertain; and a next check. Optimization advice should add the relevant tradeoff and a way to measure whether the change helps. Where the repository does not show a cache, queue, or service boundary, the product may describe it as a possible design option, not claim that the application uses it. The AI guide and learning views are planned capabilities, not part of the current foundation page.

### Product principles

- **Evidence before explanation.** Source locations, analyzer output, traces, metrics, and experiment results are first-class records.
- **Learning through investigation.** Developers should move from a concrete behavior to a design concept and test a hypothesis rather than memorize a diagram.
- **Visual evidence first.** Flow graphs, mind maps, traces, and charts are navigable views of source or measurements; each element opens its evidence and displays uncertainty.
- **One reproducible path first.** A complete FastAPI demonstration is more valuable than superficial support for many frameworks.
- **Uncertainty is visible.** Static relationships carry confidence and provenance; missing telemetry remains missing.
- **Safety is part of the workflow.** Repository inspection does not execute imported code. Runtime tests use isolated targets and explicit authorization.
- **Language independence at the data boundary.** Python is the first deep analyzer; the shared intermediate representation supports later analyzers.
