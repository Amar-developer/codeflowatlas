"""Module index built from parsed syntax trees. Names are resolved from source text; nothing is imported."""

import ast
from dataclasses import dataclass, field


FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef
MAX_REEXPORT_DEPTH = 10


@dataclass
class ModuleInfo:
    name: str
    path: str
    is_package: bool
    tree: ast.Module
    functions: dict[str, FunctionNode] = field(default_factory=dict)
    classes: dict[str, ast.ClassDef] = field(default_factory=dict)
    assignments: dict[str, ast.Assign | ast.AnnAssign] = field(default_factory=dict)
    imports: dict[str, str] = field(default_factory=dict)


@dataclass
class Symbol:
    kind: str  # module, class, function, method, variable, external
    qualified_name: str
    module: ModuleInfo | None = None
    node: ast.AST | None = None


def module_name_for(path: str) -> tuple[str, bool]:
    parts = path.removesuffix(".py").split("/")
    if parts[-1] == "__init__":
        return ".".join(parts[:-1]), True
    return ".".join(parts), False


def class_methods(node: ast.ClassDef) -> dict[str, FunctionNode]:
    return {item.name: item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}


def build_module(path: str, tree: ast.Module) -> ModuleInfo:
    """Index top-level definitions, assignments, and imports. Nested or conditional ones are not indexed."""
    name, is_package = module_name_for(path)
    module = ModuleInfo(name=name, path=path, is_package=is_package, tree=tree)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            module.functions[node.name] = node
        elif isinstance(node, ast.ClassDef):
            module.classes[node.name] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module.assignments[target.id] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            module.assignments[node.target.id] = node
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    module.imports[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    module.imports[top] = top
        elif isinstance(node, ast.ImportFrom):
            base = _import_base(module, node)
            if base is None:
                continue
            for alias in node.names:
                if alias.name != "*":
                    module.imports[alias.asname or alias.name] = f"{base}.{alias.name}" if base else alias.name

    return module


def _import_base(module: ModuleInfo, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module
    package = module.name.split(".") if module.is_package else module.name.split(".")[:-1]
    if node.level - 1 > len(package):
        return None
    package = package[: len(package) - (node.level - 1)]
    return ".".join([*package, *([node.module] if node.module else [])])


class ProjectIndex:
    def __init__(self, modules: list[ModuleInfo]) -> None:
        self.modules = {module.name: module for module in modules if module.name}

    def resolve_expr(self, module: ModuleInfo, expr: ast.expr) -> str | None:
        """Dotted name an expression refers to through imports and top-level definitions, or None."""
        if isinstance(expr, ast.Name):
            if expr.id in module.imports:
                return self._canonical_import(module, module.imports[expr.id])
            if expr.id in module.functions or expr.id in module.classes or expr.id in module.assignments:
                return f"{module.name}.{expr.id}"
            return None
        if isinstance(expr, ast.Attribute):
            base = self.resolve_expr(module, expr.value)
            return f"{base}.{expr.attr}" if base else None
        return None

    def resolve_symbol(self, module: ModuleInfo, expr: ast.expr) -> Symbol | None:
        qualified = self.resolve_expr(module, expr)
        return self.lookup(qualified) if qualified else None

    def lookup(self, qualified: str, depth: int = 0) -> Symbol | None:
        """Find the definition behind a dotted name, following project re-exports.

        Names outside the project come back as `external` symbols; project names that do not exist return None.
        """
        if depth > MAX_REEXPORT_DEPTH:
            return None
        if qualified in self.modules:
            return Symbol("module", qualified, self.modules[qualified])
        parts = qualified.split(".")
        for split in range(len(parts) - 1, 0, -1):
            module = self.modules.get(".".join(parts[:split]))
            if module is not None:
                return self._lookup_in(module, parts[split:], depth)
        return Symbol("external", qualified)

    def _lookup_in(self, module: ModuleInfo, names: list[str], depth: int) -> Symbol | None:
        head, rest = names[0], names[1:]
        qualified = f"{module.name}.{head}"
        if head in module.classes:
            node = module.classes[head]
            if not rest:
                return Symbol("class", qualified, module, node)
            method = class_methods(node).get(rest[0]) if len(rest) == 1 else None
            return Symbol("method", f"{qualified}.{rest[0]}", module, method) if method else None
        if head in module.functions and not rest:
            return Symbol("function", qualified, module, module.functions[head])
        if head in module.assignments and not rest:
            return Symbol("variable", qualified, module, module.assignments[head])
        
        if head in module.imports:
            imported = self._canonical_import(module, module.imports[head])
            return self.lookup(".".join([imported, *rest]), depth + 1)
        return None
    
    def _canonical_import(self, module: ModuleInfo, qualified: str) -> str:
        """Resolve an absolute import against this file's repository subtree."""
        root_name = qualified.split(".", 1)[0]
        parts = module.name.split(".")
        limit = len(parts) if module.is_package else len(parts) - 1

        for index in range(limit - 1, -1, -1):
            if parts[index] != root_name:
                continue

            prefix = ".".join(parts[:index])
            candidate = f"{prefix}.{qualified}" if prefix else qualified

            if any(
                name == candidate
                or candidate.startswith(name + ".")
                or name.startswith(candidate + ".")
                for name in self.modules
            ):
                return candidate

        return qualified