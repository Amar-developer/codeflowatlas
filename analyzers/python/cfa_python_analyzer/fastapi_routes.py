"""FastAPI app, router, and route discovery from parsed source."""

import ast
import re
from dataclasses import dataclass, field

from cfa_python_analyzer.symbols import FunctionNode, ModuleInfo, ProjectIndex, Symbol
from cfa_python_analyzer.calls import Bindings, root_name

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}
FASTAPI_APP = "fastapi.FastAPI"
FASTAPI_ROUTER = "fastapi.APIRouter"
PYDANTIC_BASE_MODEL = "pydantic.BaseModel"
STATUS_MODULES = ("fastapi.status.", "starlette.status.")
MAX_DEPTH = 10

_STATUS_NAME = re.compile(r"^HTTP_(\d{3})(?:_|$)")


@dataclass
class RouterDef:
    qualified_name: str
    is_app: bool
    prefix: str
    source_file: str
    mounts: list[tuple["RouterDef", str]] = field(
        default_factory=list
    )  # parent router, include prefix


@dataclass
class Route:
    method: str
    path: str
    handler_name: str
    handler: FunctionNode
    decorator: ast.Call
    module: ModuleInfo
    request_model: str | None
    response_model: str | None
    status_code: int | None
    app_name: str
    app_file: str


@dataclass
class RouteWarning:
    code: str
    message: str
    module: ModuleInfo
    node: ast.AST


def discover_routes(index: ProjectIndex) -> tuple[list[Route], list[RouteWarning]]:
    warnings: list[RouteWarning] = []
    routers = _find_routers(index, warnings)
    _find_factory_mounts(index, routers, warnings)
    _find_mounts(index, routers, warnings)

    routes: list[Route] = []
    for module in index.modules.values():
        for func in module.functions.values():
            handler_name = f"{module.name}.{func.name}"
            for decorator in func.decorator_list:
                found = _route_decorator(index, module, decorator, routers)
                if found is None:
                    continue
                router, method, path_node = found
                route_path = _string(path_node)
                if route_path is None:
                    warnings.append(
                        RouteWarning(
                            "dynamic_route_path",
                            f"{method} route on {handler_name} has a non-literal path",
                            module,
                            decorator,
                        )
                    )
                    continue

                full_paths = sorted(
                    set(_full_paths(router, router.prefix + route_path))
                )
                if not full_paths:
                    warnings.append(
                        RouteWarning(
                            "router_not_included",
                            f"{router.qualified_name} is not included in any FastAPI app found statically; "
                            f"{method} {route_path} on {handler_name} is not reported as an endpoint",
                            module,
                            decorator,
                        )
                    )
                    continue

                for path, app_name, app_file in full_paths:
                    routes.append(
                        Route(
                            method=method,
                            path=path,
                            handler_name=handler_name,
                            handler=func,
                            decorator=decorator,
                            module=module,
                            request_model=_request_model(index, module, func),
                            response_model=_response_model(
                                index, module, func, decorator
                            ),
                            status_code=_status_code(index, module, decorator),
                            app_name=app_name,
                            app_file=app_file,
                        )
                    )
    return routes, warnings


def _find_routers(
    index: ProjectIndex, warnings: list[RouteWarning]
) -> dict[str, RouterDef]:
    routers: dict[str, RouterDef] = {}
    for module in index.modules.values():
        for name, statement in module.assignments.items():
            call = statement.value
            if not isinstance(call, ast.Call):
                continue
            symbol = index.resolve_symbol(module, call.func)
            if symbol is None or symbol.qualified_name not in (
                FASTAPI_APP,
                FASTAPI_ROUTER,
            ):
                continue

            qualified = f"{module.name}.{name}"
            prefix_node = _keyword(call, "prefix")
            prefix = _string(prefix_node) if prefix_node is not None else ""
            if prefix is None:
                warnings.append(
                    RouteWarning(
                        "dynamic_router_prefix",
                        f"{qualified} has a non-literal prefix",
                        module,
                        call,
                    )
                )
                continue
            routers[qualified] = RouterDef(
                qualified_name=qualified,
                is_app=symbol.qualified_name == FASTAPI_APP,
                prefix=prefix,
                source_file=module.path,
            )
    return routers


def _named_assignment(statement):
    if (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
    ):
        return statement.targets[0].id, statement.value

    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        return statement.target.id, statement.value

    return None, None


class _FactoryReturns(ast.NodeVisitor):
    """Collect returns belonging to the factory, excluding nested scopes."""

    def __init__(self):
        self.returns = []

    def visit_Return(self, node):
        self.returns.append(node)

    def visit_FunctionDef(self, node):
        pass

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_ClassDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef


