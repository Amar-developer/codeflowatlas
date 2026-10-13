# ADR 0001 API database and container foundation

## Status

Superseded in its database-access choice by ADR 0003; the container and health-check foundation remains accepted.

## Context

CodeFlowAtlas needs a locally repeatable backend before repository analysis and tracing can be built. The initial product scope calls for Python, FastAPI, PostgreSQL, and containers. The developer guide favors a modular application before distributed services.

## Decision

Use a Python 3.12 FastAPI process in a non-root API container and PostgreSQL 17 in a separate Compose service. Keep PostgreSQL on the internal Compose network. Publish only the API on the host loopback address. Configure database credentials through an ignored `.env` file. Use a liveness endpoint for the process and a readiness endpoint that executes `SELECT 1` against PostgreSQL. Compose waits for the database health check before starting the API.

The first API slice had no persistent product tables. Its initial direct-driver readiness query was temporary; ADR 0003 defines the SQLAlchemy and Alembic database layer.

## Alternatives considered

- A local host installation would make setup vary by machine and would not provide the intended isolated development stack.
- Adding Redis, Kafka, workers, and a frontend immediately would increase setup and debugging cost before their product capabilities exist.
- A full ORM and migration layer was deferred until the first durable domain records are defined.

## Consequences

The project can build and start a small API and database together. A readiness failure is visible as HTTP 503 and an unhealthy API container. Docker and Compose are required to run the documented local stack. Dependency versions are pinned directly in `requirements.txt`; transitive dependency locking and image digest pinning can be added before a production release.

## Verification

The API image built, PostgreSQL became healthy, both health endpoints returned HTTP 200 while PostgreSQL was running, and the readiness endpoint returned HTTP 503 after the test database stopped. The temporary verification stack was removed afterward.
