# ADR 0003 SQLAlchemy, Psycopg, and Alembic database layer

## Status

Accepted. Supersedes the temporary direct-driver readiness-query choice in ADR 0001.

## Context

The foundation API used a direct PostgreSQL driver for a single readiness query. Authentication and later project records require a consistent model, session, and migration pattern. The user selected SQLAlchemy and Alembic for the project and requested one database-driver stack.

## Decision

Use SQLAlchemy's async ORM and session API with the Psycopg 3 async dialect for PostgreSQL. Build one async engine during FastAPI startup, share its session factory through dependency injection, and dispose of the engine during shutdown. The readiness endpoint checks the same engine with `SELECT 1`. Use Alembic's async environment for schema migrations. Keep model metadata in one declarative base and import model modules before autogeneration. Pin direct package dependencies.

## Consequences

Database access and migrations share one SQLAlchemy model contract. The API requires a Psycopg driver package in addition to SQLAlchemy and Alembic. The existing auth model and route placeholders do not create tables until a reviewed migration is added. Do not use `Base.metadata.create_all()` at API startup; apply Alembic revisions deliberately.

## Verification

The change is checked by static compilation, Alembic configuration discovery, and a Compose configuration check. Runtime database readiness must be rechecked after the user installs the new pinned dependencies and rebuilds the API image.
