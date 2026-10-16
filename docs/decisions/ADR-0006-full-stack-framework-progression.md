# ADR-0006: Progress from FastAPI analysis to full-stack framework support

Status: proposed

## Context

CodeFlowAtlas aims to explain a user's feature across frontend and backend source. The current standalone analyzer prototype covers a FastAPI fixture. Adding framework names to a support list would overstate its ability to connect a UI action to a backend route.

## Decision

Finish the FastAPI product path first. Add a paired React or Next.js and FastAPI fixture as the first full-stack source-flow path. Keep client actions, server data loading, and Next.js route handlers distinct. Connect a frontend HTTP call to a backend endpoint only when its method, normalized path, and base URL or API configuration resolve. Record both source locations and unresolved cases in a versioned IR extension. Add Express as the next backend family through a separate adapter and fixtures. Evaluate other frameworks separately. Report detected, catalogued, source-flow, observed-flow, and test-lab capabilities independently.

## Consequences and verification

The graph can show useful partial flows before every framework is runnable. A source-flow claim requires paired fixture expectations, API and graph checks, and documented limits. Runtime observation and lab support require their own isolated target and synthetic-data checks. Any IR schema change needs a migration or compatibility rule for stored analysis runs. See the [framework support roadmap](../analysis/framework-support-roadmap.md) and [acceptance criteria](../delivery/acceptance-criteria.md).
