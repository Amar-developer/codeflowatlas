# Platform observability

OpenTelemetry carries request and worker traces. Structured JSON logs include request ID, job ID, project ID, revision ID, trace ID, and error code when appropriate, while excluding secrets and sensitive source content. Prometheus-compatible metrics and dashboards show both CodeFlowAtlas health and controlled target behavior.

Suggested platform metrics include analysis duration, files analyzed, analysis failures, queue depth, worker utilization, trace ingestion rate, traffic throughput and error rate, p95 and p99 latency, and AI latency and cost estimates where available. Distinguish platform errors from errors in an imported target. Label measurements with the target revision, environment, and scenario when they are used to compare experiments.

Sampling, retention, and cardinality limits should be decided before ingesting large workloads. A metric or trace is evidence only when its source, collection window, and relevant sample count are known.
