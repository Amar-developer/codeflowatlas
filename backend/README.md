# Backend

`app/main.py` defines the FastAPI application. Its current endpoints are `/health/live` for process liveness and `/health/ready` for a PostgreSQL connectivity check. `app/db.py` provides the SQLAlchemy async engine and per-request sessions; Psycopg 3 is the PostgreSQL driver. Dependencies are pinned in `requirements.txt`.

The root Dockerfile builds this service and includes the Alembic configuration and migration directory. The root Compose file supplies database settings and waits for PostgreSQL to become healthy. Run Alembic from this directory locally with the database environment variables set, or from the API container with `alembic -c /app/alembic.ini upgrade head`. Review generated revisions before applying them. The auth model and route files are still placeholders, so no auth-table migration exists yet.

Repository import, analysis, traces, experiments, findings, and AI routes remain planned. See `../docs/developer-guide.md` before adding those domains.
