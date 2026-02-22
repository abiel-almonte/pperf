`pperf` **- Hierarchical profiler for quick iteration**

Nest traces anywhere in your code. On exit, pperf surfaces the worst bottlenecks with their full call tree.

Enable with `PPERF=1`.

```python
import pperf

with pperf.trace(f"loop closure - kf: {count}"):
    ...
    with pperf.trace(f"apply update {step}"):
        ...
        with pperf.trace("gru"): ...
```

Output:
```
Tracer Summary:

    Top 1 Latency Spikes:
    [ 1]  loop closure - kf: 89 ─────────────────────────────│ 1102.5 ms
            └── apply update 0 ──────────────────────────────│ 171.0 ms (16%)
                ├── flow encoder ────────────────────────────│ 33.2 ms (19%)
                └── gru ─────────────────────────────────────│ 39.3 ms (23%)

    Top 1 Memory Reserved Spikes:
    [ 1]  loop closure - kf: 91 ─────────────────────────────│ 10.20 GB → 10.81 GB (0.6103 ∆)
            └── apply update 2 ──────────────────────────────│ 10.20 GB → 10.81 GB (0.6103 ∆)
                └── gru ─────────────────────────────────────│ 10.20 GB → 10.81 GB (0.6103 ∆)
```


Define what performance means for you:
```python
@register_metric("Queue Depth", unit="items")
def _queue_depth():
    return queue.qsize()
```

---

**pperf**, the practical profiler.