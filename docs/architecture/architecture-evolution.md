# Architecture evolution

CodeFlowAtlas starts as a modular FastAPI application with a stable frontend API. The domain modules are repository import, analysis, graph, tracing, experiments, findings, and AI. Background workers isolate long-running jobs while keeping the product contract in one deployable system.

The next architecture step is driven by observed pressure. Independent analyzer, traffic, or AI worker pools become useful when their resource profiles differ or queue latency needs separate control. Durable event streaming becomes useful when multiple independent consumers require replay or high-throughput fan-out. A separate service boundary should follow a measured operational or ownership need, not a diagram requirement.

If Kafka is introduced, define event schemas, keys, ordering scope, retries, dead-letter handling, consumer idempotency, and the transaction boundary between PostgreSQL state changes and published events. If the UI presents an architecture pattern, label whether it is an implemented deployment shape, a static inference about an imported repository, or a suggested future design.

The API/BFF remains stable while internal execution changes. Document transitions in architecture decision records and keep the golden flow passing after each transition.
