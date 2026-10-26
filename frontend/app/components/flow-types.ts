export type SourceLocation = {
  path: string;
  start_line: number;
  end_line: number;
};

export type FlowEntity = {
  id: string;
  type: string;
  name: string;
  qualified_name: string | null;
  location: SourceLocation | null;
  source_url: string | null;
};

export type FlowEdge = {
  id: string;
  type: string;
  source_id: string;
  target_id: string | null;
  confidence: string;
  provenance: string;
  location: SourceLocation | null;
  source_url: string | null;
  unresolved_reason: string | null;
  target_hint: string | null;
  properties?: {
    call_category?: string;
    classification_reason?: string;
    parameter?: string;
    declaration_kind?: string;
    evidence_kind?: string;
  };
};

export type EndpointFlowData = {
  commit_sha: string;
  root_id: string;
  handler_id: string;
  entities: FlowEntity[];
  edges: FlowEdge[];
  node_depths: Record<string, number>;
  requested_depth: number;
  depth_limited: boolean;
  truncated: boolean;
  warning_count: number;
  limits: {
    max_nodes: number;
    max_edges: number;
  };
};

const CALL_CATEGORY_LABELS: Record<string, string> = {
  project_function: "Project function",
  imported_callable: "Imported callable",
  attribute_call: "Attribute call",
  dynamic_call: "Dynamic callable",
  unresolved_callable: "Unresolved callable",
};

export function callCategoryLabel(edge: FlowEdge): string {
  const category = edge.properties?.call_category;

  if (category && CALL_CATEGORY_LABELS[category]) {
    return CALL_CATEGORY_LABELS[category];
  }

  return edge.target_id === null ? "Unresolved target" : "Project target";
}
