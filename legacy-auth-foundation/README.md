# Earlier authentication prototype

This folder preserves the FastAPI authentication and RBAC prototype from the repository's original commit. It is **not connected** to the CodeFlowAtlas API in `../backend/` or to the root Docker Compose stack. Its dependencies, migration files, and application entry point remain here for review and future integration work.

The original Alembic configuration contained a database password. The current configuration requires `DATABASE_URL` from the environment. If that password was ever used outside a disposable local database, rotate it; removing it from this revision does not remove it from Git history.
