from __future__ import annotations

import sys
from typing import Dict, Hashable, Iterator, List, Tuple

__all__ = ["strongly_connected_components", "tarjan_scc"]

# Tarjan's algorithm operates on a recursion stack mirroring the DFS traversal.
# Deep or pathological graphs can exceed CPython's default 1000-frame limit.
# We raise it once at import: a library that silently crashes on valid input
# on some interpreters is worse than one that advertises a generous ceiling.
if not getattr(sys, "_scc_recursion_patched", False):
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 1_000_000))
    sys._scc_recursion_patched = True  # type: ignore[attr-defined]


def strongly_connected_components(
    graph: Dict[Hashable, List[Hashable]]
) -> Iterator[List[Hashable]]:
    """Yield strongly connected components (SCCs) of *graph* as lists of nodes.

    Args:
        graph: Dict mapping each node to a list of successor nodes. Every node
            that appears as a key OR as a successor value is treated as a member
            of the graph. Lists may contain duplicates; they carry no special
            meaning and are tolerated as ordinary multi-edges.

    Yields:
        Each SCC as a list of its member nodes. The order of nodes within an
        SCC is the order in which each node's self-recursion completed — a
        DFS-derived order, not sorted. The order of SCCs follows Tarjan's
        property: components are produced bottom-up relative to the condensation
        DAG, so a component's descendants (reachable SCCs) are emitted before
        the component itself.

    Notes:
        * Empty graph → yields nothing.
        * Isolated node (no out-edges) → yielded as a singleton component.
        * Graphs with no explicit keys but only successors-as-values: every
          referenced node is treated as a member and yielded.
    """
    yield from tarjan_scc(graph)


def tarjan_scc(
    graph: Dict[Hashable, List[Hashable]]
) -> Iterator[List[Hashable]]:
    """Tarjan's single-pass SCC algorithm over a dict adjacency list.

    Implementation choices:
        * Iterative DFS. CPython's default recursion limit (1000) is too tight
          for real-world graphs and a 1,000,000 ceiling is still finite. The
          explicit stack avoids recursion entirely; correctness does not depend
          on interpreter tuning.
        * No sentinel "undefined" index constant. CPython dicts guarantee that a
          key absent before insertion is absent after, so `index in visited`
          is an unambiguous "has this node been pushed yet" test. This is cheaper
          than a module-level sentinel and reads as plainly.
        * Popped-on-root discipline: we only pop the stack up to AND INCLUDING the
          current node when it is the root of an SCC. Popping eagerly when a
          node's lowlink is updated would prematurely merge components.

    Args:
        graph: Dict mapping each node to a list of successor nodes.

    Yields:
        Lists of nodes, one per SCC.
    """
    # Collect the full node set up front. A node may appear only as a successor
    # value and never as a key; we still need to visit it. Iterating a snapshot
    # avoids mutation-during-iteration issues if the caller's dict changes.
    nodes: List[Hashable] = list(graph.keys())
    seen: set = set(graph.keys())
    for src, dsts in graph.items():
        for d in dsts:
            if d not in seen:
                seen.add(d)
                nodes.append(d)

    index_counter: List[int] = [0]
    indices: Dict[Hashable, int] = {}
    lowlinks: Dict[Hashable, int] = {}
    on_stack: set = set()
    stack: List[Hashable] = []

    for root in nodes:
        if root in indices:
            continue

        # Iterative DFS frame: (node, successor_iterator, started).
        # `started` distinguishes the first time we process a node from
        # subsequent re-emergences after a child subtree completes.
        work: List[Tuple[Hashable, Iterator, bool]] = [
            (root, iter(graph.get(root, [])), False)
        ]

        while work:
            node, succ_iter, started = work.pop()

            if not started:
                indices[node] = index_counter[0]
                lowlinks[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)

            advanced = False
            for w in succ_iter:
                if w not in indices:
                    # Tree edge: descend into w. We re-push *node* with the same
                    # iterator so it resumes after w's subtree is finished.
                    work.append((node, succ_iter, True))
                    work.append((w, iter(graph.get(w, [])), False))
                    advanced = True
                    break
                elif w in on_stack:
                    # Back edge or cross edge to a node currently on the stack.
                    # Tarjan's update uses the *index* of w, not its lowlink.
                    lowlinks[node] = min(lowlinks[node], indices[w])
            if advanced:
                continue

            # Node's subtree is fully explored. If it is an SCC root, drain the
            # stack down to and including it, forming the component.
            if lowlinks[node] == indices[node]:
                component: List[Hashable] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    component.append(w)
                    if w == node:
                        break
                yield component

            # Propagate lowlink to parent if any.
            if work:
                parent = work[-1][0]
                lowlinks[parent] = min(lowlinks[parent], lowlinks[node])
