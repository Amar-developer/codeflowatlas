# Runtime tracing and visualization

The supported target application exports OpenTelemetry spans for inbound HTTP requests and instrumented downstream operations such as database, Redis, messaging, and external HTTP. A span contains trace ID, span ID, parent span ID, service and operation names, timestamps, duration, status, error details, and selected sanitized attributes. Trace collection is the source of truth for observed timings.

The trace explorer presents a request timeline, waterfall, error markers, service map, and links to code where mapping is supported. An auto-instrumented database span may identify a query and service without an exact source line; the UI must say so. Span retention and sampling are explicit. Avoid storing secrets, personal data, full request bodies, or unbounded SQL parameters in span attributes.
