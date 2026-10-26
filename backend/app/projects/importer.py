import io
import re
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urljoin, urlparse

import httpx
from cfa_ir import EntityType
from cfa_python_analyzer.analyze import analyze
from fastapi.concurrency import run_in_threadpool

MAX_ARCHIVE_BYTES = 10_000_000
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_PYTHON_BYTES = 50_000_000
MAX_ARCHIVE_ENTRIES = 3_000
MAX_PYTHON_FILES = 2_000

OWNER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ImportProblem(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def parse_repository_url(value: str) -> tuple[str, str]:
    parsed = urlparse(value.strip())

    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ImportProblem(422, "Enter a public https://github.com/OWNER/REPO URL")

    match = re.fullmatch(r"/([^/]+)/([^/]+)/?", parsed.path)
    if match is None:
        raise ImportProblem(422, "Enter a repository URL, not a file or branch URL")

    owner = match.group(1)
    repo = match.group(2).removesuffix(".git")

    if not OWNER_RE.fullmatch(owner) or not REPO_RE.fullmatch(repo):
        raise ImportProblem(422, "Invalid GitHub owner or repository name")

    return owner, repo


async def _github_json(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)

    if response.status_code == 404:
        raise ImportProblem(404, "Public repository or default branch not found")
    if response.status_code in (403, 429):
        raise ImportProblem(503, "GitHub request limit reached; try again later")
    if response.status_code != 200:
        raise ImportProblem(502, "GitHub could not provide repository information")

    try:
        data = response.json()
    except ValueError as exc:
        raise ImportProblem(502, "GitHub returned invalid repository data") from exc

    if not isinstance(data, dict):
        raise ImportProblem(502, "GitHub returned invalid repository data")

    return data


async def _download_archive(
    client: httpx.AsyncClient, owner: str, repo: str, sha: str
) -> bytes:
    archive_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{sha}"
    redirect = await client.get(archive_url)

    if redirect.status_code not in (301, 302, 303, 307, 308):
        raise ImportProblem(502, "GitHub did not provide a repository archive")

    location = redirect.headers.get("location")
    if not location:
        raise ImportProblem(502, "GitHub archive location is missing")

    download_url = urljoin(str(redirect.request.url), location)
    parsed = urlparse(download_url)

    if (
        parsed.scheme != "https"
        or parsed.hostname != "codeload.github.com"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ImportProblem(502, "GitHub archive redirect was rejected")

    content = bytearray()

    async with client.stream("GET", download_url) as response:
        if response.status_code != 200:
            raise ImportProblem(502, "GitHub archive download failed")

        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > MAX_ARCHIVE_BYTES:
                raise ImportProblem(413, "Repository archive exceeds 10 MB")

    return bytes(content)


def _analyze_archive(archive: bytes, repository_url: str):
    try:
        source = zipfile.ZipFile(io.BytesIO(archive))
    except zipfile.BadZipFile as exc:
        raise ImportProblem(422, "GitHub archive is invalid") from exc

    with source, tempfile.TemporaryDirectory(prefix="cfa-import-") as directory:
        root = Path(directory)
        entries = source.infolist()

        if len(entries) > MAX_ARCHIVE_ENTRIES:
            raise ImportProblem(413, "Repository has too many archive entries")

        seen: set[str] = set()
        total_bytes = 0
        python_files = 0
        skipped_count = 0

        for entry in entries:
            name = entry.filename

            if (
                "\\" in name
                or "\x00" in name
                or name.startswith("/")
                or name.startswith("../")
            ):
                raise ImportProblem(422, "Repository archive contains an unsafe path")

            raw_parts = name[:-1].split("/") if entry.is_dir() else name.split("/")

            if not raw_parts or any(part in ("", ".", "..") for part in raw_parts):
                raise ImportProblem(422, "Repository archive contains an unsafe path")

            # GitHub archives contain one top-level directory entry.
            if entry.is_dir() and len(raw_parts) == 1:
                continue

            if len(raw_parts) < 2:
                raise ImportProblem(422, "Repository archive contains an unsafe path")

            relative = PurePosixPath(*raw_parts[1:])

            if entry.is_dir():
                continue

            mode = entry.external_attr >> 16
            file_type = stat.S_IFMT(mode)
            if file_type not in (0, stat.S_IFREG):
                raise ImportProblem(422, "Repository archive contains a special file")

            if relative.suffix != ".py":
                skipped_count += 1
                continue

            path = relative.as_posix()

            if path in seen:
                raise ImportProblem(422, "Repository archive contains duplicate files")
            seen.add(path)

            if len(path) > 1500 or entry.file_size > MAX_FILE_BYTES:
                raise ImportProblem(
                    413, "A Python source file exceeds the import limit"
                )
            if python_files >= MAX_PYTHON_FILES:
                raise ImportProblem(413, "Repository has too many Python files")

            with source.open(entry) as handle:
                data = handle.read(MAX_FILE_BYTES + 1)

            if len(data) > MAX_FILE_BYTES:
                raise ImportProblem(
                    413, "A Python source file exceeds the import limit"
                )

            total_bytes += len(data)
            if total_bytes > MAX_TOTAL_PYTHON_BYTES:
                raise ImportProblem(413, "Repository Python source exceeds 50 MB")

            destination = root.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            python_files += 1

        if python_files == 0:
            raise ImportProblem(422, "No Python files found in this repository")

        document = analyze(root, source=repository_url)
        entities = {entity.id: entity for entity in document.entities}

        endpoints = []
        for entity in document.entities:
            if entity.type is not EntityType.API_ENDPOINT or entity.location is None:
                continue

            handler_id = entity.properties.get("handler")
            handler = entities.get(handler_id)

            endpoints.append(
                {
                    "method": str(entity.properties["method"]),
                    "path": str(entity.properties["path"]),
                    "handler": (
                        handler.qualified_name or handler.name
                        if handler is not None
                        else "Unknown handler"
                    ),
                    "source_file": entity.location.path,
                    "source_line": entity.location.start_line,
                    "app_name": entity.properties.get("app_name"),
                    "app_file": entity.properties.get("app_file"),
                }
            )

        if len(endpoints) > 1_000:
            raise ImportProblem(413, "Repository has too many discovered endpoints")

        warnings = [
            {
                "code": warning.code,
                "message": warning.message,
                "file": warning.location.path if warning.location else None,
                "line": warning.location.start_line if warning.location else None,
            }
            for warning in document.warnings[:100]
        ]

        skipped_count += len(document.skipped_files)

        return (
            endpoints,
            warnings,
            skipped_count,
            document.analyzer.version,
            document.model_dump(mode="json"),
        )


async def import_public_github_repository(url: str) -> dict:
    owner, repo = parse_repository_url(url)
    repository_url = f"https://github.com/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CodeFlowAtlas/0.1",
    }

    try:
        async with httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(20.0, connect=5.0),
            follow_redirects=False,
            trust_env=False,
        ) as client:
            metadata = await _github_json(
                client, f"https://api.github.com/repos/{owner}/{repo}"
            )

            if metadata.get("private") is not False:
                raise ImportProblem(422, "Only public repositories are supported")

            branch = metadata.get("default_branch")
            if not isinstance(branch, str) or not branch:
                raise ImportProblem(422, "Repository has no default branch")

            commit = await _github_json(
                client,
                f"https://api.github.com/repos/{owner}/{repo}/commits/"
                f"{quote(branch, safe='')}",
            )
            sha = commit.get("sha")

            if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
                raise ImportProblem(502, "GitHub did not return a valid commit SHA")

            archive = await _download_archive(client, owner, repo, sha)
    except httpx.HTTPError as exc:
        raise ImportProblem(502, "Could not reach GitHub") from exc

    try:
        (
            endpoints,
            warnings,
            skipped_count,
            analyzer_version,
            static_graph,
        ) = await run_in_threadpool(
            _analyze_archive,
            archive,
            repository_url,
        )
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ImportProblem(422, "Repository archive could not be analyzed") from exc

    return {
        "owner": owner,
        "repo": repo,
        "repository_url": repository_url,
        "commit_sha": sha,
        "analyzer_version": analyzer_version,
        "endpoints": endpoints,
        "warnings": warnings,
        "skipped_count": skipped_count,
        "static_graph": static_graph,
    }
