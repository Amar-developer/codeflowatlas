# Data and event design

Core relational records are users, projects, repositories, revisions, analysis runs, files, code entities and edges, API endpoints, findings, trace sessions and summaries, experiment scenarios and runs, architecture models, AI conversations, and knowledge chunks. Index by project and revision, endpoint method/path, trace ID, timestamp, and finding severity as needed. Raw high-volume spans and traffic samples can live in dedicated telemetry storage with stable references from PostgreSQL.

If the architecture adopts Kafka, candidate events include analysis requested/progress/completed, trace received, traffic started/completed, failure started, finding created, and AI requested/completed. Every event needs an ID, schema version, project and revision context where applicable, correlation ID, and idempotent consumer behavior. The database remains the system of record; Redis does not become the source of truth.
