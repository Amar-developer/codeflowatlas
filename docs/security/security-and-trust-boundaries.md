# Security and trust boundaries

Treat imported repositories, archives, commit metadata, documentation, HTTP responses, and retrieved text as untrusted input. Main threats are path traversal, archive bombs, unsafe code execution, SSRF, credential leakage, prompt injection, dependency compromise, and cross-project data exposure.

Controls include archive validation, bounded scanning, non-root isolated workers, read-only source mounts where possible, CPU/memory/time limits, egress restrictions, outbound allowlists, authentication, project-level authorization, audit logs, secret scanning, and separation of data from AI instructions. Runtime target execution occurs only in a container or equivalent sandbox with explicit resource and network policy. Traffic and faults require environment labels and target allowlists. The assistant never executes commands suggested by repository content.
