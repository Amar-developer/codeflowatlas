# System architecture

The starting architecture is a modular FastAPI application with clear repository, analysis, graph, trace, experiment, finding, and AI modules; a Next.js frontend; and one or more background workers for expensive or isolated jobs. PostgreSQL is the durable application store. Redis may hold short-lived job state, rate limits, and WebSocket fan-out. A trace backend stores high-volume raw telemetry; PostgreSQL stores searchable trace summaries and links. Object storage is appropriate for repository archives and large artifacts when local storage is insufficient.

The frontend communicates through a stable API/BFF boundary. Analysis, traffic, and AI work can move to independently scaled workers without changing the product contract. Kafka is a later event transport when durable high-volume streams, independent consumers, or replay justify its cost. A local queue and transactional job records are adequate for the initial workflow. The system should document any transition to Kafka, including idempotency, retry, dead-letter handling, ordering assumptions, and outbox or equivalent publication guarantees.

### Logical flow

```text
Next.js UI → FastAPI API/BFF → PostgreSQL
                         → analysis worker → IR and graph
                         → trace ingestion → trace backend
                         → traffic/failure worker → isolated target
                         → findings engine → AI explanation service
```

OpenTelemetry collects traces, Prometheus-compatible metrics describe platform and experiment health, and structured logs connect jobs to project, revision, and trace IDs. WebSocket or server-sent updates report job progress; polling remains a fallback.
