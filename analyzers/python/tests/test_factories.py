from textwrap import dedent

from cfa_ir import EntityType
from cfa_python_analyzer import analyze


def write(root, name, source):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(source), encoding="utf-8")


def endpoints(document):
    return [
        entity for entity in document.entities if entity.type is EntityType.API_ENDPOINT
    ]


def test_imported_factory_with_literal_prefix(tmp_path):
    write(
        tmp_path,
        "routes.py",
        """\
        from fastapi import APIRouter

        router = APIRouter(prefix="/orders")

        @router.get("/{order_id}")
        def get_order(order_id: int):
            return {}
        """,
    )

    write(
        tmp_path,
        "factory.py",
        """\
        from fastapi import FastAPI
        from routes import router

        def create_app():
            application = FastAPI()
            application.include_router(router, prefix="/api")
            return application
        """,
    )

    write(
        tmp_path,
        "main.py",
        """\
        from factory import create_app as build

        app = build()
        """,
    )

    document = analyze(tmp_path)
    found = endpoints(document)

    assert len(found) == 1
    assert found[0].properties["path"] == "/api/orders/{order_id}"
    assert found[0].properties["app_name"] == "main.app"
    assert found[0].properties["app_file"] == "main.py"
    assert found[0].location.path == "routes.py"
    assert found[0].location.start_line == 5

    assert analyze(tmp_path).model_dump_json() == document.model_dump_json()


def test_factory_configuration_prefix_is_not_guessed(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from fastapi import FastAPI, APIRouter

        router = APIRouter()

        @router.get("/orders")
        def orders():
            return {}

        def create_app():
            app = FastAPI()
            app.include_router(router, prefix=settings.api_prefix)
            return app

        app = create_app()
        """,
    )

    document = analyze(tmp_path)

    assert endpoints(document) == []
    assert any(
        warning.code == "dynamic_factory_prefix" for warning in document.warnings
    )


def test_uninvoked_factory_does_not_publish_routes(tmp_path):
    write(
        tmp_path,
        "main.py",
        """\
        from fastapi import FastAPI, APIRouter

        router = APIRouter()

        @router.get("/orders")
        def orders():
            return {}

        def create_app():
            app = FastAPI()
            app.include_router(router)
            return app
        """,
    )

    assert endpoints(analyze(tmp_path)) == []


def test_factory_body_is_never_executed(tmp_path):
    marker = tmp_path / "executed.txt"

    write(
        tmp_path,
        "main.py",
        f"""\
        from pathlib import Path
        from fastapi import FastAPI, APIRouter

        router = APIRouter()

        @router.get("/orders")
        def orders():
            return {{}}

        def create_app():
            Path({str(marker)!r}).write_text("executed")
            app = FastAPI()
            app.include_router(router)
            return app

        app = create_app()
        """,
    )

    document = analyze(tmp_path)

    assert not marker.exists()
    assert len(endpoints(document)) == 1
