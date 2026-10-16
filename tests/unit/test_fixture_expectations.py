"""Keep fixture expectations in sync with fixture source and the IR vocabulary."""

import json
from pathlib import Path

import pytest

from cfa_ir import IR_SCHEMA_VERSION, Confidence, EntityType, RelationType


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "fastapi-basic"
EXPECTED = json.loads((FIXTURE / "expected-graph.json").read_text())


def _source_sites(node):
    if isinstance(node, dict):
        if {"path", "line", "text"} <= node.keys():
            yield node
        for value in node.values():
            yield from _source_sites(value)
    elif isinstance(node, list):
        for item in node:
            yield from _source_sites(item)


SITES = list(_source_sites(EXPECTED))


def test_expectations_target_current_ir_schema():
    assert EXPECTED["ir_schema_version"] == IR_SCHEMA_VERSION


@pytest.mark.parametrize("site", SITES, ids=lambda s: f'{s["path"]}:{s["line"]}')
def test_expected_source_site_matches_fixture(site):
    lines = (FIXTURE / site["path"]).read_text().splitlines()

    assert site["line"] <= len(lines), f'{site["path"]} has only {len(lines)} lines'
    assert site["text"] in lines[site["line"] - 1]


def test_expectations_use_ir_vocabulary():
    for edge in EXPECTED["edges"] + EXPECTED["unresolved_edges"] + EXPECTED["absent_edges"]:
        RelationType(edge["type"])
    for edge in EXPECTED["edges"] + EXPECTED["unresolved_edges"]:
        Confidence(edge["confidence"])
    for item in EXPECTED["endpoints"] + EXPECTED["entities"]:
        EntityType(item["id"].split(":", 1)[0])


def test_unresolved_edges_have_no_target():
    for edge in EXPECTED["unresolved_edges"]:
        assert "target" not in edge
        assert edge["confidence"] == "low"


def test_absent_edges_do_not_contradict_expected_edges():
    expected = {(e["type"], e["source"], e["target"]) for e in EXPECTED["edges"]}
    for edge in EXPECTED["absent_edges"]:
        assert (edge["type"], edge["source"], edge["target"]) not in expected