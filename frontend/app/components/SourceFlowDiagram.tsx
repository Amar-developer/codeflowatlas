"use client";

import { useId, useState } from "react";
import type { EndpointFlowData, FlowEdge } from "./flow-types";

import { callCategoryLabel } from "./flow-types";

type Props = {
  flow: EndpointFlowData;
  edges: FlowEdge[];
};

export default function SourceFlowDiagram({ flow, edges }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const arrowId = useId().replace(/:/g, "");

  const entities = new Map(flow.entities.map((entity) => [entity.id, entity]));

  const included = new Set([flow.root_id, flow.handler_id]);

  for (const edge of edges) {
    included.add(edge.source_id);

    if (edge.target_id !== null) {
      included.add(edge.target_id);
    }
  }

  const candidates = [
    ...flow.entities
      .filter((entity) => included.has(entity.id))
      .map((entity) => ({
        id: entity.id,
        label: entity.qualified_name ?? entity.name,
        kind: entity.type,
        level: flow.node_depths[entity.id] ?? 0,
        sourceUrl: entity.source_url,
        location: entity.location,
        unresolved: false,
        reason: null as string | null,
      })),
    ...edges
      .filter((edge) => edge.target_id === null)
      .map((edge) => ({
        id: `unresolved:${edge.id}`,
        label: edge.target_hint ?? "Unknown target",
        kind:
          edge.type === "depends_on"
            ? "Unresolved dependency"
            : callCategoryLabel(edge),
        level: (flow.node_depths[edge.source_id] ?? 1) + 1,
        sourceUrl: edge.source_url,
        location: edge.location,
        unresolved: true,
        reason: [edge.properties?.classification_reason, edge.unresolved_reason]
          .filter(Boolean)
          .join(" "),
      })),
  ].sort((a, b) => a.level - b.level || a.id.localeCompare(b.id));

  const diagramLimit = 40;
  const visible = candidates.slice(0, diagramLimit);
  const rows = new Map<number, number>();

  const nodes = visible.map((node) => {
    const row = rows.get(node.level) ?? 0;
    rows.set(node.level, row + 1);

    return {
      ...node,
      x: 20 + node.level * 310,
      y: 30 + row * 100,
    };
  });

  const positions = new Map(nodes.map((node) => [node.id, node]));
  const width = Math.max(650, ...nodes.map((node) => node.x + 270));
  const height = Math.max(220, ...nodes.map((node) => node.y + 100));
  const selected = nodes.find((node) => node.id === selectedId);

  return (
    <section className="mt-5" aria-label="Static source-flow diagram">
      <p className="text-xs leading-5 text-slate-400">
        Columns show shortest source-relationship distance from the endpoint,
        not execution order. Select a node for source evidence.
      </p>

      <div className="mt-3 overflow-auto rounded-xl border border-white/10 bg-[#0b0d17]">
        <svg
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          role="group"
          aria-label="Selectable source relationships"
        >
          <defs>
            <marker
              id={arrowId}
              viewBox="0 0 10 10"
              refX="9"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
            </marker>
          </defs>

          {edges.map((edge) => {
            const source = positions.get(edge.source_id);
            const target = positions.get(
              edge.target_id ?? `unresolved:${edge.id}`,
            );

            if (!source || !target) return null;

            const x1 = source.x + 240;
            const y1 = source.y + 30;
            const x2 = target.x;
            const y2 = target.y + 30;

            return (
              <path
                key={edge.id}
                d={`M ${x1} ${y1} C ${x1 + 45} ${y1}, ${
                  x2 - 45
                } ${y2}, ${x2} ${y2}`}
                stroke={edge.target_id ? "#64748b" : "#fbbf24"}
                strokeDasharray={edge.target_id ? undefined : "6 4"}
                strokeWidth="2"
                markerEnd={`url(#${arrowId})`}
                fill="none"
              >
                <title>
                  {edge.type} · {edge.confidence}
                </title>
              </path>
            );
          })}

          {nodes.map((node) => (
            <g
              key={node.id}
              role="button"
              tabIndex={0}
              aria-label={`${node.kind}: ${node.label}`}
              aria-pressed={selectedId === node.id}
              onClick={() => setSelectedId(node.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  setSelectedId(node.id);
                }
              }}
              className="cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-400"
            >
              <title>{node.label}</title>
              <rect
                x={node.x}
                y={node.y}
                width="240"
                height="60"
                rx="12"
                fill={selectedId === node.id ? "#1e3a5f" : "#172033"}
                stroke={node.unresolved ? "#fbbf24" : "#38bdf8"}
                strokeWidth={selectedId === node.id ? 3 : 1}
              />
              <text
                x={node.x + 12}
                y={node.y + 21}
                fill="#94a3b8"
                fontSize="11"
              >
                {node.kind}
              </text>
              <text
                x={node.x + 12}
                y={node.y + 43}
                fill="#f1f5f9"
                fontSize="12"
              >
                {node.label.length > 29
                  ? `${node.label.slice(0, 28)}…`
                  : node.label}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {selected && (
        <div
          aria-live="polite"
          className="mt-3 rounded-xl border border-white/10 p-4"
        >
          <p className="break-all font-mono text-sm text-white">
            {selected.label}
          </p>
          <p className="mt-2 text-xs text-slate-400">
            {selected.location
              ? `${selected.location.path}:${selected.location.start_line}–${selected.location.end_line}`
              : "Source location unavailable"}
          </p>

          {selected.reason && (
            <p className="mt-2 text-sm text-amber-200">{selected.reason}</p>
          )}

          {selected.sourceUrl && (
            <a
              href={selected.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-block text-sm font-semibold text-brand-300 hover:underline"
            >
              {selected.unresolved
                ? "Inspect unresolved call site"
                : "Open source at this revision"}{" "}
              ↗
            </a>
          )}
        </div>
      )}

      {candidates.length > diagramLimit && (
        <p className="mt-3 text-xs text-amber-200">
          Diagram shows {diagramLimit} of {candidates.length} matching nodes.
          The text view below includes all returned matching relationships.
        </p>
      )}
    </section>
  );
}
