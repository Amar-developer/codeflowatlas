"""Static analysis entry point: scan, parse, discover, and emit an IR document.

Target files are read as bytes and parsed with `ast`. They are never imported, executed, or installed.
"""

import ast
import hashlib
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from cfa_ir import (
    AnalysisWarning,
    AnalyzerInfo,
    Confidence,
    Edge,
    Entity,
    EntityType,
    IRDocument,
    RelationType,
    RevisionInfo,
    SkippedFile,
    SourceLocation,
    edge_id,
    entity_id,
)
from cfa_python_analyzer.fastapi_routes import discover_routes
from cfa_python_analyzer.scan import scan
from cfa_python_analyzer.symbols import FunctionNode, ModuleInfo, ProjectIndex, build_module, class_methods


ANALYZER_VERSION = "0.2.0"
ANALYZER = AnalyzerInfo(name="cfa-python-analyzer", version=ANALYZER_VERSION)


def analyze(root: Path, source: str | None = None) -> IRDocument:
    root = root.resolve()
    scanned = scan(root)
    skipped = [SkippedFile(path=path, reason=reason) for path, reason in scanned.skipped]
    warnings: list[AnalysisWarning] = []
    modules: list[ModuleInfo] = []
    fingerprint = hashlib.sha256()

    for path in scanned.python_files:
        raw = (root / path).read_bytes()
        fingerprint.update(path.encode() + b"\0" + raw + b"\0")
        try:
            tree = ast.parse(raw.decode("utf-8"), filename=path)
        except UnicodeDecodeError:
            skipped.append(SkippedFile(path=path, reason="not valid UTF-8"))
            continue
        except (SyntaxError, ValueError, RecursionError) as exc:
            line = getattr(exc, "lineno", None) or 1
            skipped.append(SkippedFile(path=path, reason="syntax error"))
            warnings.append(AnalysisWarning(code="parse_error", message=str(exc), location=_location(path, line)))
            continue
        modules.append(build_module(path, tree))

    index = ProjectIndex(modules)
    entities: dict[str, Entity] = {}
    edges: dict[str, Edge] = {}

    for module in modules:
        for entity in _code_entities(module):
            entities.setdefault(entity.id, entity)

    routes, route_warnings = discover_routes(index)
    route_counts = Counter((route.method, route.path) for route in routes)
    warnings += [
        AnalysisWarning(code=w.code, message=w.message, location=_node_location(w.module.path, w.node)) for w in route_warnings
    ]

    for route in routes:
        route_key = (route.method, route.path)

        if route_counts[route_key] > 1:
            identity = f"{route.app_name} {route.method} {route.path}"
        else:
            identity = f"{route.method} {route.path}"

        endpoint_id = entity_id(EntityType.API_ENDPOINT, identity)
        location = _node_location(route.module.path, route.decorator)
        if endpoint_id in entities:
            warnings.append(
                AnalysisWarning(code="duplicate_route", message=f"{route.method} {route.path} is declared more than once", location=location)
            )
            continue

        handler_id = entity_id(EntityType.FUNCTION, route.handler_name)
        entities[endpoint_id] = Entity(
            id=endpoint_id,
            type=EntityType.API_ENDPOINT,
            name=f"{route.method} {route.path}",
            location=location,
            properties={
                "framework": "fastapi",
                "method": route.method,
                "path": route.path,
                "handler": handler_id,
                "request_model": route.request_model,
                "response_model": route.response_model,
                "status_code": route.status_code,
                "app_name": route.app_name,
                "app_file": route.app_file
            },
        )
        edge = Edge(
            id=edge_id(RelationType.EXPOSES, endpoint_id, handler_id, location),
            type=RelationType.EXPOSES,
            source_id=endpoint_id,
            target_id=handler_id,
            confidence=Confidence.EXACT,
            provenance="fastapi.route_decorator",
            location=location,
        )
        edges[edge.id] = edge

    return IRDocument(
        analyzer=ANALYZER,
        repository=RevisionInfo(source=source or f"local:{root.name}", revision=f"sha256:{fingerprint.hexdigest()}"),
        entities=sorted(entities.values(), key=lambda entity: entity.id),
        edges=sorted(edges.values(), key=lambda edge: edge.id),
        warnings=warnings,
        skipped_files=sorted(skipped, key=lambda item: item.path),
    )


def _code_entities(module: ModuleInfo) -> Iterator[Entity]:
    for name, node in module.functions.items():
        yield _function_entity(f"{module.name}.{name}", node, module.path)
    for class_name, node in module.classes.items():
        qualified = f"{module.name}.{class_name}"
        yield Entity(
            id=entity_id(EntityType.CLASS, qualified),
            type=EntityType.CLASS,
            name=class_name,
            qualified_name=qualified,
            location=_node_location(module.path, node),
        )
        for method_name, method in class_methods(node).items():
            yield _function_entity(f"{qualified}.{method_name}", method, module.path)


def _function_entity(qualified: str, node: FunctionNode, path: str) -> Entity:
    return Entity(
        id=entity_id(EntityType.FUNCTION, qualified),
        type=EntityType.FUNCTION,
        name=node.name,
        qualified_name=qualified,
        location=_node_location(path, node),
    )


def _node_location(path: str, node: ast.AST) -> SourceLocation:
    return SourceLocation(path=path, start_line=node.lineno, end_line=node.end_lineno or node.lineno)


def _location(path: str, line: int) -> SourceLocation:
    return SourceLocation(path=path, start_line=line, end_line=line)