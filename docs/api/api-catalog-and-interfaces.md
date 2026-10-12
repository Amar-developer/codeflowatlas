# API catalog and application interfaces

The endpoint record includes HTTP method, normalized path, handler entity, file and line, framework, auth indicators, request and response schema references, downstream graph links, confidence, and analysis warnings. The detail view can attach recent traces, latency and error summaries, and relevant scenarios when those records exist.

Representative product APIs include project and repository creation, starting and checking analysis, listing endpoints and graph slices, querying traces and findings, creating traffic and failure runs, and asking a grounded AI question. All collection APIs use pagination and project scoping. Mutating APIs validate roles and return consistent errors. Long-running operations return a job or run ID immediately, with progress events and a polling endpoint.
