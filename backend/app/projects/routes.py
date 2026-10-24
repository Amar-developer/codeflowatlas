from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

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
        "created_at": project.created_at.isoformat(),
        "endpoints": [endpoint_payload(project, item) for item in endpoints],
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