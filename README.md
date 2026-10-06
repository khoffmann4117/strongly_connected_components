# strongly_connected_components

Finds the strongly connected components of a directed graph using Tarjan's single-pass algorithm over a plain dict adjacency list.

## Usage

```python
from strongly_connected_components import strongly_connected_components

graph = {
    "a": ["b"],
    "b": ["c", "e"],
    "c": ["d"],
    "d": ["a"],
    "e": ["f"],
    "f": ["e"],
}

# A generator yielding each SCC as a list of nodes.
for component in strongly_connected_components(graph):
    print(component)
# ['e', 'f']
# ['d', 'c', 'b', 'a']
```

A second name, `tarjan_scc`, is exported as an alias for the same function — use whichever reads better at the call site.

## Why this exists

The problem: given a directed graph as a `dict[str, list[str]]`, enumerate its strongly connected components with no external dependencies and a predictable traversal order. The trade-off taken is Tarjan's single-pass algorithm over Kosaraju's two-pass variant: Tarjan makes one DFS traversal instead of two, at the cost of slightly more careful bookkeeping (`index`, `lowlink`, `on_stack`). For dict-based adjacency lists where the node set is the union of keys and successor values, the single pass also means we collect nodes and visit them in one pass rather than two.

Components are yielded bottom-up relative to the condensation DAG: a component's reachable descendants are emitted before the component itself. This ordering is a property of Tarjan's algorithm and is preserved here; if you need top-down order, reverse the output stream. Within a component, the node order is the order in which each node's self-recursion completed — deterministic for a given graph, but not sorted.

## The awkward edge

A node may appear only as a successor value and never as a key in the dict. This implementation treats every node that appears as a key OR as a successor value as a member of the graph, and yields each such node as part of some component (singleton if it has no path back to itself). If your caller expects every node to be a key, you must normalize the input yourself before calling this function — this library will not silently drop successor-only nodes.
