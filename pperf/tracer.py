import os
import atexit

from . import ascii
from .node import Node, render_topk
from .metric import Metric


class _NoopCtx:
    def __enter__(self):
        return

    def __exit__(self, *args):
        return False


_no_op = _NoopCtx()


class _TracerCtx:
    def __init__(self, instance: str, metric: Metric) -> None:
        parent = metric.ctx_var.get()
        self._node = Node(
            instance,
            metric.unit,
            parent,
            custom_stat_line=metric.child_stat_line if parent else metric.stat_line,
        )

        if parent and metric.prune_pct:
            parent.children.append(
                self._node
            )  # link eagerly — pruning needs full tree built top-down

        self._measure = metric.measure
        self._push = metric.push
        self._ctx_var = metric.ctx_var

        self._start = None

    def __enter__(self):
        self._token = self._ctx_var.set(self._node)
        self._start = self._measure()

    def __exit__(self, *args):
        end = self._measure()

        self._node.apply_measure(self._start, end, end - self._start)

        self._push(self._node)
        self._ctx_var.reset(self._token)
        return False


class _CompositeCtx:
    def __init__(self, *args) -> None:
        self.contexts = list(args)

    def __enter__(self):
        for ctx in self.contexts:
            ctx.__enter__()

    def __exit__(self, *args):
        for ctx in reversed(self.contexts):
            ctx.__exit__(*args)

        return False


class Tracer:
    def __init__(self, summary_topk: int = 10) -> None:
        self._enabled = int(os.environ.get("PPERF", 0)) > 0
        self._top_k = summary_topk

        from .registry import _metric_registry

        self.metrics: list[Metric] = _metric_registry

        if self._enabled:
            atexit.register(self.summarize)

    def trace(self, instance_name: str):
        if self._enabled:
            return _CompositeCtx(*(_TracerCtx(instance_name, m) for m in self.metrics))
        else:
            return _no_op

    def summarize(self) -> None:
        line = "=" * 80
        sections = ""
        for metric in self.metrics:
            spikes = render_topk(
                metric.nodes, k=self._top_k, prune_pct=metric.prune_pct
            )
            sections += (
                f"  Top {self._top_k} {metric.name} Spikes:\n"
                f"{spikes if spikes else f'{ascii.indent}(None)'}\n\n"
            )

        summary = f"\n{line}\n" f"Tracer Summary:\n\n{sections}{line}\n"
        print(summary)
