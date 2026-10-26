"use client";

import { useEffect, useState } from "react";
import SourceFlowDiagram from "./SourceFlowDiagram";
import type { EndpointFlowData } from "./flow-types";
import { callCategoryLabel } from "./flow-types";

type Props = {
  projectId: string;
  endpointId: string;
};

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; flow: EndpointFlowData };

export default function EndpointFlow(props: Props) {
  const [depth, setDepth] = useState(1);
  const [filter, setFilter] = useState("all");

  return (
    <section className="mt-6 border-t border-white/10 pt-5">
      <h5 className="font-semibold text-white">Source-flow explorer</h5>
      <p className="mt-2 text-xs leading-5 text-slate-400">
        Explore saved static relationships. Timing and runtime execution are not
        measured here.
      </p>

      <div className="mt-4 flex flex-wrap gap-4">
        <label className="text-sm text-slate-300">
          Downstream depth
          <select
            value={depth}
            onChange={(event) => setDepth(Number(event.target.value))}
            className="ml-2 rounded-lg border border-white/15 bg-[#0b0d17] px-3 py-2"
          >
            {[1, 2, 3].map((value) => (
              <option key={value} value={value}>
                {value} {value === 1 ? "level" : "levels"}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-slate-300">
          Relationships
          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            className="ml-2 rounded-lg border border-white/15 bg-[#0b0d17] px-3 py-2"
          >
            <option value="all">All</option>
            <option value="calls">Calls</option>
            <option value="depends_on">Dependencies</option>
            <option value="reads_from">Reads</option>
            <option value="writes_to">Writes</option>
            <option value="unresolved">Unresolved</option>
          </select>
        </label>
      </div>

      <FlowContent
        key={`${props.projectId}:${props.endpointId}:${depth}`}
        {...props}
        depth={depth}
        filter={filter}
      />
    </section>
  );
}

function FlowContent({
  projectId,
  endpointId,
  depth,
  filter,
}: Props & { depth: number; filter: string }) {
  const [state, setState] = useState<State>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading" });

    async function load() {
      try {
        const response = await fetch(
          `/api/projects/${projectId}/endpoints/${endpointId}/flow?depth=${depth}`,
          {
            cache: "no-store",
            signal: controller.signal,
          },
        );

        if (!response.ok) {
          const body = await response.json().catch(() => null);
          throw new Error(
            typeof body?.detail === "string"
              ? body.detail
              : `Could not load flow (${response.status})`,
          );
        }

        const flow: EndpointFlowData = await response.json();

        if (!controller.signal.aborted) {
          setState({ status: "ready", flow });
        }
      } catch (cause) {
        if (!controller.signal.aborted) {
          setState({
            status: "error",
            message:
              cause instanceof Error ? cause.message : "Could not load flow",
          });
        }
      }
    }

    void load();
    return () => controller.abort();
  }, [projectId, endpointId, depth, attempt]);

  if (state.status === "loading") {
    return (
      <p role="status" className="mt-4 text-sm text-slate-400">
        Loading source flow…
      </p>
    );
  }

  if (state.status === "error") {
    return (
      <div className="mt-4">
        <p role="alert" className="text-sm text-amber-200">
          {state.message}
        </p>
        <button
          type="button"
          onClick={() => setAttempt((value) => value + 1)}
          className="mt-2 text-sm font-semibold text-brand-300"
        >
          Retry
        </button>
      </div>
    );
  }

  const { flow } = state;
  const byId = new Map(flow.entities.map((entity) => [entity.id, entity]));
  const name = (id: string) => {
    const entity = byId.get(id);
    return entity?.qualified_name ?? entity?.name ?? "Unknown entity";
  };

  const matching = flow.edges.filter((edge) => {
    if (edge.type === "exposes") return false;
    if (filter === "all") return true;
    if (filter === "unresolved") return edge.target_id === null;
    return edge.type === filter;
  });

  // Retain the entry link as context under every relationship filter.
  const displayed = [
    ...flow.edges.filter((edge) => edge.type === "exposes"),
    ...matching,
  ];

  return (
    <div className="mt-4">
      <p className="break-all font-mono text-xs text-slate-400">
        Revision: {flow.commit_sha}
      </p>
      <p role="status" className="mt-2 text-xs text-slate-400">
        {matching.length} matching downstream relationships. The
        route-to-handler link remains visible.
      </p>
      <p className="mt-2 text-xs text-slate-400">
        Filters hide relationships and can leave disconnected nodes.
      </p>

      <SourceFlowDiagram
        key={`${flow.root_id}:${depth}:${filter}`}
        flow={flow}
        edges={displayed}
      />

      {matching.length === 0 && (
        <p className="mt-4 text-sm text-amber-200">
          No downstream relationships match this filter in the returned slice.
          This does not prove that the code makes no other calls.
        </p>
      )}

      <details open className="mt-5">
        <summary className="cursor-pointer text-sm font-semibold text-white">
          Text relationship view ({displayed.length})
        </summary>
        <ul className="mt-3 space-y-3">
          {displayed.map((edge) => (
            <li key={edge.id} className="rounded-xl border border-white/10 p-4">
              <p className="break-all font-mono text-sm text-white">
                {name(edge.source_id)} →{" "}
                {edge.target_id
                  ? name(edge.target_id)
                  : (edge.target_hint ?? "Unresolved target")}
              </p>
              <p className="mt-2 text-xs text-brand-300">
                {edge.type} · Confidence: {edge.confidence}
              </p>

              {edge.type === "depends_on" && (
                <p className="mt-2 text-xs text-slate-300">
                  Declared dependency
                  {edge.properties?.parameter
                    ? ` for parameter "${edge.properties.parameter}"`
                    : ""}
                  . This declaration does not establish runtime execution.
                </p>
              )}

              {edge.type === "calls" && (
                <div className="mt-2">
                  <p className="text-xs font-semibold text-slate-200">
                    Category: {callCategoryLabel(edge)}
                  </p>

                  {edge.properties?.classification_reason && (
                    <p className="mt-1 text-xs leading-5 text-slate-400">
                      {edge.properties.classification_reason}
                    </p>
                  )}
                </div>
              )}
              <p className="mt-2 break-all text-xs text-slate-400">
                Analyzer rule: {edge.provenance}
              </p>
              <p className="mt-2 break-all text-xs text-slate-400">
                {edge.location
                  ? `${edge.location.path}:${edge.location.start_line}–${edge.location.end_line}`
                  : "Source location unavailable"}
              </p>
              {edge.unresolved_reason && (
                <p className="mt-2 text-xs text-amber-200">
                  Unresolved: {edge.unresolved_reason}
                </p>
              )}
              {edge.source_url && (
                <a
                  href={edge.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-block text-sm font-semibold text-brand-300 hover:underline"
                >
                  Inspect relationship source ↗
                </a>
              )}
            </li>
          ))}
        </ul>
      </details>

      {flow.depth_limited && (
        <p className="mt-4 text-sm text-amber-200">
          Further relationships exist beyond depth {flow.requested_depth}.
          {flow.requested_depth < 3
            ? " Increase the depth to explore further."
            : " This explorer supports a maximum depth of three."}
        </p>
      )}

      {flow.truncated && (
        <p className="mt-4 text-sm text-amber-200">
          Partial response: graph limits were reached. Limits are{" "}
          {flow.limits.max_nodes} entities and {flow.limits.max_edges}{" "}
          relationships.
        </p>
      )}

      {flow.warning_count > 0 && (
        <p className="mt-4 text-xs text-slate-400">
          {flow.warning_count} project-wide analysis warnings are available
          below the endpoint catalog.
        </p>
      )}
    </div>
  );
}
