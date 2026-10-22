"use client";

import { useEffect, useState } from "react";

type ProjectSummary = {
  id: string;
  name: string;
  repository_url: string;
  commit_sha: string;
  created_at: string;
};

type Endpoint = {
  id: string;
  method: string;
  path: string;
  handler: string;
  source_file: string;
  source_line: number;
  source_url: string;
};

type ProjectDetail = ProjectSummary & {
  analyzer_version: string;
  skipped_count: number;
  warnings: {
    code: string;
    message: string;
    file: string | null;
    line: number | null;
  }[];
  endpoints: Endpoint[];
};

const errorMessage = async (response: Response): Promise<string> => {
  const body: unknown = await response.json().catch(() => null);

  if (
    typeof body === "object" &&
    body !== null &&
    "detail" in body &&
    typeof body.detail === "string"
  ) {
    return body.detail;
  }

  return `Request failed (${response.status})`;
};

const RepositoryImport = () => {
  const [url, setUrl] = useState("");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selected, setSelected] = useState<ProjectDetail | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadProjects = async () => {
    const response = await fetch("/api/projects", { cache: "no-store" });
    if (!response.ok) throw new Error(await errorMessage(response));
    setProjects((await response.json()) as ProjectSummary[]);
  };

  useEffect(() => {
    void loadProjects().catch((cause: unknown) => {
      setError(cause instanceof Error ? cause.message : "Could not load projects");
    });
  }, []);

  const importRepository = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!response.ok) throw new Error(await errorMessage(response));

      const imported = (await response.json()) as ProjectDetail;
      setSelected(imported);
      setUrl("");
      await loadProjects();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Import failed");
    } finally {
      setBusy(false);
    }
  };

  const openProject = async (id: string) => {
    setError("");

    try {
      const response = await fetch(`/api/projects/${id}`, {
        cache: "no-store",
      });
      if (!response.ok) throw new Error(await errorMessage(response));
      setSelected((await response.json()) as ProjectDetail);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not open project");
    }
  };

  return (
    <section className="mt-8 rounded-3xl border border-brand-400/20 bg-[#101522] p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-widest text-brand-300">
        Repository inspection
      </p>
      <h2 className="mt-2 text-2xl font-semibold text-white">
        Import a public GitHub repository
      </h2>
      <p className="mt-2 text-sm text-slate-400">
        Discover FastAPI endpoints from source code. No project code is run.
      </p>

      <form onSubmit={importRepository} className="mt-6 flex flex-col gap-3 sm:flex-row">
        <label htmlFor="repository-url" className="sr-only">
          GitHub repository URL
        </label>
        <input
          id="repository-url"
          type="url"
          required
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://github.com/owner/repository"
          className="min-w-0 flex-1 rounded-xl border border-white/15 bg-[#0b0d17] px-4 py-3 text-sm text-white outline-none focus:border-brand-400"
        />
        <button
          type="submit"
          disabled={busy}
          className="rounded-xl bg-brand-500 px-5 py-3 text-sm font-bold text-white disabled:opacity-50"
        >
          {busy ? "Analyzing…" : "Import repository"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 text-sm text-brand-200">
          {error}
        </p>
      )}

      {projects.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-white">Your imports</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {projects.map((project) => (
              <button
                key={project.id}
                type="button"
                onClick={() => void openProject(project.id)}
                className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-brand-400"
              >
                {project.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {selected && (
        <div className="mt-8 border-t border-white/10 pt-6">
          <h3 className="text-xl font-semibold text-white">{selected.name}</h3>
          <p className="mt-2 break-all font-mono text-xs text-slate-400">
            Commit {selected.commit_sha}
          </p>
          <p className="mt-2 text-sm text-slate-400">
            {selected.endpoints.length} endpoints · {selected.skipped_count} skipped files
          </p>

          {selected.endpoints.length === 0 && (
            <p className="mt-5 text-sm text-amber-200">
              No supported FastAPI routes were found in this revision.
            </p>
          )}

          <ul className="mt-5 space-y-3">
            {selected.endpoints.map((endpoint) => (
              <li
                key={endpoint.id}
                className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <span className="rounded bg-brand-500/15 px-2 py-1 font-mono text-xs font-bold text-brand-200">
                    {endpoint.method}
                  </span>
                  <span className="font-mono text-sm text-white">
                    {endpoint.path}
                  </span>
                </div>
                <p className="mt-2 break-all text-xs text-slate-400">
                  {endpoint.handler} · {endpoint.source_file}:{endpoint.source_line}
                </p>
                <a
                  href={endpoint.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-block text-sm font-semibold text-brand-300 hover:underline"
                >
                  Open source at this commit ↗
                </a>
              </li>
            ))}
          </ul>

          {selected.warnings.length > 0 && (
            <details className="mt-6 text-sm text-slate-400">
              <summary className="cursor-pointer">
                Analysis warnings ({selected.warnings.length})
              </summary>
              <ul className="mt-2 list-inside list-disc space-y-1">
                {selected.warnings.map((warning, index) => (
                  <li key={`${warning.code}-${index}`}>{warning.message}</li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </section>
  );
};

export default RepositoryImport;