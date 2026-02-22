import heapq
from typing import Optional

from . import ascii


class Node:
    def __init__(
        self,
        name: str,
        unit: str,
        parent: Optional["Node"] = None,
        custom_stat_line: str = "",
    ) -> None:
        self.parent = parent

        if parent is None:
            header = ascii.indent + "[{{section:>2}}]  "
        else:
            header = "{{prefix}}{{connector}} "

        self.line = (
            header
            + name
            + "__SPACER__"
            + (
                custom_stat_line
                if custom_stat_line
                else f"{{t0:.2f}} {unit} {ascii.arrow} {{t1:.2f}} {unit} ({{delta:.4f}} {ascii.delta})"
            )
        )

        self.delta = 0
        self.children: list[Node] = []

    def apply_measure(self, t0, t1, delta):
        # parent delta isn't known yet, so pct is deferred to _render_tree

        self.line = self.line.format(t0=t0, t1=t1, delta=delta, pct="{pct:.0f}")
        self.delta = delta

    def __lt__(self, other: "Node"):
        return self.delta > other.delta  # reverse for max heap


class Nodes:
    def __init__(self) -> None:
        self._heap: list[Node] = []

    def add(self, node: Node) -> None:
        heapq.heappush(self._heap, node)

    def __contains__(self, node: Node):
        return node in self._heap

    def __iter__(self):
        return self

    def __next__(self) -> Node:
        if not self._heap:
            raise StopIteration
        return heapq.heappop(self._heap)

    def __len__(self):
        return len(self._heap)


def _connect_upwards(node: Node):
    if node.parent is None:
        return node

    parent = node.parent
    if node not in parent.children:
        parent.children.append(node)  # claim our parent

    return _connect_upwards(parent)


def _render_tree(
    node: Node,
    prefix: str = "",
    last_child: bool = False,
    prune_pct: float = 0,
) -> str:

    if node.parent:
        node.line = node.line.format_map(
            dict(
                prefix=prefix,
                connector=ascii.corner if last_child else ascii.tee,
                pct=(
                    (node.delta / node.parent.delta) * 100
                    if node.parent.delta
                    else ascii.horz
                ),
            )
        )
        prefix += ascii.indent if last_child else (ascii.vert + f"   ")  # connect tees

    node.line = node.line.replace("__SPACER__", ascii.build_spacer(node.line))
    line = node.line + "\n"

    visible = [
        child
        for child in node.children
        if not prune_pct
        or not node.delta
        or (child.delta / node.delta) * 100 >= prune_pct
    ]

    for ci, child in enumerate(visible):
        line += _render_tree(
            node=child,
            prefix=prefix,
            last_child=ci == len(visible) - 1,
            prune_pct=prune_pct,
        )

    return line


def render_topk(nodes: Nodes, k: int = 1, prune_pct: float = 0):
    root_nodes: Nodes = Nodes()

    for leaf_node in nodes:

        root = _connect_upwards(leaf_node)
        if root not in root_nodes:
            root_nodes.add(root)

        if len(root_nodes) >= k:
            break

    lines = ""
    for i, root in enumerate(root_nodes):
        root.line = root.line.format(section=i + 1)

        lines += _render_tree(root, prefix=ascii.indent * (1 + 2), prune_pct=prune_pct)

    return lines
