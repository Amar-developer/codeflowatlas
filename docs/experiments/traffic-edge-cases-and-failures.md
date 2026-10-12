# Traffic edge cases and failure experiments

Scenarios define an allowlisted target endpoint, method, payload, virtual users or arrival rate, duration, ramp-up, headers and authentication strategy, success criteria, and environment label. Profiles include smoke, baseline, stress, spike, and soak, but the initial complete workflow needs only a repeatable baseline and one stress profile. k6 is the planned traffic engine. Runs store the exact configuration, target revision, tool version, aggregate metrics, and artifact links.

Metrics include requests per second, throughput, p50/p95/p99 latency, errors, timeouts, CPU and memory, and relevant dependency indicators such as database connections, cache hit ratio, or queue lag. Measurements are meaningful only when the target environment and its resource limits are recorded. CodeFlowAtlas should not promise that an arbitrary target can sustain a specified request rate.

The edge-case engine starts with deterministic inputs derived from resolvable schemas: missing required fields, invalid enum values, nulls, malformed IDs, boundary values, duplicate requests, pagination extremes, wrong content type, and expired tokens when a safe test credential exists. Every case stores expected outcome, actual outcome, trace ID, and verdict.

Failure injection is opt-in and restricted to isolated test targets. The first supported fault can be dependency latency or an HTTP dependency error. Later faults may include database or Redis unavailability, message delay or duplication, connection-pool pressure, and resource pressure. Each run requires a bounded duration, cleanup, environment label, and audit record. The UI must not inject faults into arbitrary external systems.
