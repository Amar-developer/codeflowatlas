"""Conservative function-call analysis without executing target code."""

import ast
from collections import Counter

from cfa_ir import (
    AnalysisWarning,
    Confidence,
    Edge,
    EntityType,
    RelationType,
    SourceLocation,
    edge_id,
    entity_id,
)

from cfa_python_analyzer.symbols import (
    ModuleInfo,
    ProjectIndex,
    class_methods,
)


def root_name(expression):
    while isinstance(expression, ast.Attribute):
        expression = expression.value

    return expression.id if isinstance(expression, ast.Name) else None


def target_hint(expression):
    if isinstance(expression, ast.Name):
        return expression.id

    if isinstance(expression, ast.Attribute):
        base = target_hint(expression.value)
        if base != "<dynamic callable>":
            return f"{base}.{expression.attr}"[:180]

    # Do not copy arbitrary expressions or literal values into metadata.
    return "<dynamic callable>"


class Bindings(ast.NodeVisitor):
    """Find names that may shadow a callable in the current scope."""

    def __init__(self):
        self.names = Counter()
        self.wildcard = False

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names[node.id] += 1

    def visit_Attribute(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            name = root_name(node)
            if name:
                self.names[name] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.names[node.name] += 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.names[node.name] += 1

    def visit_Lambda(self, node):
        pass

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name.split(".")[0]
            self.names[name] += 1

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == "*":
                self.wildcard = True
            else:
                self.names[alias.asname or alias.name] += 1

    def visit_ExceptHandler(self, node):
        if node.name:
            self.names[node.name] += 1
        self.generic_visit(node)

    def visit_Global(self, node):
        self.names.update(node.names)

    visit_Nonlocal = visit_Global

    def visit_MatchAs(self, node):
        if node.name:
            self.names[node.name] += 1
        self.generic_visit(node)

    def visit_MatchStar(self, node):
        if node.name:
            self.names[node.name] += 1

    def visit_MatchMapping(self, node):
        if node.rest:
            self.names[node.rest] += 1
        self.generic_visit(node)


class Calls(ast.NodeVisitor):
    """Collect calls from one function body, excluding nested scopes."""

    def __init__(self):
        self.calls = []
        self.skipped = []

    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)

    def skip_scope(self, node):
        if any(isinstance(item, ast.Call) for item in ast.walk(node)):
            self.skipped.append(node)

    visit_FunctionDef = skip_scope
    visit_AsyncFunctionDef = skip_scope
    visit_ClassDef = skip_scope
    visit_Lambda = skip_scope
    visit_ListComp = skip_scope
    visit_SetComp = skip_scope
    visit_DictComp = skip_scope
    visit_GeneratorExp = skip_scope


def location(path, node):
    return SourceLocation(
        path=path,
        start_line=node.lineno,
        end_line=node.end_lineno or node.lineno,
    )


