# Visualization system

CodeFlowAtlas is a visual learning tool. The central screen is a map of one selected API or feature, with code, evidence, and AI explanation available from the selected step. The views below are product requirements, not implemented features.

## Planned views

| View | Learner question | Evidence and interaction |
| --- | --- | --- |
| Repository mind map | What parts of this small project exist? | Group discovered APIs, modules, data stores, and external dependencies. Select a branch to focus on one feature; show unsupported areas. |
| API flow graph | How does this request move through code? | Show route, handler, resolvable calls, data access, and response as a bounded path. Each node opens file and line; each edge shows relationship, confidence, and provenance. |
| Data-flow view | Where does this value come from and where is it used? | Show statically supported input, transformation, database read/write, and response links. Mark unresolved data movement rather than inventing it. |
| Runtime trace waterfall | What actually ran and how long did it take? | Show parent-child spans, request and database durations, errors, and source links only where mapping is reliable. Available only for an approved instrumented target. |
| Experiment charts | What changed under load or a fault? | Plot configured and achieved load, throughput, p50/p95/p99 latency, errors, and resource or database metrics with units, sample counts, and scenario context. |
| Comparison view | Did a proposed change help? | Align baseline and rerun by revision, target environment, workload, and metric; show differences and missing comparability conditions. |

## Main interaction

1. Select a project revision and an API or feature. Open its focused graph, with the relevant branch of the repository mind map highlighted.
2. Select a node or edge. Open its source excerpt, file and line, analyzer confidence, and a plain-language AI explanation in a side panel.
3. Ask a follow-up question about that selection. The answer cites the same revision's evidence and can highlight supporting nodes or source ranges.
4. When runtime evidence exists, switch to the observed trace or overlay verified span links. Keep inferred calls visible as inferred, even if no matching span was recorded.
5. If a measured issue exists, open the related trace, chart, finding, and testable improvement idea. A saved rerun enables before/after comparison.

The initial useful slice needs the API flow graph, source panel, and source-grounded AI questions. Repository mind maps and data-flow views can expand the same graph contract. Runtime waterfalls and experiment charts follow when their data sources are implemented.

## Evidence and readability rules

- Static analysis, runtime observation, and AI hypothesis are distinct visual layers with a text label as well as color or line style. A source edge never becomes an observed edge merely because it appears near a trace.
- Every shown node or relationship has an evidence link or a clear `unresolved`/`unsupported` state. AI-generated summaries point to evidence; AI does not add unverified graph edges.
- Show one endpoint or bounded neighborhood by default. Support expand, collapse, filter by node or edge type, search, zoom, fit-to-view, and breadcrumbs for larger projects.
- Preserve project, revision, analysis run, and trace or experiment context while navigating. Avoid comparing measurements from different targets or scenarios without a visible warning.
- Provide a keyboard-accessible list or step view alongside graph canvases so the flow remains understandable without spatial navigation.
- Keep timings, units, sample counts, and source-mapping uncertainty visible. Never fabricate query durations or bottlenecks from source-only analysis.

## Data contract and implementation order

Render the first graph from the versioned intermediate representation (IR), using entity IDs, relationship types, source ranges, confidence, and provenance. Keep layout coordinates and collapsed UI state separate from analysis facts. Runtime span links refer to IR entity IDs only when verified; traces and charts remain separate records. A future language analyzer should emit the same IR rather than requiring a new visualization model.

Implement in this order: focused FastAPI endpoint graph and source selection; AI explanation tied to selected evidence; repository mind map and data-flow refinements; trace waterfall and verified graph links; experiment charts and before/after comparison. Each view needs a known fixture, expected nodes or measurements, and visible empty and unsupported states.
