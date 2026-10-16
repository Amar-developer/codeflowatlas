# Proposed database model

PostgreSQL is the durable product store. The following entities are planned; migrations and queries should add only the records required by implemented capabilities.

| Domain | Records | Key relationship |
| --- | --- | --- |
| Identity | users, projects, memberships | Memberships scope access to projects |
| Repository | repositories, repository_revisions | Revisions pin source content and fingerprint |
| Analysis | analysis_runs, files, code_entities, code_edges, api_endpoints, analysis_findings | Analyzer output belongs to one revision and run |
| Tracing | trace_sessions, traces, span_summaries | Searchable records link to raw telemetry |
| Experiments | traffic_scenarios, traffic_runs, traffic_samples, failure_scenarios, failure_runs | Runs preserve target revision and exact configuration |
| Synthetic runtime lab | target_runs, synthetic_dataset_versions, test_journeys, journey_runs, journey_steps, issue_reports | Every run ties a validated disposable schema and seed to one revision, reviewed scenario, and measured evidence |
| Explanation | ai_conversations, knowledge_chunks | Chunks and responses are scoped to project and revision |
| Architecture | architecture_models | Model claims identify evidence and provenance |

Use project and revision keys throughout. Candidate indexes include `(project_id, repository_sha)`, entity type and qualified name, endpoint method/path, trace ID, timestamp, and finding severity. High-volume raw spans and traffic samples may live in a telemetry backend; PostgreSQL should retain stable references and searchable summaries. Avoid duplicating an unbounded telemetry stream in relational tables.

Every record that can be shown as evidence needs a stable ID, provenance, and retention behavior. Deleting or changing a repository revision must not silently relabel findings from another revision.

Synthetic dataset records contain generator version, source schema or migration fingerprint, seed, row counts, and disposable target identity, never raw original data. A bot proposal is stored separately from an approved immutable scenario; execution records carry actual requests, assertions, trace IDs, and cleanup status. The CodeFlowAtlas product PostgreSQL database is distinct from every short-lived target database.
