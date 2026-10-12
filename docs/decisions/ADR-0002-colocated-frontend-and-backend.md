# ADR-0002: Keep frontend and backend in one project

Status: Accepted.

## Context

The foundation already uses one Git repository and one Docker Compose stack. CodeFlowAtlas needs a web entry point while the API, analysis, and experiment workflows are built incrementally. A clear root layout helps developers and coding assistants find the active applications.

## Decision

Keep the Next.js application in `frontend/` and the FastAPI application in `backend/` under the same project root. Keep one root `docker-compose.yml` for web, API, and PostgreSQL. Keep the API's Dockerfile at the root for compatibility with existing commands; keep the web Dockerfile in `frontend/`. Store Python dependencies in `backend/requirements.txt` and JavaScript dependencies and lockfile in `frontend/`.

## Consequences

The three services start together with `docker compose up --build -d`. Web and API use separate containers and ports. PostgreSQL data remains in its existing named volume. Future modules can be added without splitting the repository. The frontend must make server-side requests through the Compose service name and use a host-facing URL for browser links.
