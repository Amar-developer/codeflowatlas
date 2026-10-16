# Golden demonstration flow

The strongest CodeFlowAtlas demonstration begins with a small FastAPI commerce fixture published as a supported public GitHub or Bitbucket repository. A student should understand its `POST /checkout` flow with source-linked AI help before the application is run. An approved isolated target later adds observed behavior and experiments without treating source analysis as proof of execution.

1. Paste the fixture repository URL, pin its revision, and record its commit SHA or content fingerprint.
2. Detect Python and FastAPI. Start a static analysis run without executing fixture code.
3. Discover `POST /checkout`, its handler, and resolvable calls to inventory, payment, and order persistence. Show detectable database reads or writes, and mark unresolved or inferred edges with confidence and provenance.
4. Open the endpoint page and walk through route, handler, downstream functions, detectable data access, and response with exact source locations.
5. Ask the AI guide what each step does and where a value comes from. It cites source lines, labels unresolved edges, and does not claim that the code ran. This is the first useful result.
6. Derive the fixture's disposable test schema from its verified models or migrations, create synthetic seed records and test accounts, and launch the instrumented fixture in an isolated target environment. Never connect the fixture to original data.
7. Display its OpenTelemetry waterfall, total request duration, database query count and durations, statuses, dependencies, and source links where reliable mapping exists.
8. Let the AI test bot propose a student journey such as checkout and order lookup. Review its target, allowed actions, synthetic inputs, limits, and expected outcomes; run that approved journey and retain a replayable failure report if a request fails.
9. Ask why one observed request is slow or failed. The AI guide separates observation, inference, and unknowns and links to the cited evidence.
10. In the optional lab, run a saved baseline and bounded 100-concurrent-virtual-user scenario against the same target revision, synthetic dataset, and environment limits.
11. Compare achieved throughput, latency percentiles, errors, database timing, and resource metrics with sample sizes.
12. Inject one bounded dependency delay, rerun the scenario, and show its effect in traces and metrics.
13. Generate a deterministic finding that cites the relevant spans and metric samples.
14. Compare relevant improvement options such as query changes, indexing, or caching, with evidence, tradeoffs, and a testable experiment.
15. Rerun the saved experiment after a controlled change and compare before/after results. Differences should be visible, not silently presented as identical.

The source-learning flow is complete when another student can follow and question the same code path using the documented fixture and expected graph assertions. The deeper runtime and lab flows are complete when another developer can repeat them using the documented environment and scenario definitions.
