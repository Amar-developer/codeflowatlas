# Repository import and analysis

An import creates a repository revision record containing source type, canonical URL or archive identity, commit SHA or content fingerprint, import status, and workspace path. The importer validates archive entries, size and compression limits, symlinks, path traversal, and remote URL policy before writing files. It applies ignore rules and limits file size, count, depth, and total bytes. Analysis reads source files as data. It does not invoke package installers, import target modules, execute setup scripts, or run target tests.

The analyzer pipeline is: file scan → language and framework detection → parser → symbol extraction → route discovery → import and call resolution → infrastructure indicators → IR validation → graph persistence → findings and warnings. Python's `ast` module is the first parser. Resolution should distinguish exact references from likely or unresolved dynamic calls. Decorators, dependency injection, dynamic imports, reflection, and framework registration require explicit confidence and limitations.

FastAPI analysis covers route decorators, `APIRouter` inclusion and prefixes, HTTP methods and paths, handler symbols, dependency declarations, and request/response models when statically resolvable. Flask and Django analyzers have separate fixture suites and should not be described as deeply supported until those suites pass.

### Analyzer outputs

Every analysis run records repository revision, analyzer and schema versions, start and completion states, warnings, counts, and reproducible inputs. Output includes files, entities, edges, endpoints, source locations, confidence, and findings. The UI must show incomplete analysis and parse failures rather than silently omitting unsupported code.
