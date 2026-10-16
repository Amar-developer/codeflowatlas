"""Versioned, language-neutral graph contract between analyzers and the rest of CodeFlowAtlas."""

from collections import Counter
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


IR_SCHEMA_VERSION = "0.1.0"


def _check_repo_path(value: str) -> str:
    """Keep paths relative to the repository root so they cannot point outside it."""
    path = PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError("path must be relative to the repository root, use '/', and not contain '..'")
    return value


RepoPath = Annotated[str, AfterValidator(_check_repo_path)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EntityType(StrEnum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    TABLE = "table"
    EXTERNAL_SERVICE = "external_service"


class RelationType(StrEnum):
    CONTAINS = "contains"
    IMPORTS = "imports"
    CALLS = "calls"
    EXPOSES = "exposes"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    DEPENDS_ON = "depends_on"


class Confidence(StrEnum):
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceLocation(_Model):
    path: RepoPath
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def _lines_in_order(self) -> "SourceLocation":
        if self.end_line < self.start_line:
            raise ValueError("end_line must not be before start_line")
        return self


class Entity(_Model):
    id: str = Field(min_length=1)
    type: EntityType
    name: str = Field(min_length=1)
    qualified_name: str | None = None
    location: SourceLocation | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _endpoint_has_route(self) -> "Entity":
        if self.type is EntityType.API_ENDPOINT:
            missing = {"method", "path"} - self.properties.keys()
            if missing:
                raise ValueError(f"api_endpoint {self.id} requires properties {sorted(missing)}")
        return self


class Edge(_Model):
    """A directed relationship. Unresolved edges keep the source and call site but have no target."""

    id: str = Field(min_length=1)
    type: RelationType
    source_id: str
    target_id: str | None = None
    confidence: Confidence
    provenance: str = Field(min_length=1, description="Analyzer rule that produced this edge")
    location: SourceLocation | None = None
    unresolved_reason: str | None = None
    target_hint: str | None = Field(default=None, description="Source text of an unresolved target")
    properties: dict[str, Any] = Field(default_factory=dict)

    @property
    def resolved(self) -> bool:
        return self.target_id is not None

    @model_validator(mode="after")
    def _target_or_reason(self) -> "Edge":
        if (self.target_id is None) == (self.unresolved_reason is None):
            raise ValueError(f"edge {self.id} needs exactly one of target_id or unresolved_reason")
        return self


class AnalyzerInfo(_Model):
    name: str
    version: str


class RevisionInfo(_Model):
    source: str = Field(description="Canonical repository URL or fixture name")
    revision: str = Field(description="Commit SHA or content fingerprint")


class AnalysisWarning(_Model):
    code: str
    message: str
    location: SourceLocation | None = None


class SkippedFile(_Model):
    path: RepoPath
    reason: str


class IRDocument(_Model):
    schema_version: str = IR_SCHEMA_VERSION
    analyzer: AnalyzerInfo
    repository: RevisionInfo
    entities: list[Entity] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)
    warnings: list[AnalysisWarning] = Field(default_factory=list)
    skipped_files: list[SkippedFile] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent_graph(self) -> "IRDocument":
        if self.schema_version != IR_SCHEMA_VERSION:
            raise ValueError(f"unsupported schema_version {self.schema_version}; expected {IR_SCHEMA_VERSION}")

        for kind, ids in (("entity", [e.id for e in self.entities]), ("edge", [e.id for e in self.edges])):
            duplicates = sorted(i for i, count in Counter(ids).items() if count > 1)
            if duplicates:
                raise ValueError(f"duplicate {kind} ids: {duplicates}")

        known = {entity.id for entity in self.entities}
        for edge in self.edges:
            if edge.source_id not in known:
                raise ValueError(f"edge {edge.id}: unknown source_id {edge.source_id}")
            if edge.target_id is not None and edge.target_id not in known:
                raise ValueError(f"edge {edge.id}: unknown target_id {edge.target_id}")
        return self
    