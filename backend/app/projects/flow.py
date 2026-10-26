"""Bounded traversal of an already validated static IR document."""

from collections import defaultdict, deque

FLOW_RELATIONS = {
    "calls",
    "depends_on",
    "reads_from",
    "writes_to",
}


def build_flow_slice(
    graph: dict,
    root_id: str,
    handler_id: str,
    depth: int = 1,
    max_nodes: int = 100,
    max_edges: int = 200,
) -> dict:
    if not 1 <= depth <= 3:
        raise ValueError("depth must be between 1 and 3")

    if max_nodes < 2 or max_edges < 1:
        raise ValueError("limits must allow the endpoint and handler")

    entities = {entity["id"]: entity for entity in graph["entities"]}

    if root_id not in entities or handler_id not in entities:
        raise ValueError("endpoint or handler is missing")

    route_edges = [
        edge
        for edge in graph["edges"]
        if edge["type"] == "exposes"
        and edge["source_id"] == root_id
        and edge["target_id"] == handler_id
    ]

    if len(route_edges) != 1:
        raise ValueError("expected one route-to-handler relationship")

    outgoing = defaultdict(list)

    for edge in graph["edges"]:
        if edge["type"] in FLOW_RELATIONS:
            outgoing[edge["source_id"]].append(edge)

    for edges in outgoing.values():
        edges.sort(key=lambda edge: edge["id"])

    selected_nodes = {root_id, handler_id}
    selected_edges = {route_edges[0]["id"]: route_edges[0]}
    distances = {root_id: 0, handler_id: 1}

    # Distance here counts downstream hops from the handler.
    queue = deque([(handler_id, 0)])
    visited = {handler_id}
    boundary_edges = set()
    truncated = False

    while queue:
        source_id, hops = queue.popleft()

        if hops >= depth:
            boundary_edges.update(edge["id"] for edge in outgoing[source_id])
            continue

        for edge in outgoing[source_id]:
            if edge["id"] in selected_edges:
                continue

            if len(selected_edges) >= max_edges:
                truncated = True
                continue

            target_id = edge["target_id"]
            adds_node = target_id is not None and target_id not in selected_nodes

            if adds_node and len(selected_nodes) >= max_nodes:
                truncated = True
                continue

            selected_edges[edge["id"]] = edge

            # An unresolved relationship is retained without inventing a node.
            if target_id is None:
                continue

            selected_nodes.add(target_id)
            distances.setdefault(target_id, hops + 2)

            # Visiting each entity once prevents recursive calls from looping.
            if target_id not in visited:
                visited.add(target_id)
                queue.append((target_id, hops + 1))

    return {
        "entities": [entities[node_id] for node_id in sorted(selected_nodes)],
        "edges": [selected_edges[edge_id] for edge_id in sorted(selected_edges)],
        "node_depths": distances,
        "requested_depth": depth,
        "depth_limited": bool(boundary_edges - selected_edges.keys()),
        "truncated": truncated,
        "limits": {
            "max_nodes": max_nodes,
            "max_edges": max_edges,
        },
    }
