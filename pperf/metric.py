from types import FunctionType
from contextvars import ContextVar

from .node import Node, Nodes


class Metric:
    def __init__(
        self,
        name: str,
        unit: str,
        measure_fn: FunctionType,
        prune_pct: float = 0,
        stat_line: str = "",
        child_stat_line: str = "",
    ) -> None:
        self.name = name
        self.measure = measure_fn
        self.unit = unit
        self.prune_pct = prune_pct
        self.stat_line = stat_line
        self.child_stat_line = child_stat_line if child_stat_line else stat_line

        self.nodes: Nodes = Nodes()
        self.ctx_var: ContextVar[Node] = ContextVar(name, default=None)

    def push(self, node: Node):
        self.nodes.add(node)
