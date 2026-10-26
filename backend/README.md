# Backend

`app/main.py` defines the FastAPI application. Its current endpoints are `/health/live` for process liveness and `/health/ready` for a PostgreSQL connectivity check. `app/db.py` provides the SQLAlchemy async engine and per-request sessions; Psycopg 3 is the PostgreSQL driver. Dependencies are pinned in `requirements.txt`.

The root Dockerfile includes Alembic and the authentication and project migrations. Compose runs a single `migrate` service after PostgreSQL is healthy; the API and authentication cleanup wait for it to complete successfully. Migration failures block startup; inspect `docker compose logs migrate`. The development override mounts revisions read-only into the migration service.

Outside Compose, set the database environment variables and run `alembic upgrade head` from this directory before starting the API or cleanup. Readiness checks connectivity only, so a successful response does not prove tables exist. Existing volumes are upgraded without resetting data. Manually altered or incorrectly stamped schemas require inspection rather than `alembic stamp head`. Review generated revisions before applying them.

Repository import, analysis, traces, experiments, findings, and AI routes remain planned. See `../docs/developer-guide.md` before adding those domains.

New repository imports store the validated, versioned analyzer IR in
`projects.static_graph` alongside the pinned commit and analyzer version.
This contains static source relationships, not runtime observations.
Existing imports have no saved graph until imported again. The graph is
not yet exposed through the API or rendered in the frontend.

Project detail responses include a static graph summary with schema version,
entity count, relationship count, and unresolved relationship count.
Imports without a saved graph return `graph_summary: null`.

`GET /projects/{project_id}/endpoints/{endpoint_id}/flow` returns an
owner-authorized static graph slice containing the endpoint, its handler,
and up to 100 direct handler relationships. It preserves confidence,
source locations, provenance, and unresolved targets. Results identify
the pinned commit and analyzer version and report truncation. This is
not recursive call traversal or runtime evidence.

The endpoint inspector displays a static relationship list fetched from
the owner-authorized flow API. It shows source locations, confidence,
analyzer provenance, unresolved targets, and truncation. The list covers
the route-to-handler link and direct handler relationships, not runtime
execution order or recursive call traversal.
