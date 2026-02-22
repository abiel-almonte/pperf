import time
from .metric import Metric

_metric_registry = []


def register_metric(name: str, unit: str, **kwargs):

    def _register_metric(measure_fn):
        global _metric_registry
        _metric_registry.append(
            Metric(name=name, unit=unit, measure_fn=measure_fn, **kwargs)
        )

        return measure_fn

    return _register_metric


# preload metrics:
_t0 = time.perf_counter()

try:
    import torch

    @register_metric("Memory Allocated", "GB")
    def _get_memory_allocated_gb():
        b = torch.cuda.memory_allocated()
        return float(b * 1e-9)

    @register_metric("Memory Reserved", "GB")
    def _get_memory_reserved_gb():
        b = torch.cuda.memory_reserved()
        return float(b * 1e-9)

    @register_metric(
        "Latency",
        "ms",
        prune_pct=15,
        stat_line="{delta:.1f} ms",
        child_stat_line="{delta:.1f} ms ({pct}%)",
    )
    def _get_time_ms():
        torch.cuda.synchronize()
        return (time.perf_counter() - _t0) * 1e3

except ImportError:

    @register_metric(
        "Latency",
        "s",
        prune_pct=15,
        stat_line="{delta:.1f} s",
        child_stat_line="{delta:.1f} s ({pct}%)",
    )
    def _get_time_s():
        return time.perf_counter() - _t0
