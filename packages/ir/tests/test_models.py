import pytest
from pydantic import ValidationError

from cfa_ir import IR_SCHEMA_VERSION, EntityType, IRDocument, RelationType, SourceLocation, edge_id, entity_id

def base_doc() -> dict:
    return {
        "analyzer": {"name": "test", "version": "0"},
        "repository": {"source": "fixture:test", "revision": "abc123"},
        "entities": [
            {
                "id": "function:app.a",
                "type": "function",
                "name": "a",
                "qualified_name": "app.a",
                "location": {"path": "app/a.py", "start_line": 1, "end_line": 2},
            },
            {
                "id": "function:app.b",
                "type": "function",
                "name": "b",
                "qualified_name": "app.b",
                "location": {"path": "app/a.py", "start_line": 4, "end_line": 5},
            },
        ],
        "edges": [
            {
                "id": "calls:function:app.a->function:app.b@app/a.py:2",
                "type": "calls",
                "source_id": "function:app.a",
                "target_id": "function:app.b",
                "confidence": "exact",
                "provenance": "test.rule",
                "location": {"path": "app/a.py", "start_line": 2, "end_line": 2},
            }
        ],
    }


def test_valid_document_round_trips_through_json():
    doc = IRDocument.model_validate(base_doc())

    assert doc.schema_version == IR_SCHEMA_VERSION
    assert doc.edges[0].resolved
    assert IRDocument.model_validate_json(doc.model_dump_json()) == doc


def test_edge_to_unknown_entity_is_rejected():
    data = base_doc()
    data["edges"][0]["target_id"] = "function:app.missing"

    with pytest.raises(ValidationError, match="unknown target_id"):
        IRDocument.model_validate(data)


def test_edge_from_unknown_entity_is_rejected():
    data = base_doc()
    data["edges"][0]["source_id"] = "function:app.missing"

    with pytest.raises(ValidationError, match="unknown source_id"):
        IRDocument.model_validate(data)


def test_duplicate_entity_ids_are_rejected():
    data = base_doc()
    data["entities"].append(data["entities"][0])

    with pytest.raises(ValidationError, match="duplicate entity ids"):
        IRDocument.model_validate(data)


def test_unresolved_edge_keeps_call_site_without_target():
    data = base_doc()
    data["edges"][0] |= {
        "target_id": None,
        "unresolved_reason": "dynamic dispatch through globals()",
        "target_hint": 'globals()[f"send_{channel}"]',
        "confidence": "low",
    }

    edge = IRDocument.model_validate(data).edges[0]

    assert not edge.resolved
    assert edge.location.start_line == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"target_id": None},
        {"unresolved_reason": "both set"},
    ],
    ids=["neither-target-nor-reason", "both-target-and-reason"],
)
def test_edge_needs_exactly_one_of_target_or_reason(changes):
    data = base_doc()
    data["edges"][0] |= changes

    with pytest.raises(ValidationError, match="exactly one of target_id or unresolved_reason"):
        IRDocument.model_validate(data)


@pytest.mark.parametrize("path", ["/etc/passwd", "../outside.py", "app/../../x.py", "app\\a.py", ""])
def test_unsafe_source_paths_are_rejected(path):
    with pytest.raises(ValidationError, match="relative to the repository root"):
        SourceLocation(path=path, start_line=1, end_line=1)


def test_line_range_must_be_ordered():
    with pytest.raises(ValidationError, match="end_line"):
        SourceLocation(path="app/a.py", start_line=5, end_line=2)


def test_endpoint_requires_method_and_path():
    data = base_doc()
    data["entities"].append(
        {"id": "api_endpoint:POST /x", "type": "api_endpoint", "name": "POST /x", "properties": {"method": "POST"}}
    )

    with pytest.raises(ValidationError, match=r"requires properties \['path'\]"):
        IRDocument.model_validate(data)


def test_unknown_fields_are_rejected():
    data = base_doc()
    data["entities"][0]["colour"] = "red"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        IRDocument.model_validate(data)


def test_unsupported_schema_version_is_rejected():
    data = base_doc() | {"schema_version": "9.9.9"}

    with pytest.raises(ValidationError, match="unsupported schema_version"):
        IRDocument.model_validate(data)


def test_ids_are_deterministic():
    location = SourceLocation(path="app/a.py", start_line=2, end_line=2)

    assert entity_id(EntityType.FUNCTION, "app.a") == "function:app.a"
    assert edge_id(RelationType.CALLS, "function:app.a", "function:app.b", location) == (
        "calls:function:app.a->function:app.b@app/a.py:2"
    )
    assert edge_id(RelationType.CALLS, "function:app.a", None) == "calls:function:app.a->?"