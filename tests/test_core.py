import unittest

from strongly_connected_components import strongly_connected_components, tarjan_scc


class TestSCC(unittest.TestCase):
    def test_empty_graph_yields_nothing(self):
        self.assertEqual(list(strongly_connected_components({})), [])

    def test_single_isolated_node(self):
        graph = {"a": []}
        result = list(strongly_connected_components(graph))
        self.assertEqual(result, [["a"]])

    def test_single_self_loop_is_singleton_component(self):
        # A self-loop makes a SCC of size 1, not larger.
        graph = {"a": ["a"]}
        result = list(strongly_connected_components(graph))
        self.assertEqual(result, [["a"]])

    def test_simple_two_node_cycle(self):
        graph = {"a": ["b"], "b": ["a"]}
        result = list(strongly_connected_components(graph))
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result[0]), {"a", "b"})

    def test_dag_each_node_own_component(self):
        graph = {"a": ["b"], "b": ["c"], "c": []}
        result = list(strongly_connected_components(graph))
        self.assertEqual(sorted([sorted(c) for c in result]), [["a"], ["b"], ["c"]])

    def test_larger_graph_with_one_scc(self):
        # Classic textbook example with exactly one non-trivial SCC.
        graph = {
            "a": ["b"],
            "b": ["c", "e"],
            "c": ["d"],
            "d": ["a"],
            "e": ["f"],
            "f": ["e"],
        }
        result = [set(c) for c in strongly_connected_components(graph)]
        self.assertIn({"e", "f"}, result)
        self.assertIn({"a", "b", "c", "d"}, result)
        self.assertEqual(len(result), 2)

    def test_node_only_in_successor_values_is_included(self):
        # 'b' is never a key but appears as a successor. It must still be a node.
        graph = {"a": ["b"]}
        result = list(strongly_connected_components(graph))
        self.assertEqual(sorted([sorted(c) for c in result]), [["a"], ["b"]])

    def test_parallel_edges_are_tolerated(self):
        graph = {"a": ["b", "b"], "b": ["a", "a"]}
        result = list(strongly_connected_components(graph))
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result[0]), {"a", "b"})

    def test_nodes_with_self_loops_and_links(self):
        graph = {
            "a": ["a", "b"],
            "b": ["b"],
        }
        result = [set(c) for c in strongly_connected_components(graph)]
        self.assertIn({"a"}, result)
        self.assertIn({"b"}, result)
        self.assertEqual(len(result), 2)

    def test_disconnected_subgraphs(self):
        # Two independent cycles with no edges between them.
        graph = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
        }
        result = [set(c) for c in strongly_connected_components(graph)]
        self.assertEqual(len(result), 2)
        self.assertIn({"a", "b"}, result)
        self.assertIn({"c", "d"}, result)

    def test_three_node_cycle(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
        result = list(strongly_connected_components(graph))
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result[0]), {"a", "b", "c"})

    def test_nickname_matches_core_function(self):
        # The exported alias must behave identically to the named implementation.
        graph = {"a": ["b"], "b": ["a"], "c": []}
        self.assertEqual(
            [set(c) for c in strongly_connected_components(graph)],
            [set(c) for c in tarjan_scc(graph)],
        )

    def test_bottom_up_ordering_in_simple_dag(self):
        # In a DAG, bottom-up order means descendants come first. For A->B->C,
        # C must be yielded before B before A.
        graph = {"a": ["b"], "b": ["c"], "c": []}
        result = [c[0] for c in strongly_connected_components(graph)]
        self.assertEqual(result, ["c", "b", "a"])

    def test_singletons_yielded_bottom_up(self):
        # All singletons in a chain; each sink should appear before its parent.
        graph = {"a": ["b"], "b": ["c"], "c": ["d"], "d": []}
        result = [c[0] for c in strongly_connected_components(graph)]
        self.assertEqual(result, ["d", "c", "b", "a"])

    def test_duplicate_successor_lists_in_singleton(self):
        graph = {"a": ["b", "b"], "b": []}
        result = list(strongly_connected_components(graph))
        self.assertEqual(sorted([sorted(c) for c in result]), [["a"], ["b"]])


if __name__ == "__main__":
    unittest.main()
