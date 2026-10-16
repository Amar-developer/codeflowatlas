# CodeFlowAtlas

CodeFlowAtlas helps students and AI-assisted builders understand the small, real projects they create through interactive visualizations. A user pastes a supported GitHub or Bitbucket repository link, selects an API or feature, and explores a source-linked flow graph or mind map of its route, functions, dependencies, database access, and response. Clicking a step opens its code and evidence; an integrated AI guide explains what it does and answers questions. For a supported runnable target, an AI test bot proposes a reviewable student journey, then a controlled runner executes it against a disposable synthetic database. The same workspace adds trace waterfalls, database timings, replayable issues, and evidence-backed improvement ideas. Controlled load and fault tests add charts and comparisons in an optional system design lab.

The framework roadmap expands source analysis from FastAPI to a frontend action in React or Next.js, its HTTP call, and the matching FastAPI backend flow. Other backend families follow with their own verified capability levels. See the [framework support roadmap](docs/analysis/framework-support-roadmap.md).

**Project status:** The project has a Next.js foundation page, FastAPI health API, PostgreSQL readiness check, Docker Compose stack, and a standalone FastAPI analyzer/IR prototype for a bundled fixture. Authentication models and routes are under development. Repository import, connected graph UI, AI guide and test bot, synthetic runtime, tracing, and experiments remain planned.

## Run the project

From the project root:

```bash
test -f .env || cp .env.example .env
docker compose up --build -d
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
```

Open `http://127.0.0.1:3000` for the frontend and `http://127.0.0.1:8000/docs` for the API documentation. Both health endpoints return `"status":"ok"` when the API and PostgreSQL are healthy. Set a new local password in `.env` before starting. Run `docker compose logs -f web api` to inspect startup, and `docker compose down` to stop the stack while preserving PostgreSQL data.

For live frontend editing in Docker, use `sudo docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build web`. The development override mounts the frontend source and runs Next.js in development mode, so changes to `frontend/app/` appear without rebuilding. Keep the normal Compose command above for the production build. If `WEB_PORT` in `.env` is changed, open that port instead of 3000.

The root [Dockerfile](Dockerfile) builds the API image, [frontend/Dockerfile](frontend/Dockerfile) builds the frontend image, and [docker-compose.yml](docker-compose.yml) starts both with PostgreSQL. The backend uses SQLAlchemy, Psycopg 3, and Alembic for database access and migrations. `.env.example` is the safe configuration template; the working `.env` contains local credentials and is excluded from Git and Docker build context.

The frontend listens on local port 3000 and the API on 8000 by default. If either is occupied, change `WEB_PORT` or `API_PORT` in `.env` and use those ports in the URLs above. PostgreSQL stays on the Compose network and is not published to the host. The production application containers run as non-root users.

### Run the API outside Docker

Create a virtual environment, install `backend/requirements.txt`, then provide `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` before starting `uvicorn app.main:app` from `backend`. A reachable PostgreSQL database is required for `/health/ready`; `/health/live` only checks the API process.

### Run the frontend outside Docker

From `frontend`, run `npm ci` yourself and then `npm run dev`. Use Node.js 20.9 or newer. The UI uses Tailwind CSS v4 through PostCSS. With the API running on your host, set `API_INTERNAL_URL=http://127.0.0.1:8000` and `API_PUBLIC_URL=http://127.0.0.1:8000`; change the port to match `API_PORT` if needed. The Compose setup supplies these URLs automatically.

## Core flow

GitHub or Bitbucket link → pinned source revision → choose an API or feature → interactive flow graph and mind map → inspect code and ask the AI guide → optional disposable synthetic target and reviewed bot journey → measured trace and issue → bounded system design experiment → rerun to check an improvement.

The first useful result is understanding a confusing feature in a small project, even when the repository has no running database. Source-only explanations describe what the code may do and identify unsupported or uncertain paths. Runtime claims, timings, and bottlenecks require an instrumented, approved, isolated target with a validated disposable schema and synthetic records; CodeFlowAtlas never connects to the imported project's original or production database. The AI bot proposes a finite journey for review, and a deterministic runner records actual outcomes. A later load lab can simulate bounded traffic, such as 100 virtual users, and compare a proposed change against measured results. A local runtime lab would need a user-installed runner; a hosted runner is a later option. The current homepage and health checks are only the foundation for this workflow.

## Read first

- [Complete project specification](docs/project-specification.md)
- [Complete developer guide](docs/developer-guide.md)
- [Documentation map](docs/README.md)
- [AI and human handoff context](AI_CONTEXT.md)
- [Product vision](docs/product/vision.md)
- [Scope and boundaries](docs/product/scope.md)
- [Acceptance criteria](docs/delivery/acceptance-criteria.md)
- [Golden demonstration flow](docs/product/golden-flow.md)
- [Functionality and implementation flow](docs/delivery/functionality-and-implementation-flow.md)

## Project layout

| Location | Responsibility |
| --- | --- |
| `frontend` | Next.js interface and its container image |
| `backend` | FastAPI API and Python dependencies |
| `legacy-auth-foundation` | Earlier authentication prototype; preserved separately and not wired into the current API |
| `workers/analyzer` | Safe static analysis jobs |
| `workers/traffic` | Isolated traffic and failure experiments |
| `workers/ai` | Evidence retrieval and grounded explanation jobs |
| `packages/ir` | Versioned language-neutral graph contract |
| `packages/schemas` | Shared API and event schemas |
| `analyzers/python` | Python and FastAPI analysis; later Flask and Django |
| `infra` | Future infrastructure definitions |
| `fixtures` | Supported repository examples and expected graphs |
| `tests` | Unit, integration, and end-to-end verification |
| `docs` | Product, technical, security, and delivery documentation |

## Build order

Foundation → safe import and static analysis → API or feature flow with grounded AI help → controlled runtime tracing → optional experiments and findings → justified extensions.

The first complete demonstration uses an isolated FastAPI fixture. Imported repository code is read as data during static analysis and is never executed on the host.

## Current file structure

```text
codeflowatlas/
├── Dockerfile                 API container image
├── docker-compose.yml        Frontend, API, and PostgreSQL services
├── .env.example              Configuration template
├── .env                      Local ignored configuration
├── .gitignore                Git exclusions
├── .dockerignore             Docker build exclusions
├── backend/
│   ├── app/                  FastAPI application
│   └── requirements.txt      Pinned Python dependencies
├── frontend/
│   ├── app/                  Next.js pages and styles
│   ├── Dockerfile            Frontend container image
│   └── package-lock.json     Locked JavaScript dependencies
├── legacy-auth-foundation/  Earlier authentication prototype
├── analyzers/python/         Standalone Python/FastAPI analyzer prototype
├── workers/                  Planned background workers
├── packages/                 IR prototype and future shared contracts
├── fixtures/                 Bundled FastAPI example and expectations
├── tests/                    Fixture and future integration tests
├── infra/                    Future infrastructure
└── docs/                     Product and developer documentation
```
