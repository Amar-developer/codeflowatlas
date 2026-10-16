"""Deterministic IDs so repeat analysis of one revision yields the same graph."""

from cfa_ir.models import EntityType, RelationType, SourceLocation


UNRESOLVED_TARGET = "?"


def entity_id(entity_type: EntityType, key: str) -> str:
    """key is the qualified name, `METHOD /path` for endpoints, or a table/service name."""
    return f"{entity_type.value}:{key}"


def edge_id(
    relation: RelationType,
    source_id: str,
    target_id: str | None,
    location: SourceLocation | None = None,
) -> str:
    target = target_id or UNRESOLVED_TARGET
    site = f"@{location.path}:{location.start_line}" if location else ""
    return f"{relation.value}:{source_id}->{target}{site}"