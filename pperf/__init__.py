from .tracer import Tracer as Tracer
from .registry import register_metric as register_metric

_tracer = Tracer()
trace = _tracer.trace
summarize = _tracer.summarize
