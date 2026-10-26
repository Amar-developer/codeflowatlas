# cfa-python-analyzer

Static analyzer for Python and FastAPI. It reads repository files as bytes, parses them with `ast`, and emits a `cfa_ir.IRDocument`. It never imports, executes, or installs the target code.

    python -m cfa_python_analyzer fixtures/fastapi-basic --source fixture:fastapi-basic

## Supported

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

## Function calls (0.3.0)

Function and method bodies are inspected for calls without execution.
Direct project-function calls through supported imports and aliases
produce high-confidence `calls` edges with call-site source locations.
Unresolved calls retain a target hint and explanation.

Parameters, local bindings, ambiguous module bindings, decorated targets,
callable re-exports, instance methods, constructors, external functions,
and computed callable expressions are not resolved to function targets.
Nested definitions, lambdas, and comprehensions are skipped with a
`call_scope_skipped` warning when they contain calls. Calls in defaults,
annotations, decorators, and module-level initialization are not extracted.

This is conservative name-based analysis. Runtime monkey-patching,
reflection, and dynamic namespace mutation can invalidate static
relationships. No call edge establishes execution.

Database reads/writes, HTTP-service classification, and FastAPI
dependency edges remain unsupported by this call-analysis implementation.

## Call classification (0.4.0)

Call edges include a category and explanation in their properties:
project function, imported callable, attribute call, dynamic callable,
or unresolved callable. Categories describe static source evidence.
An imported callable is not necessarily a third-party dependency.
Attribute-call syntax does not establish an instance type.
Classification does not resolve missing targets, establish execution,
or classify database operations. Older saved graphs retain their
original metadata.

## Declared FastAPI dependencies (0.5.0)

Top-level function parameters support Depends(provider),
Depends(dependency=provider), and direct typing.Annotated or
typing_extensions.Annotated metadata containing Depends(provider).
Supported import aliases are recognized.

Dependencies produce static depends_on edges with parameter names,
source locations, and confidence. Providers use the existing conservative
function resolver. Missing or unsupported providers remain unresolved.

Class declaration scopes, string annotations, annotation type aliases,
Security, router/app/decorator dependency lists, and provider inference
from parameter types are unsupported. Arbitrary functions may declare
Depends without being invoked by FastAPI; these edges describe declarations,
not observed dependency execution.

## FastAPI app factories (0.6.0)

Supports module-level assignments that invoke an undecorated, zero-parameter
project factory without arguments. The factory must directly construct one
FastAPI instance, leave that variable unreassigned, and return it through
one final return. Direct include_router statements can connect existing
module-level routers using literal prefixes.

Imported factory aliases are supported through the existing symbol index.
Factories are inspected as syntax and are never executed.

Configuration-derived prefixes remain unresolved and produce
dynamic_factory_prefix warnings. Conditional/loop-based registration,
nested route handlers, add_api_route, factory-local routers, parameterized
or async factories, and mounted sub-applications remain unsupported.
