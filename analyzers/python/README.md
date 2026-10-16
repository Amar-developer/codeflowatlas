# cfa-python-analyzer

Static analyzer for Python and FastAPI. It reads repository files as bytes, parses them with `ast`, and emits a `cfa_ir.IRDocument`. It never imports, executes, or installs the target code.

    python -m cfa_python_analyzer fixtures/fastapi-basic --source fixture:fastapi-basic

## Supported (0.1.0)

- Bounded scan: at most 2,000 Python files, 1 MB per file, 50 MB total. Symlinks are skipped, not followed. Non-Python files, ignored directories, and files over limits are listed in `skipped_files`.
- Syntax errors become a `parse_error` warning; other files are still analyzed.
- Top-level functions, classes, and methods become entities.
- Imports, `from` imports, relative imports, aliases, and project re-exports are resolved by name.
- FastAPI: `FastAPI()` and `APIRouter(prefix=...)` assigned at module level; `@router.get/post/put/patch/delete/options/head(path)`; top-level `include_router(router, prefix=...)` chains, combined in FastAPI order; request model (first plain-annotated Pydantic parameter), `response_model` or return annotation, and `status_code` as an int or `status.HTTP_*` constant.

## Not supported yet (reported, not guessed)

- Non-literal route paths or prefixes: `dynamic_route_path` / `dynamic_router_prefix` warning.
- Routers never included in an app: `router_not_included` warning; no endpoint is reported.
- `include_router` that cannot be resolved: `unresolved_include_router` warning.
- Not detected at all: apps or routers created inside functions (app factories), `add_api_route`, `api_route`, websocket routes, class-based views, mounts of sub-applications, imports inside `if`/`try` blocks, and `src/` layouts where the import root is not the repository root.
- The order of `include_router` calls is not checked; FastAPI copies routes at include time, so including a router before its own child routes are added can differ at runtime.
- Call, database, and external HTTP edges arrive in analyzer part 2.