def _find_factory_mounts(index, routers, warnings):
    module_bindings = {}

    for module in index.modules.values():
        bindings = Bindings()
        for statement in module.tree.body:
            bindings.visit(statement)
        module_bindings[module.name] = bindings

    def stable_reference(module, expression):
        name = root_name(expression)
        bindings = module_bindings[module.name]
        return name is not None and not bindings.wildcard and bindings.names[name] == 1

    for owner in index.modules.values():
        for exported_name, assignment in owner.assignments.items():
            invocation = assignment.value

            if (
                not isinstance(invocation, ast.Call)
                or invocation.args
                or invocation.keywords
                or not stable_reference(owner, invocation.func)
            ):
                continue

            symbol = index.resolve_symbol(owner, invocation.func)

            if (
                symbol is None
                or symbol.kind != "function"
                or symbol.module is None
                or not isinstance(symbol.node, ast.FunctionDef)
            ):
                continue

            module = symbol.module
            factory = symbol.node

            if (
                factory.decorator_list
                or factory.args.posonlyargs
                or factory.args.args
                or factory.args.kwonlyargs
                or factory.args.vararg
                or factory.args.kwarg
                or module_bindings[module.name].wildcard
                or module_bindings[module.name].names[factory.name] != 1
            ):
                continue

            local = Bindings()
            for statement in factory.body:
                local.visit(statement)

            constructions = []

            for statement in factory.body:
                name, value = _named_assignment(statement)

                if (
                    name is None
                    or not isinstance(value, ast.Call)
                    or not stable_reference(module, value.func)
                    or root_name(value.func) in local.names
                ):
                    continue

                constructor = index.resolve_symbol(module, value.func)

                if (
                    constructor is not None
                    and constructor.qualified_name == FASTAPI_APP
                ):
                    constructions.append((name, statement))

            if len(constructions) != 1:
                continue

            app_local, construction = constructions[0]
            returns = _FactoryReturns()

            for statement in factory.body:
                returns.visit(statement)

            supported_return = (
                isinstance(factory.body[-1], ast.Return)
                and len(returns.returns) == 1
                and isinstance(returns.returns[0].value, ast.Name)
                and returns.returns[0].value.id == app_local
                and local.names[app_local] == 1
            )

            if not supported_return:
                warnings.append(
                    RouteWarning(
                        "unsupported_factory_return",
                        "Factory must return its single, unreassigned "
                        "FastAPI instance through one final return.",
                        module,
                        factory,
                    )
                )
                continue

            qualified = f"{owner.name}.{exported_name}"
            parent = RouterDef(
                qualified_name=qualified,
                is_app=True,
                prefix="",
                source_file=owner.path,
            )
            routers[qualified] = parent
            constructed = False

            for statement in factory.body:
                if statement is construction:
                    constructed = True
                    continue

                if not constructed:
                    continue

                if not (
                    isinstance(statement, ast.Expr)
                    and isinstance(statement.value, ast.Call)
                ):
                    continue

                call = statement.value

                if not (
                    isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == app_local
                ):
                    continue

                if call.func.attr == "add_api_route":
                    warnings.append(
                        RouteWarning(
                            "unsupported_factory_registration",
                            "add_api_route inside a factory is not "
                            "supported by this registration adapter.",
                            module,
                            call,
                        )
                    )
                    continue

                if call.func.attr != "include_router":
                    continue

                child_expression = (
                    call.args[0] if call.args else _keyword(call, "router")
                )
                child_name = (
                    root_name(child_expression)
                    if child_expression is not None
                    else None
                )

                child = None

                if (
                    child_expression is not None
                    and child_name not in local.names
                    and stable_reference(module, child_expression)
                ):
                    child = _router_for(
                        index,
                        module,
                        child_expression,
                        routers,
                    )

                prefix_node = _keyword(call, "prefix")
                prefix = _string(prefix_node) if prefix_node is not None else ""

                if child is None:
                    warnings.append(
                        RouteWarning(
                            "unresolved_factory_router",
                            "Factory router reference could not be resolved.",
                            module,
                            call,
                        )
                    )
                elif prefix is None:
                    warnings.append(
                        RouteWarning(
                            "dynamic_factory_prefix",
                            "Factory app was recognized, but this router "
                            "uses a configuration-derived or computed prefix. "
                            "Its full endpoint paths remain unresolved.",
                            module,
                            call,
                        )
                    )
                else:
                    child.mounts.append((parent, prefix))


