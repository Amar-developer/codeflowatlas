# Frontend and backend framework support roadmap

CodeFlowAtlas is a full-stack code understanding product. A learner should eventually be able to choose a user action or API and follow a supported path from a frontend page or component, through an HTTP call or server handler, to backend functions, data access, and response handling. This is a product goal, not a claim that every repository or framework works today. The CodeFlowAtlas application's own Next.js/FastAPI stack is separate from the frameworks it analyzes in imported projects.

## Capability levels

Report support by framework and capability, not as one yes/no label:

1. **Detected:** identify files and framework with evidence.
2. **Catalogued:** list supported pages, UI actions, or backend endpoints with source locations.
3. **Source flow:** connect resolvable components, event handlers, client requests, server handlers, service calls, and data access through the versioned IR. Mark dynamic or missing links unresolved.
4. **Observed flow:** add runtime spans or browser/request evidence for a supported isolated target with synthetic data. Source paths do not become observed paths without telemetry.
5. **Test lab:** run a reviewed AI-proposed journey and bounded load or fault scenario on that same disposable target.

Every UI and API response must show the achieved level for each repository and framework, warnings, unsupported syntax, and analyzer version. A repository may support a frontend source flow but have no runnable backend, or vice versa.

## Planned progression

| Step | Imported-project targets | First evidence-backed result |
| --- | --- | --- |
| Current prototype | Python/FastAPI backend | Standalone fixture route discovery and route-to-handler IR edges; product API and UI integration remain planned. |
| First full product path | Python/FastAPI backend | Searchable API catalog, selected endpoint graph, source lines, and grounded explanation. |
| First full-stack path | JavaScript/TypeScript React and Next.js frontend calling a FastAPI backend | Selected page or action → event/data-loading code → supported `fetch` or Axios call → matching FastAPI route → backend flow. |
| Second backend family | JavaScript/TypeScript Express; evaluate NestJS with separate fixtures | Route/controller → middleware or dependency → service/data flow; connect to a supported React/Next.js call when the HTTP contract matches. |
| Further supported shapes | Python Flask and Django, then other demanded frameworks | Add one framework at a time with fixture expectations and clearly stated limits. Java/Spring and Go frameworks remain candidates, not commitments. |

Next.js needs separate treatment for browser Client Components, Server Components, and Route Handlers because request and data-loading code can run in different places. React without a framework needs explicit routing configuration. For a cross-stack static link, match normalized HTTP method and path plus a resolvable base URL or API client configuration. Preserve the frontend call site and backend route site as distinct evidence. Do not guess a match when URLs are constructed dynamically, routed through unknown proxies, or selected at runtime; record an unresolved edge and an explanation. Observed browser/network traces may later establish a separate runtime link.

## Analyzer contract and verification

Each language/framework analyzer maps its own syntax into the same versioned IR and records source locations, confidence, provenance, and unresolved cases. The graph UI queries IR and does not parse framework-specific source itself. Add fixture pairs for each newly supported combination, including successful calls, unmatched calls, dynamic URLs, errors, authentication, and frontend-only/backend-only cases. Check that a UI action reaches the expected endpoint when statically resolvable and that unsupported paths stay visibly incomplete. Do not call a framework supported until its fixture, API contract, graph view, and limitation documentation pass together.

Runtime instrumentation and the AI test bot are separate capability gates. A framework can have useful source analysis without a runnable target, synthetic database, or load support. New runners must use the same disposable-data, approved-target, bounded-action policy as the FastAPI fixture.
