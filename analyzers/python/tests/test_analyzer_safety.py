import textwrap
from pathlib import Path

from cfa_ir import EntityType
from cfa_python_analyzer import analyze


def write(root: Path, relative: str, source: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(source))


def endpoint_ids(doc) -> set[str]:
    return {entity.id for entity in doc.entities if entity.type is EntityType.API_ENDPOINT}


def test_target_code_is_never_executed(tmp_path):
    marker = tmp_path / "executed.txt"
    write(
        tmp_path,
        "app/main.py",
        f"""
        from pathlib import Path
        Path({str(marker)!r}).write_text("ran")

        from fastapi import FastAPI

        app = FastAPI()

        @app.get("/")
        def root():
            return {{}}
        """,
    )

    doc = analyze(tmp_path)

    assert not marker.exists()
    assert endpoint_ids(doc) == {"api_endpoint:GET /"}


def test_syntax_error_is_reported_and_other_files_are_still_analyzed(tmp_path):
    write(tmp_path, "broken.py", "def oops(:\n")
    write(tmp_path, "ok.py", "def fine():\n    return 1\n")

    doc = analyze(tmp_path)

    assert [(w.code, w.location.path) for w in doc.warnings] == [("parse_error", "broken.py")]
    assert ("broken.py", "syntax error") in {(s.path, s.reason) for s in doc.skipped_files}
    assert any(entity.id == "function:ok.fine" for entity in doc.entities)


def test_symlinks_are_skipped_not_followed(tmp_path):
    outside = tmp_path / "outside"
    repo = tmp_path / "repo"
    write(outside, "secret.py", "def secret():\n    pass\n")
    write(repo, "app.py", "def a():\n    pass\n")
    (repo / "link.py").symlink_to(outside / "secret.py")
    (repo / "linkdir").symlink_to(outside, target_is_directory=True)

    doc = analyze(repo)

    assert not any("secret" in entity.id for entity in doc.entities)
    assert {("link.py", "symlink"), ("linkdir", "symlink")} <= {(s.path, s.reason) for s in doc.skipped_files}


def test_router_not_included_in_any_app_is_reported_not_guessed(tmp_path):
    write(
        tmp_path,
        "routes.py",
        """
        from fastapi import APIRouter

        router = APIRouter(prefix="/items")

        @router.get("/")
        def list_items():
            return []
        """,
    )

    doc = analyze(tmp_path)

    assert endpoint_ids(doc) == set()
    assert [w.code for w in doc.warnings] == ["router_not_included"]


def test_nested_router_prefixes_are_combined_in_fastapi_order(tmp_path):
    write(
        tmp_path,
        "main.py",
        """
        from fastapi import APIRouter, FastAPI

        app = FastAPI()
        api = APIRouter(prefix="/api")
        v1 = APIRouter(prefix="/v1")

        @v1.delete("/items/{item_id}")
        def delete_item(item_id: int):
            return None

        api.include_router(v1, prefix="/admin")
        app.include_router(api, prefix="/root")
        """,
    )

    doc = analyze(tmp_path)

    assert endpoint_ids(doc) == {"api_endpoint:DELETE /root/api/admin/v1/items/{item_id}"}


def test_dynamic_route_path_is_reported(tmp_path):
    write(
        tmp_path,
        "main.py",
        """
        from fastapi import FastAPI

        app = FastAPI()
        PATH = "/x"

        @app.get(PATH)
        def handler():
            return None
        """,
    )

    doc = analyze(tmp_path)

    assert endpoint_ids(doc) == set()
    assert [w.code for w in doc.warnings] == ["dynamic_route_path"]