def analyze_calls(index: ProjectIndex, known_entity_ids: set[str]):
    edges = []
    warnings = []
    module_bindings = {}

    for module in index.modules.values():
        bindings = Bindings()
        for statement in module.tree.body:
            bindings.visit(statement)
        module_bindings[module.name] = bindings

    def resolve(module, expression, local):
        name = root_name(expression)
        bindings = module_bindings[module.name]

        if (
            name is None
            or local.wildcard
            or bindings.wildcard
            or name in local.names
            or bindings.names[name] != 1
        ):
            return None, "Dynamic, shadowed, or ambiguous callable"

        qualified = index.resolve_expr(module, expression)
        symbol = index.resolve_symbol(module, expression)

        if (
            symbol is None
            or symbol.kind != "function"
            or symbol.module is None
            or symbol.node is None
        ):
            return None, "Target is not a supported project function"

        # Re-exports require additional binding checks; do not guess yet.
        if qualified != symbol.qualified_name:
            return None, "Callable re-export requires further analysis"

        target_bindings = module_bindings[symbol.module.name]
        if target_bindings.wildcard or target_bindings.names[symbol.node.name] != 1:
            return None, "Target definition has ambiguous module bindings"

        if symbol.node.decorator_list:
            return None, "Decorated callable behavior is not resolved"

        target_id = entity_id(
            EntityType.FUNCTION,
            symbol.qualified_name,
        )

        if target_id not in known_entity_ids:
            return None, "Target has no indexed function entity"

        return target_id, None

    def classify(module, expression, local, target_id):
        if target_id is not None:
            return {
                "call_category": "project_function",
                "classification_reason": ("Resolved to an indexed project function."),
            }

        name = root_name(expression)
        bindings = module_bindings[module.name]

        stable_import = (
            name is not None
            and name in module.imports
            and name not in local.names
            and bindings.names[name] == 1
            and not local.wildcard
            and not bindings.wildcard
        )

        if stable_import:
            symbol = index.resolve_symbol(module, expression)

            if symbol is not None and symbol.kind == "external":
                return {
                    "call_category": "imported_callable",
                    "classification_reason": (
                        "Referenced through an import, but target source "
                        "is not available in the analyzed project index. "
                        "This does not prove it is a third-party library."
                    ),
                }

        if isinstance(expression, ast.Attribute):
            return {
                "call_category": "attribute_call",
                "classification_reason": (
                    "Attribute-call syntax was detected. The receiver "
                    "type and target implementation are not resolved."
                ),
            }

        if not isinstance(expression, ast.Name) or (
            name in local.names and not local.wildcard
        ):
            return {
                "call_category": "dynamic_call",
                "classification_reason": (
                    "The callable uses a local binding, parameter, "
                    "or computed expression. Its target is not resolved."
                ),
            }

        return {
            "call_category": "unresolved_callable",
            "classification_reason": (
                "The callable cannot be safely classified with the "
                "supported resolution rules."
            ),
        }

    for module in index.modules.values():
        functions = [
            (f"{module.name}.{name}", function)
            for name, function in module.functions.items()
        ]

        for class_name, class_node in module.classes.items():
            functions.extend(
                (
                    f"{module.name}.{class_name}.{method_name}",
                    method,
                )
                for method_name, method in class_methods(class_node).items()
            )

        for qualified_name, function in functions:
            source_id = entity_id(EntityType.FUNCTION, qualified_name)

            # Defaults and annotations are resolved in the declaration
            # context, not against the function's parameter bindings.
            # Class declaration scopes require separate handling.
            if module.functions.get(function.name) is function:
                declarations = dependency_declarations(
                    function,
                    module,
                    index,
                    module_bindings[module.name],
                )

                for parameter, marker, provider, declaration_kind in declarations:
                    if provider is None:
                        target_id = None
                        reason = (
                            "Dependency provider is omitted or uses an "
                            "unsupported argument form."
                        )
                        hint = "<implicit dependency>"
                    else:
                        target_id, reason = resolve(
                            module,
                            provider,
                            Bindings(),
                        )
                        hint = target_hint(provider)

                    site = location(module.path, marker)

                    edges.append(
                        Edge(
                            id=(
                                edge_id(
                                    RelationType.DEPENDS_ON,
                                    source_id,
                                    target_id,
                                    site,
                                )
                                + f":param{parameter}"
                                + f":col{marker.col_offset}"
                                + (
                                    f":end{marker.end_lineno}:"
                                    f"{marker.end_col_offset}"
                                )
                            ),
                            type=RelationType.DEPENDS_ON,
                            source_id=source_id,
                            target_id=target_id,
                            confidence=(
                                Confidence.HIGH
                                if target_id is not None
                                else Confidence.LOW
                            ),
                            provenance="fastapi.parameter_dependency.v1",
                            location=site,
                            target_hint=hint,
                            unresolved_reason=reason,
                            properties={
                                "parameter": parameter,
                                "declaration_kind": declaration_kind,
                                "evidence_kind": "static",
                            },
                        )
                    )

            local = Bindings()

            arguments = [
                *function.args.posonlyargs,
                *function.args.args,
                *function.args.kwonlyargs,
            ]

            if function.args.vararg:
                arguments.append(function.args.vararg)

            if function.args.kwarg:
                arguments.append(function.args.kwarg)

            local.names.update(argument.arg for argument in arguments)

            calls = Calls()

            for statement in function.body:
                local.visit(statement)
                calls.visit(statement)

            for call in calls.calls:
                target_id, reason = resolve(
                    module,
                    call.func,
                    local,
                )
                site = location(module.path, call)
                classification = classify(
                    module,
                    call.func,
                    local,
                    target_id,
                )

                edges.append(
                    Edge(
                        id=(
                            edge_id(
                                RelationType.CALLS,
                                source_id,
                                target_id,
                                site,
                            )
                            + f":col{call.col_offset}"
                            + (f":end{call.end_lineno}:" f"{call.end_col_offset}")
                        ),
                        type=RelationType.CALLS,
                        source_id=source_id,
                        target_id=target_id,
                        confidence=(
                            Confidence.HIGH if target_id is not None else Confidence.LOW
                        ),
                        provenance="python.direct_function_call.v1",
                        location=site,
                        target_hint=target_hint(call.func),
                        unresolved_reason=reason,
                        properties=classification,
                    )
                )

            for skipped in calls.skipped:
                warnings.append(
                    AnalysisWarning(
                        code="call_scope_skipped",
                        message=(
                            "Calls inside a nested definition, lambda, "
                            "or comprehension are not analyzed in this scope."
                        ),
                        location=location(module.path, skipped),
                    )
                )

    return edges, warnings


