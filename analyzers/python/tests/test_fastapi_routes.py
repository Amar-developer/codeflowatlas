import json
from pathlib import Path

import pytest

from cfa_ir import EntityType, IRDocument, RelationType
from cfa_python_analyzer import analyze


FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "fastapi-basic"
EXPECTED = json.loads((FIXTURE / "expected-graph.json").read_text())
EXPECTED_EXPOSES = [edge for edge in EXPECTED["edges"] if edge["type"] == "exposes"]


@pytest.fixture(scope="module")
def doc() -> IRDocument:
    return analyze(FIXTURE, source="fixture:fastapi-basic")


def _entity(doc: IRDocument, entity_id: str):
    return next((entity for entity in doc.entities if entity.id == entity_id), None)


def test_discovers_exactly_the_expected_endpoints(doc):
    found = {entity.id for entity in doc.entities if entity.type is EntityType.API_ENDPOINT}

    assert found == {endpoint["id"] for endpoint in EXPECTED["endpoints"]}


@pytest.mark.parametrize("expected", EXPECTED["endpoints"], ids=lambda e: e["id"])
def test_endpoint_details_match_expectations(doc, expected):
    endpoint = _entity(doc, expected["id"])
    handler = _entity(doc, expected["handler"])

    assert endpoint.properties["method"] == expected["method"]
    assert endpoint.properties["path"] == expected["path"]
    assert endpoint.properties["handler"] == expected["handler"]
    assert endpoint.properties["request_model"] == expected["request_model"]
    assert endpoint.properties["response_model"] == expected["response_model"]
    assert endpoint.properties["status_code"] == expected["status_code"]
    assert (endpoint.location.path, endpoint.location.start_line) == (expected["site"]["path"], expected["site"]["line"])
    assert (handler.location.path, handler.location.start_line) == (
        expected["handler_site"]["path"],
        expected["handler_site"]["line"],
    )


@pytest.mark.parametrize("expected", EXPECTED_EXPOSES, ids=lambda e: e["source"])
def test_exposes_edges_match_expectations(doc, expected):
    matches = [
        edge
        for edge in doc.edges
        if edge.type is RelationType.EXPOSES and edge.source_id == expected["source"] and edge.target_id == expected["target"]
    ]

    assert len(matches) == 1
    edge = matches[0]
    assert edge.confidence == expected["confidence"]
    assert (edge.location.path, edge.location.start_line) == (expected["site"]["path"], expected["site"]["line"])


def test_non_python_files_are_reported_as_skipped(doc):
    skipped = {item.path for item in doc.skipped_files}

    assert set(EXPECTED["skipped_files_include"]) <= skipped


def test_fixture_produces_no_warnings(doc):
    assert doc.warnings == []


def test_output_is_deterministic(doc):
    again = analyze(FIXTURE, source="fixture:fastapi-basic")

    assert again.model_dump_json() == doc.model_dump_json()


def test_output_round_trips_through_ir_validation(doc):
    assert IRDocument.model_validate_json(doc.model_dump_json()) == doc