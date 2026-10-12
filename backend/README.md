# Backend

`app/main.py` defines the FastAPI application. Its current endpoints are `/health/live` for process liveness and `/health/ready` for a PostgreSQL connectivity check. Dependencies are pinned in `requirements.txt`.

The root Dockerfile builds this service. The root Compose file supplies database settings and waits for PostgreSQL to become healthy.

Repository import, analysis, traces, experiments, findings, and AI routes remain planned. See `../docs/developer-guide.md` before adding those domains.
