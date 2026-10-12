# User journeys

### Repository understanding

The user creates a project, imports a pinned revision, and starts analysis. The UI shows progress, detected language and framework, warnings, discovered endpoints, and the graph. Selecting `POST /checkout` reveals its handler, source location, request and response models when resolvable, authentication indicators, downstream calls, and confidence for each relationship. Clicking a node opens the relevant source line.

### Runtime diagnosis

The user launches a supported example target with tracing, sends a request, and opens the waterfall. The trace contains timing, status, errors, and parent-child relationships. Source mapping is shown only when instrumentation or reliable metadata identifies a file, function, or entity. The user can compare trace evidence with the static graph and see where they differ.

### Controlled experiment

The user selects an isolated target, records a baseline, runs a repeatable load profile, then injects a supported delay or failure. CodeFlowAtlas retains the scenario definition, target revision, environment label, metrics, traces, and findings. The user can rerun the same configuration and compare p50, p95, p99, throughput, and error rate.

### Evidence-grounded explanation

The user asks why the endpoint slowed down. The assistant retrieves the relevant endpoint, code nodes, traces, metrics, and findings. Its response separates observed facts, likely explanations, unknowns, and suggested next checks. Each factual claim points to a source, span, metric series, or finding ID.
