from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.projects.flow import build_flow_slice

from cfa_ir import IRDocument, IR_SCHEMA_VERSION

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.auth import User
from app.models.project import Project, ProjectEndpoint
from app.projects.importer import ImportProblem, import_public_github_repository

router = APIRouter(prefix="/projects", tags=["projects"])


class ImportRequest(BaseModel):
    url: str = Field(min_length=20, max_length=600)


def endpoint_payload(project: Project, endpoint: ProjectEndpoint) -> dict:
    source_url = (
        f"https://github.com/{project.owner_name}/{project.repository_name}"
        f"/blob/{project.commit_sha}/"
        f"{quote(endpoint.source_file, safe='/')}#L{endpoint.source_line}"
    )

    return {
        "id": str(endpoint.id),
        "method": endpoint.method,
        "path": endpoint.path,
        "handler": endpoint.handler,
        "source_file": endpoint.source_file,
        "source_line": endpoint.source_line,
        "source_url": source_url,
        "app_name": endpoint.app_name or "Unknown app",
        "app_file": endpoint.app_file or "Unknown app file",
    }


def project_payload(project: Project, endpoints: list[ProjectEndpoint]) -> dict:
    return {
        "id": str(project.id),
        "name": project.name,
        "repository_url": project.repository_url,
        "commit_sha": project.commit_sha,
        "analyzer_version": project.analyzer_version,
        "warnings": project.warnings,
        "skipped_count": project.skipped_count,
        "graph_summary": graph_summary(project),
        "created_at": project.created_at.isoformat(),
        "endpoints": [endpoint_payload(project, item) for item in endpoints],
    }


def graph_summary(project: Project) -> dict | None:
    graph = project.static_graph

    if graph is None:
        return None

    entities = graph["entities"]
    edges = graph["edges"]

    return {
        "schema_version": graph["schema_version"],
        "entity_count": len(entities),
        "edge_count": len(edges),
        "unresolved_edge_count": sum(
            1 for edge in edges if edge.get("target_id") is None
        ),
    }


@router.post("/import", status_code=201)
async def import_project(
    body: ImportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    try:
        result = await import_public_github_repository(body.url)
    except ImportProblem as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    project = Project(
        owner_id=user.id,
        name=result["repo"],
        repository_url=result["repository_url"],
        owner_name=result["owner"],
        repository_name=result["repo"],
        commit_sha=result["commit_sha"],
        analyzer_version=result["analyzer_version"],
        warnings=result["warnings"],
        skipped_count=result["skipped_count"],
        static_graph=result["static_graph"],
    )

    try:
        db.add(project)
        await db.flush()

        endpoints = [
            ProjectEndpoint(project_id=project.id, **item)
            for item in result["endpoints"]
        ]
        db.add_all(endpoints)
        await db.flush()
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return project_payload(project, endpoints)


@router.get("")
async def list_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == user.id)
        .order_by(Project.created_at.desc())
        .limit(50)
    )

    return [
        {
            "id": str(project.id),
            "name": project.name,
            "repository_url": project.repository_url,
            "commit_sha": project.commit_sha,
            "created_at": project.created_at.isoformat(),
        }
        for project in result.scalars()
    ]


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user.id,
        )
    )
    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    endpoint_result = await db.execute(
        select(ProjectEndpoint)
        .where(ProjectEndpoint.project_id == project.id)
        .order_by(ProjectEndpoint.method, ProjectEndpoint.path)
    )

    return project_payload(project, list(endpoint_result.scalars()))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    result = await db.execute(
        delete(Project)
        .where(
            Project.id == project_id,
            Project.owner_id == user.id,
        )
        .returning(Project.id)
    )

    if result.scalar_one_or_none() is None:
        await db.rollback()
        raise HTTPException(status_code=404, detail="Project not found")

    await db.commit()
    return Response(status_code=204)


@router.get("/{project_id}/endpoints/{endpoint_id}/flow")
async def get_endpoint_flow(
    project_id: UUID,
    endpoint_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    depth: Annotated[int, Query(ge=1, le=3)] = 1,
) -> dict:
    project = await db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user.id,
        )
    )

    if project is None:
        raise HTTPException(404, "Project not found")

    endpoint = await db.scalar(
        select(ProjectEndpoint).where(
            ProjectEndpoint.id == endpoint_id,
            ProjectEndpoint.project_id == project.id,
        )
    )

    if endpoint is None:
        raise HTTPException(404, "Endpoint not found")

    if project.static_graph is None:
        raise HTTPException(
            409,
            "This import has no saved graph. Import the repository again.",
        )

    if project.static_graph.get("schema_version") != IR_SCHEMA_VERSION:
        raise HTTPException(
            409,
            "This saved graph uses an unsupported schema version.",
        )

    try:
        document = IRDocument.model_validate(project.static_graph)
    except ValidationError:
        raise HTTPException(
            409,
            "This saved graph is invalid. Import the repository again.",
        ) from None

    # Match the catalog record to its source-backed graph entity.
    # Method and path alone are insufficient for multi-app repositories.
    matches = [
        entity
        for entity in document.entities
        if entity.type.value == "api_endpoint"
        and entity.location is not None
        and entity.properties.get("method") == endpoint.method
        and entity.properties.get("path") == endpoint.path
        and entity.location.path == endpoint.source_file
        and entity.location.start_line == endpoint.source_line
        and entity.properties.get("app_name") == endpoint.app_name
        and entity.properties.get("app_file") == endpoint.app_file
    ]

    if len(matches) != 1:
        raise HTTPException(
            409,
            "The endpoint cannot be uniquely matched to the saved graph.",
        )

    root = matches[0]
    entities = {entity.id: entity for entity in document.entities}
    handler_id = root.properties.get("handler")

    if not isinstance(handler_id, str) or handler_id not in entities:
        raise HTTPException(
            409,
            "The endpoint has no resolved handler in this saved graph.",
        )

    try:
        sliced = build_flow_slice(
            document.model_dump(mode="json"),
            root.id,
            handler_id,
            depth=depth,
        )
    except ValueError:
        raise HTTPException(
            409,
            "The saved graph cannot produce a valid endpoint flow.",
        ) from None

    def source_url(location: dict | None) -> str | None:
        if location is None:
            return None

        path = quote(location["path"], safe="/")
        start = location["start_line"]
        end = location["end_line"]

        return (
            f"https://github.com/"
            f"{project.owner_name}/{project.repository_name}"
            f"/blob/{project.commit_sha}/{path}"
            f"#L{start}-L{end}"
        )

    for entity in sliced["entities"]:
        entity["source_url"] = source_url(entity.get("location"))

    for relationship in sliced["edges"]:
        relationship["source_url"] = source_url(relationship.get("location"))

    return {
        "project_id": str(project.id),
        "endpoint_id": str(endpoint.id),
        "commit_sha": project.commit_sha,
        "schema_version": document.schema_version,
        "analyzer_version": document.analyzer.version,
        "evidence_kind": "static",
        "scope": "bounded_downstream_relationships",
        "root_id": root.id,
        "handler_id": handler_id,
        "warning_count": len(document.warnings),
        **sliced,
    }
