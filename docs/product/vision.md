# Product vision

### Problem

Students and people building with AI often have a small project that appears to work, but they do not know how its routes, functions, database calls, and responses fit together. When an error or slowdown appears, they may not know where to look or how to verify a suggested fix. A repository link alone does not explain the feature flow, and a generic AI answer can guess at code or runtime behavior it has not inspected.

### Vision

The intended entry point is a GitHub or Bitbucket repository URL for a supported small application. CodeFlowAtlas pins a revision, safely reads its source, discovers APIs and supported frontend entry points, and lets a learner select an endpoint, page action, or feature. Its main workspace is an interactive flow graph and mind map showing the path step by step: frontend page or component → event or data loading → HTTP call → backend route → functions and dependencies → detectable database access → response and UI update. A backend-only repository begins at its route; a frontend-only repository stops at its unresolved or external API call. Selecting a node or edge opens the supporting source and an AI guide that explains it in plain language, answers follow-up questions, and says when a relationship is inferred or unknown. This source-only visual experience must work without a database or runnable application.

When the application can run with approved instrumentation in an isolated target, the same workspace adds an observed path, trace waterfall, request and database timings, errors, and source mappings where reliable. A learner can switch between the inferred map and observed trace without confusing them. An AI test bot can propose a reviewable student journey from discovered APIs, generate synthetic test records, and run the approved journey against a disposable copy of the application. The bot reports reproducible failures and measured slowdowns with request, trace, and code evidence; it does not invent a defect from source alone. A separate, controlled system design lab can send bounded traffic such as 100 virtual users, inject a supported dependency fault, and show latency, error, resource, and before/after charts. Runtime and load experiments deepen learning; they are not required before a learner can understand a code flow.

### Target users and value

The primary users are students and AI-assisted builders, often called vibe coders, working on small real projects. They need to move from “AI wrote this feature, but I do not understand it” to a source-linked explanation they can inspect and question. A second use is diagnosing an actual error or slowdown when a supported runtime is available. Educators, onboarding teams, and experienced developers reviewing unfamiliar code are additional users.

### Learning model

The learning path follows one selected feature. A source-linked flow teaches how a request enters the app, reaches code and data, and returns a result. The learner can ask the AI guide “why is this function called?”, “where does this value come from?”, or “what could fail here?” and receive answers grounded in the analyzed revision. A trace, when available, shows which operations actually ran and where time was spent. A controlled load or fault experiment makes latency, throughput, bottlenecks, and resilience visible for learners who want to go deeper.

Every explanation should include a concrete source, trace, metric, or experiment reference; a plain-language explanation; what is known or uncertain; and a next check. Optimization advice should add the relevant tradeoff and a way to measure whether the change helps. Where the repository does not show a cache, queue, or service boundary, the product may describe it as a possible design option, not claim that the application uses it. Guided exercises can ask a learner to predict a flow or failure before revealing the evidence. Flow and experiment comparisons can show how behavior changes across revisions or tested improvements. These AI and learning views are planned capabilities, not part of the current foundation page.

### Product principles

- **Evidence before explanation.** Source locations, analyzer output, traces, metrics, and experiment results are first-class records.
- **Learning through investigation.** Developers should move from a concrete behavior to a design concept and test a hypothesis rather than memorize a diagram.
- **Visual evidence first.** Flow graphs, mind maps, traces, and charts are navigable views of source or measurements; each element opens its evidence and displays uncertainty.
- **One reproducible path first.** Complete the FastAPI backend flow, then a React/Next.js-to-FastAPI path, before claiming broad frontend or backend framework support.
- **Uncertainty is visible.** Static relationships carry confidence and provenance; missing telemetry remains missing.
- **Safety is part of the workflow.** Repository inspection does not execute imported code. Runtime tests use isolated targets and explicit authorization.
- **Disposable data only.** Runtime tests use a separate generated schema and synthetic seed data derived from verified models, migrations, or fixtures; they never attach to an imported project's original or production database. If a runnable schema cannot be validated, the product keeps source-only analysis available and marks runtime testing unsupported.
- **Language independence at the data boundary.** Python/FastAPI is the first deep analyzer; JavaScript/TypeScript frontend and backend analyzers and further Python frameworks can map into the same versioned intermediate representation.
