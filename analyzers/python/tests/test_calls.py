from textwrap import dedent

from cfa_ir import IRDocument, RelationType
from cfa_python_analyzer import analyze


def write(root, path, source):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dedent(source), encoding="utf-8")


def call_edges(document):
    return [edge for edge in document.edges if edge.type is RelationType.CALLS]


def test_import_aliases_and_call_sites(tmp_path):
    write(
        tmp_path,
        "service.py",
        """\
        def save():
            return 1
        """,
    )
    write(
        tmp_path,
        "main.py",
        """\
        import service as storage
        from service import save as persist

        def handler():
            storage.save()
            persist()
        """,
    )

    document = analyze(tmp_path)
    edges = call_edges(document)

    assert len(edges) == 2
    assert {edge.source_id for edge in edges} == {"function:main.handler"}
    assert {edge.target_id for edge in edges} == {"function:service.save"}
    assert {edge.confidence.value for edge in edges} == {"high"}
    assert {(edge.location.path, edge.location.start_line) for edge in edges} == {
        ("main.py", 5),
        ("main.py", 6),
    }

    assert IRDocument.model_validate_json(document.model_dump_json()) == document


def test_parameters_and_dynamic_calls_stay_unresolved(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def save():
            pass

        def handler(save, service):
            save()
            service.execute()
        """,
    )

    edges = call_edges(analyze(tmp_path))

    assert len(edges) == 2
    assert all(edge.target_id is None for edge in edges)
    assert all(edge.unresolved_reason for edge in edges)
    assert {edge.target_hint for edge in edges} == {
        "save",
        "service.execute",
    }


def test_reassigned_module_function_stays_unresolved(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def save():
            pass

        save = None

        def handler():
            save()
        """,
    )

    edges = call_edges(analyze(tmp_path))

    assert len(edges) == 1
    assert edges[0].target_id is None


def test_recursion_and_multiple_calls_on_one_line(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def recurse():
            recurse(); recurse()
        """,
    )

    document = analyze(tmp_path)
    edges = call_edges(document)

    assert len(edges) == 2
    assert len({edge.id for edge in edges}) == 2
    assert all(edge.target_id == "function:main.recurse" for edge in edges)

    again = analyze(tmp_path)
    assert again.model_dump_json() == document.model_dump_json()


def test_nested_scope_calls_are_not_attributed_to_outer(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def save():
            pass

        def outer():
            def inner():
                save()
            return inner
        """,
    )

    document = analyze(tmp_path)

    assert call_edges(document) == []
    assert any(warning.code == "call_scope_skipped" for warning in document.warnings)


def test_target_code_is_not_executed(tmp_path):
    marker = tmp_path / "executed.txt"

    write(
        tmp_path,
        "main.py",
        f"""\
        from pathlib import Path

        Path({str(marker)!r}).write_text("executed")

        def save():
            pass

        def handler():
            save()
        """,
    )

    document = analyze(tmp_path)

    assert not marker.exists()
    assert any(edge.target_id == "function:main.save" for edge in call_edges(document))


def test_call_classification_preserves_unresolved_targets(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from unavailable_package import send as deliver

        def save():
            pass

        def handler(db, callback):
            save()
            deliver()
            db.execute()
            callback()
            callback()()
        """,
    )

    edges = call_edges(analyze(tmp_path))

    classified = {edge.target_hint: edge for edge in edges}

    assert classified["save"].properties["call_category"] == ("project_function")
    assert classified["save"].target_id == "function:main.save"

    expected_unresolved = {
        "deliver": "imported_callable",
        "db.execute": "attribute_call",
        "callback": "dynamic_call",
        "<dynamic callable>": "dynamic_call",
    }

    for hint, category in expected_unresolved.items():
        edge = classified[hint]
        assert edge.properties["call_category"] == category
        assert edge.properties["classification_reason"]
        assert edge.target_id is None
        assert edge.unresolved_reason
        assert edge.confidence.value == "low"


def test_shadowed_import_is_not_classified_as_imported(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        import unavailable_package as client

        def handler(client):
            client.send()
        """,
    )

    edge = call_edges(analyze(tmp_path))[0]

    assert edge.properties["call_category"] == "attribute_call"
    assert edge.target_id is None


def test_rebound_callable_remains_ambiguous(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from unavailable_package import send

        send = None

        def handler():
            send()
        """,
    )

    edge = call_edges(analyze(tmp_path))[0]

    assert edge.properties["call_category"] == "unresolved_callable"
    assert edge.target_id is None


def test_nested_calls_have_distinct_edges(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def handler(callback):
            callback()()
        """,
    )

    edges = call_edges(analyze(tmp_path))

    assert len(edges) == 2
    assert len({edge.id for edge in edges}) == 2
    assert {edge.target_hint for edge in edges} == {
        "callback",
        "<dynamic callable>",
    }
    assert all(edge.target_id is None for edge in edges)