def dependency_declarations(function, module, index, bindings):
    """Find supported Depends declarations on top-level functions."""

    def reference_matches(expression, expected):
        name = root_name(expression)

        return (
            name is not None
            and not bindings.wildcard
            and bindings.names[name] == 1
            and index.resolve_expr(module, expression) in expected
        )

    def dependency_marker(expression):
        if not isinstance(expression, ast.Call):
            return None

        if reference_matches(
            expression.func,
            {"fastapi.Depends"},
        ):
            return expression

        return None

    def provider_expression(marker):
        named = [
            keyword.value for keyword in marker.keywords if keyword.arg == "dependency"
        ]

        if len(marker.args) == 1 and not named:
            if not isinstance(marker.args[0], ast.Starred):
                return marker.args[0]

        if not marker.args and len(named) == 1:
            return named[0]

        return None

    positional = [
        *function.args.posonlyargs,
        *function.args.args,
    ]

    defaults = [
        *zip(
            positional[len(positional) - len(function.args.defaults) :],
            function.args.defaults,
        ),
        *(
            (argument, default)
            for argument, default in zip(
                function.args.kwonlyargs,
                function.args.kw_defaults,
            )
            if default is not None
        ),
    ]

    for argument, default in defaults:
        marker = dependency_marker(default)

        if marker is not None:
            yield (
                argument.arg,
                marker,
                provider_expression(marker),
                "default",
            )

    arguments = [
        *positional,
        *function.args.kwonlyargs,
    ]

    for argument in arguments:
        annotation = argument.annotation

        if not isinstance(annotation, ast.Subscript) or not reference_matches(
            annotation.value,
            {
                "typing.Annotated",
                "typing_extensions.Annotated",
            },
        ):
            continue

        items = (
            annotation.slice.elts
            if isinstance(annotation.slice, ast.Tuple)
            else [annotation.slice]
        )

        for metadata in items[1:]:
            marker = dependency_marker(metadata)

            if marker is not None:
                yield (
                    argument.arg,
                    marker,
                    provider_expression(marker),
                    "annotated",
                )
