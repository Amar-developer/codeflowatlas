# Proposed HTTP and event API

These routes are a design contract for implementation planning. They do not claim that handlers exist yet. All project-scoped operations require authentication and authorization. Collection endpoints use pagination, and long-running mutations return a run or job ID with a status URL.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/projects` | Create a project |
| POST | `/projects/{id}/repositories` | Import a validated source revision |
| POST | `/projects/{id}/analysis` | Start static analysis |
| GET | `/projects/{id}/analysis/{run_id}` | Read status, warnings, and summary |
| GET | `/projects/{id}/apis` | List discovered endpoints |
| GET | `/projects/{id}/graph` | Read a filtered graph slice |
| GET | `/projects/{id}/traces` | Search trace summaries |
| GET | `/projects/{id}/findings` | List evidence-backed findings |
| POST | `/projects/{id}/traffic-runs` | Start an approved traffic scenario |
| POST | `/projects/{id}/failure-runs` | Start a bounded fault scenario |
| POST | `/projects/{id}/ai/query` | Request a grounded explanation |
| WS | `/projects/{id}/events` | Stream project job progress |

Requests and responses should use versioned Pydantic schemas. Error responses should include a stable code, human-readable message, request ID, and field errors where applicable. The API must not return filesystem paths, secrets, raw credentials, or another project's records. Progress streams carry job ID, status, sequence number, and sanitized detail; clients must be able to resume with polling.

Endpoint records should expose method, normalized path, handler entity ID, source location, detected framework, confidence, analyzer version, request and response schema references when known, and links to related traces and findings. Unknown fields remain null or absent with a reason; do not fabricate them.
