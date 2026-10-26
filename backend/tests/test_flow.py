import unittest

from app.projects.flow import build_flow_slice


def entity(identifier):
    return {
        "id": identifier,
        "name": identifier,
    }


def edge(identifier, source, target, relation="calls"):
    return {
        "id": identifier,
        "type": relation,
        "source_id": source,
        "target_id": target,
    }


def graph():
    return {
        "entities": [
            entity("route"),
            entity("handler"),
            entity("service"),
            entity("repository"),
        ],
        "edges": [
            edge("exposes", "route", "handler", "exposes"),
            edge("call-service", "handler", "service"),
            edge("call-repository", "service", "repository"),
            edge("recursive-call", "repository", "handler"),
            edge("unknown-call", "handler", None),
        ],
    }


class FlowSliceTests(unittest.TestCase):
    def test_one_level_keeps_unresolved_relationships(self):
        result = build_flow_slice(graph(), "route", "handler", depth=1)

        self.assertEqual(
            {item["id"] for item in result["entities"]},
            {"route", "handler", "service"},
        )
        self.assertEqual(
            {item["id"] for item in result["edges"]},
            {"exposes", "call-service", "unknown-call"},
        )
        self.assertTrue(result["depth_limited"])

    def test_deeper_flow_handles_cycles(self):
        result = build_flow_slice(graph(), "route", "handler", depth=3)

        self.assertEqual(len(result["entities"]), 4)
        self.assertEqual(len(result["edges"]), 5)
        self.assertFalse(result["depth_limited"])
        self.assertFalse(result["truncated"])

    def test_node_limit_does_not_create_dangling_targets(self):
        result = build_flow_slice(
            graph(),
            "route",
            "handler",
            depth=3,
            max_nodes=2,
        )

        known = {item["id"] for item in result["entities"]}

        self.assertTrue(result["truncated"])
        self.assertEqual(known, {"route", "handler"})

        for relationship in result["edges"]:
            target = relationship["target_id"]
            self.assertTrue(target is None or target in known)

    def test_relationship_limit_is_reported(self):
        result = build_flow_slice(
            graph(),
            "route",
            "handler",
            max_edges=1,
        )

        self.assertEqual(len(result["edges"]), 1)
        self.assertTrue(result["truncated"])

    def test_repeated_traversal_is_stable(self):
        first = build_flow_slice(graph(), "route", "handler", depth=3)
        second = build_flow_slice(graph(), "route", "handler", depth=3)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