def _find_mounts(
    index: ProjectIndex, routers: dict[str, RouterDef], warnings: list[RouteWarning]
) -> None:
    """Record top-level `parent.include_router(child, prefix=...)` calls."""
    for module in index.modules.values():
        for statement in module.tree.body:
            if not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Call)
            ):
                continue
            call = statement.value
            if not (
                isinstance(call.func, ast.Attribute)
                and call.func.attr == "include_router"
            ):
                continue

            parent = _router_for(index, module, call.func.value, routers)
            child_expr = call.args[0] if call.args else _keyword(call, "router")
            child = (
                _router_for(index, module, child_expr, routers)
                if child_expr is not None
                else None
            )
            prefix_node = _keyword(call, "prefix")
            prefix = _string(prefix_node) if prefix_node is not None else ""

            if parent is None or child is None:
                warnings.append(
                    RouteWarning(
                        "unresolved_include_router",
                        "include_router target could not be resolved",
                        module,
                        call,
                    )
                )
            elif prefix is None:
                warnings.append(
                    RouteWarning(
                        "dynamic_router_prefix",
                        f"include of {child.qualified_name} has a non-literal prefix",
                        module,
                        call,
                    )
                )
            else:
                child.mounts.append((parent, prefix))


def _full_paths(
    router: RouterDef,
    path: str,
    depth: int = 0,
) -> list[tuple[str, str, str]]:
    """Return (full path, FastAPI app name, FastAPI app source file)."""
    if router.is_app:
        return [(path, router.qualified_name, router.source_file)]

    if depth > MAX_DEPTH:
        return []

    paths: list[tuple[str, str, str]] = []

    for parent, include_prefix in router.mounts:
        paths.extend(
            _full_paths(
                parent,
                parent.prefix + include_prefix + path,
                depth + 1,
            )
        )

    return paths


def _route_decorator(
    index: ProjectIndex,
    module: ModuleInfo,
    decorator: ast.expr,
    routers: dict[str, RouterDef],
) -> tuple[RouterDef, str, ast.expr | None] | None:
    if not (
        isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
    ):
        return None
    if decorator.func.attr not in HTTP_METHODS:
        return None
    router = _router_for(index, module, decorator.func.value, routers)
    if router is None:
        return None
    path = decorator.args[0] if decorator.args else _keyword(decorator, "path")
    return router, decorator.func.attr.upper(), path


def _router_for(
    index: ProjectIndex,
    module: ModuleInfo,
    expr: ast.expr,
    routers: dict[str, RouterDef],
) -> RouterDef | None:
    symbol = index.resolve_symbol(module, expr)
    return routers.get(symbol.qualified_name) if symbol else None


def _request_model(
    index: ProjectIndex, module: ModuleInfo, func: FunctionNode
) -> str | None:
    """First plain-annotated parameter that is a Pydantic model. `Annotated[...]` parameters are dependencies or params."""
    for arg in [*func.args.posonlyargs, *func.args.args, *func.args.kwonlyargs]:
        if arg.annotation is None or isinstance(arg.annotation, ast.Subscript):
            continue
        model = _pydantic_model(index, module, arg.annotation)
        if model:
            return model
    return None


def _response_model(
    index: ProjectIndex, module: ModuleInfo, func: FunctionNode, decorator: ast.Call
) -> str | None:
    explicit = _keyword(decorator, "response_model")
    if explicit is not None:
        return _pydantic_model(index, module, explicit)
    return (
        _pydantic_model(index, module, func.returns)
        if func.returns is not None
        else None
    )


def _status_code(
    index: ProjectIndex, module: ModuleInfo, decorator: ast.Call
) -> int | None:
    node = _keyword(decorator, "status_code")
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    qualified = index.resolve_expr(module, node)
    if qualified and qualified.startswith(STATUS_MODULES):
        match = _STATUS_NAME.match(qualified.rsplit(".", 1)[1])
        return int(match.group(1)) if match else None
    return None


def _pydantic_model(
    index: ProjectIndex, module: ModuleInfo, expr: ast.expr
) -> str | None:
    symbol = index.resolve_symbol(module, expr)
    if symbol and symbol.kind == "class" and _is_pydantic(index, symbol):
        return symbol.qualified_name
    return None


def _is_pydantic(index: ProjectIndex, symbol: Symbol, depth: int = 0) -> bool:
    if (
        depth > MAX_DEPTH
        or not isinstance(symbol.node, ast.ClassDef)
        or symbol.module is None
    ):
        return False
    for base in symbol.node.bases:
        base_symbol = index.resolve_symbol(symbol.module, base)
        if base_symbol is None:
            continue
        if base_symbol.qualified_name == PYDANTIC_BASE_MODEL:
            return True
        if base_symbol.kind == "class" and _is_pydantic(index, base_symbol, depth + 1):
            return True
    return False


def _keyword(call: ast.Call, name: str) -> ast.expr | None:
    return next(
        (keyword.value for keyword in call.keywords if keyword.arg == name), None
    )


def _string(node: ast.expr | None) -> str | None:
    return (
        node.value
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        else None
    )
