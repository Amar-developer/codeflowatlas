# Golden demonstration flow

The strongest CodeFlowAtlas demonstration is one reproducible experiment on an isolated FastAPI commerce fixture. It connects source analysis to observed behavior without treating one as proof of the other.

1. Import a pinned fixture revision and record its content fingerprint.
2. Detect Python and FastAPI. Start a static analysis run without executing fixture code.
3. Discover `POST /checkout`, its handler, and resolvable calls to inventory, payment, and order persistence. Mark unresolved or inferred edges with confidence and provenance.
4. Open the endpoint page, graph path, and exact source locations.
5. Launch the instrumented fixture in an isolated target environment and send a baseline request.
6. Display its OpenTelemetry waterfall, statuses, dependencies, and source links where reliable mapping exists.
7. Run a saved baseline traffic scenario, then a saved stress scenario against the same target revision and environment limits.
8. Compare throughput, latency percentiles, errors, and dependency metrics with sample sizes.
9. Inject one bounded dependency delay, rerun the scenario, and show its effect in traces and metrics.
10. Generate a deterministic finding that cites the relevant spans and metric samples.
11. Ask the AI assistant to explain the finding. The answer separates observation, inference, and unknowns and links to the cited evidence.
12. Rerun the saved experiment and compare results. Differences should be visible, not silently presented as identical.

The flow is complete when another developer can repeat it using the documented fixture, environment, scenario definitions, and expected graph assertions.
