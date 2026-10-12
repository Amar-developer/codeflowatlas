# Events and Redis

The initial architecture can use durable job records and a simple queue. Kafka is an optional later transport. If adopted, candidate topics are `analysis.requested`, `analysis.progress`, `analysis.completed`, `trace.received`, `traffic.started`, `traffic.completed`, `failure.started`, `finding.created`, `ai.requested`, and `ai.completed`.

Events need an event ID, schema version, project ID, relevant revision and run IDs, creation time, correlation ID, producer, and payload. Consumers must be idempotent. Specify ordering only within the key where the transport guarantees it. Persist processing status when duplicate delivery matters, and define retries and dead-letter handling. Use a transactional outbox or equivalent when a database change and event publication must stay consistent.

Redis may store short-lived job progress, safe response caches, rate limits, and WebSocket fan-out. Set expiration and invalidation rules. Redis is not the primary system of record and should not be the only place a completed run or finding exists. A cache loss should affect performance or live updates, not erase durable project results.
