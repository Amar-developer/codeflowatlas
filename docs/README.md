# CodeFlowAtlas documentation

Start with the [complete specification](project-specification.md) for the full product idea. The focused files below make individual decisions easier to find. These files describe intended behavior and do not imply implementation status.

The [developer guide](developer-guide.md) connects the product requirements to proposed module boundaries, data and API contracts, security checks, test gates, and implementation order.

## Product

- [Vision](product/vision.md)
- [Scope and boundaries](product/scope.md)
- [User journeys](product/user-journeys.md)
- [Golden demonstration flow](product/golden-flow.md)

## Architecture and contracts

- [System architecture](architecture/system-architecture.md)
- [Architecture evolution](architecture/architecture-evolution.md)
- [Repository import and analysis](analysis/repository-import-and-analysis.md)
- [Frontend and backend framework support roadmap](analysis/framework-support-roadmap.md)
- [Intermediate representation](analysis/intermediate-representation.md)
- [API catalog and interfaces](api/api-catalog-and-interfaces.md)
- [Proposed HTTP API](api/http-api.md)
- [Data and events](data/data-and-events.md)
- [Proposed database model](data/database-model.md)
- [Events and Redis](data/events-and-redis.md)

## Runtime and user experience

- [Tracing and visualization](runtime/tracing-and-visualization.md)
- [Platform observability](runtime/observability.md)
- [Traffic, edge cases, and failures](experiments/traffic-edge-cases-and-failures.md)
- [Findings and AI assistant](ai/findings-and-assistant.md)
- [Frontend experience](frontend/frontend-experience.md)
- [Visualization system](frontend/visualization-system.md)

## Safety, quality, and delivery

- [Security and trust boundaries](security/security-and-trust-boundaries.md)
- [Quality and verification](testing/quality-and-verification.md)
- [Delivery sequence](delivery/delivery-sequence.md)
- [Functionality and implementation flow](delivery/functionality-and-implementation-flow.md)
- [Acceptance criteria](delivery/acceptance-criteria.md)
- [Deployment and CI](deployment/deployment-and-ci.md)
- [Open design decisions](decisions/open-design-decisions.md)
- [Architecture decision record template](decisions/ADR_TEMPLATE.md)
- [Initial API and database decision](decisions/ADR-0001-api-database-container-foundation.md)
- [Synthetic runtime and AI test bot decision](decisions/ADR-0005-synthetic-runtime-and-ai-test-bot.md)
- [Full-stack framework progression decision](decisions/ADR-0006-full-stack-framework-progression.md)

## Engineering context

- [Engineering concepts](learning/engineering-concepts.md)
- [Interview and resume evidence](learning/interview-and-resume.md)

For a compact handoff to a coding assistant, see [AI_CONTEXT.md](../AI_CONTEXT.md).
