# cfa-ir

The CodeFlowAtlas intermediate representation (IR), schema version `0.1.0`. Language analyzers emit an `IRDocument`; the backend stores it and the frontend renders it. Consumers must not depend on Python AST details.

- **Entities:** file, module, class, function, api_endpoint, database, table, external_service. `api_endpoint` requires `method` and `path` properties.
- **Edges:** contains, imports, calls, exposes, reads_from, writes_to, depends_on. Each has a confidence (`exact`, `high`, `medium`, `low`), a provenance rule name, and a call-site location.
- **Unresolved edges** have `unresolved_reason` and an optional `target_hint` instead of `target_id`. Never invent a target.
- **IDs** are deterministic (`function:app.services.inventory.reserve`), so repeat analysis of one revision yields the same graph.
- **Paths** are relative to the repository root and are rejected if absolute or containing `..`.

Not yet supported: queues, caches, topics, middleware, workers, tests, and their relationships. Add them with a fixture that needs them and a schema version bump.

Run the tests from the repository root:

    pip install -e packages/ir pytest==9.1.1
    pytest packages/ir