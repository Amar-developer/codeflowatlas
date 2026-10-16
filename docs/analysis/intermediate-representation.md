# Common intermediate representation

The IR is the contract between language analyzers and the rest of CodeFlowAtlas. Each entity has a stable ID scoped to a repository revision, type, display name, qualified name where available, source location, analyzer version, and properties. Suggested types are Repository, File, Module, Class, Function, APIEndpoint, Database, Table, Cache, Queue, Topic, ExternalService, Middleware, Worker, and Test.

Each directed edge has source and target IDs, relationship type, source location, confidence (`exact`, `high`, `medium`, `low`), provenance, and analyzer version. Suggested relationships are CONTAINS, IMPORTS, CALLS, EXPOSES, READS_FROM, WRITES_TO, PUBLISHES, CONSUMES, DEPENDS_ON, MIDDLEWARE_BEFORE, and TRIGGERS. An edge may be unknown or unresolved; it must not be invented to make a diagram look complete.

For example, `GET /orders → OrderRouter.get_orders → OrderService.list_orders → OrderRepository.find → PostgreSQL` represents an analysis path. Runtime traces may confirm only some steps. Keep static edges and observed span links distinct so the interface can compare them.

The IR schema must be versioned. Graph IDs should remain stable across repeat analysis of the same revision and analyzer version. Adding a language analyzer should require a parser and mapper to the IR, plus fixtures, without changes to generic graph visualization or experiment storage.

For the planned full-stack source flow, extend the versioned contract with frontend concepts such as a page or component, UI action, and HTTP request call site. Keep the request call and backend API endpoint as separate entities so each has its own file and line evidence. A cross-stack static edge requires a resolvable method, normalized path, and base URL or API client configuration; ambiguous or dynamic calls remain unresolved. The exact new entity and edge names require an IR schema decision and fixture tests before implementation. See the [framework support roadmap](framework-support-roadmap.md).
