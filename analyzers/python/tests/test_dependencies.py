from textwrap import dedent

from cfa_ir import IRDocument, RelationType
from cfa_python_analyzer import analyze


def write(root, path, source):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dedent(source), encoding="utf-8")


def dependencies(document):
    return [edge for edge in document.edges if edge.type is RelationType.DEPENDS_ON]


def test_dependency_chain_and_import_alias(tmp_path):
    write(
        tmp_path,
        "providers.py",
        """\
        def get_session():
            return None
        """,
    )
    write(
        tmp_path,
        "main.py",
        """\
        from typing import Annotated
        from fastapi import Depends as Inject
        from providers import get_session

        def get_service(session=Inject(get_session)):
            return session

        def handler(service: Annotated[object, Inject(get_service)]):
            return service
        """,
    )

    document = analyze(tmp_path)
    found = dependencies(document)

    assert {(edge.source_id, edge.target_id) for edge in found} == {
        (
            "function:main.get_service",
            "function:providers.get_session",
        ),
        (
            "function:main.handler",
            "function:main.get_service",
        ),
    }

    assert {(edge.location.path, edge.location.start_line) for edge in found} == {
        ("main.py", 5),
        ("main.py", 8),
    }

    assert all(edge.confidence.value == "high" for edge in found)
    assert {edge.properties["declaration_kind"] for edge in found} == {
        "default",
        "annotated",
    }

    assert IRDocument.model_validate_json(document.model_dump_json()) == document

    assert analyze(tmp_path).model_dump_json() == document.model_dump_json()


def test_keyword_only_provider_and_implicit_dependency(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from fastapi import Depends

        def provide():
            return None

        def handler(
            *,
            explicit=Depends(dependency=provide),
            implicit=Depends(),
        ):
            return explicit
        """,
    )

    found = {
        edge.properties["parameter"]: edge for edge in dependencies(analyze(tmp_path))
    }

    assert found["explicit"].target_id == "function:main.provide"

    assert found["implicit"].target_id is None
    assert found["implicit"].unresolved_reason
    assert found["implicit"].confidence.value == "low"


def test_unrelated_depends_name_is_not_fastapi(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        def Depends(value):
            return value

        def provide():
            return None

        def handler(value=Depends(provide)):
            return value
        """,
    )

    assert dependencies(analyze(tmp_path)) == []


def test_shadowed_depends_import_is_not_assumed(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from fastapi import Depends

        Depends = None

        def provide():
            return None

        def handler(value=Depends(provide)):
            return value
        """,
    )

    assert dependencies(analyze(tmp_path)) == []
