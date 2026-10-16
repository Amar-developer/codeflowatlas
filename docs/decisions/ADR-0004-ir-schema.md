# ADR 0004 IR schema as Pydantic models

## Status

Accepted.

## Context

The analyzer, backend, and frontend need one graph contract (specification section 6). It must carry confidence, provenance, and source locations, represent unresolved relationships without inventing targets, and reject unsafe paths from untrusted repositories.

## Decision

Define IR schema `0.1.0` as Pydantic v2 models in `packages/ir` (`cfa_ir`). An `IRDocument` validates unique IDs, edge references, and that each edge has exactly one of `target_id` or `unresolved_reason`. IDs are deterministic strings derived from entity type and qualified name. Only entity and relationship types needed by the `fastapi-basic` fixture are included.

## Alternatives considered

- Hand-written JSON Schema first: no runtime validation in Python without a second library, and harder to keep in sync.
- Hashed IDs: stable but unreadable in tests and fixture expectations.
- A placeholder "unknown" entity for unresolved targets: makes unresolved calls look like real nodes.

## Consequences

Analyzers and the backend share validation. A JSON Schema for the frontend can be exported with `IRDocument.model_json_schema()`. New entity or relationship types require a schema version bump and a fixture that uses them.

## Verification

`pytest packages/ir` covers valid round-trip, dangling references, duplicate IDs, unresolved edges, unsafe paths, endpoint requirements, unknown fields, and version checks.