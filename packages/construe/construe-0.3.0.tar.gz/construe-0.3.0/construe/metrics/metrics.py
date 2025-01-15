"""
Measurements are the result of a benchmark run.

This module influenced by https://rtnl.link/hMNNI90KBGj
"""

import numpy as np
import dataclasses

from collections import defaultdict
from typing import cast, Optional, Any, Iterable, Dict, List, Tuple


# Measurement will include a warning if the distribution is suspect. All
# runs are expected to have some variation; these parameters set the thresholds.
_IQR_WARN_THRESHOLD = 0.1
_IQR_GROSS_WARN_THRESHOLD = 0.25


@dataclasses.dataclass(init=True, repr=False, eq=True, frozen=True)
class Metric:
    """
    Container information used to define a benchmark measurement.

    This class is similar to a pytorch TaskSpec.
    """

    label: Optional[str] = None
    sub_label: Optional[str] = None
    description: Optional[str] = None
    device: Optional[str] = None
    env: Optional[str] = None

    @property
    def title(self) -> str:
        """
        Best effort attempt at a string label for the metric.
        """
        if self.label is not None:
            return self.label + (f": {self.sub_label}" if self.sub_label else "")
        elif self.env is not None:
            return f"Metric for {self.env}" + (f" on {self.device}" if self.device else "")  # noqa
        return "Metric"

    def summarize(self) -> str:
        """
        Builds a summary string for printing the metric.
        """
        parts = [
            self.title,
            self.description or ""
        ]
        return "\n".join([f"{i}\n" if "\n" in i else i for i in parts if i])


_TASKSPEC_FIELDS = tuple(i.name for i in dataclasses.fields(Metric))


@dataclasses.dataclass(init=True, repr=False)
class Measurement:
    """
    The result of a benchmark measurement.

    This class stores one or more measurements of a given statement. It is similar to
    the pytorch measurement and provides convienence methods and serialization.
    """

    metric: Metric
    raw_metrics: List[float]
    per_run: int = 1
    units: Optional[str] = None
    metadata: Optional[Dict[Any, Any]] = None

    def __post_init__(self) -> None:
        self._sorted_metrics: Tuple[float, ...] = ()
        self._warnings: Tuple[str, ...] = ()
        self._median: float = -1.0
        self._mean: float = -1.0
        self._p25: float = -1.0
        self._p75: float = -1.0

    def __getattr__(self, name: str) -> Any:
        # Forward Metric fields for convenience.
        if name in _TASKSPEC_FIELDS:
            return getattr(self.task_spec, name)
        return super().__getattribute__(name)

    def _compute_stats(self) -> None:
        """
        Comptues the internal stats for the measurements if not already computed.
        """
        if self.raw_metrics and not self._sorted_metrics:
            self._sorted_metrics = tuple(sorted(self.metrics))
            _metrics = np.array(self._sorted_metrics, dtype=np.float64)
            self._median = np.quantile(_metrics, 0.5).item()
            self._mean = _metrics.mean()
            self._p25 = np.quantile(_metrics, 0.25).item()
            self._p75 = np.quantile(_metrics, 0.75).item()

            if not self.meets_confidence(_IQR_GROSS_WARN_THRESHOLD):
                self.__add_warning("This suggests significant environmental influence.")
            elif not self.meets_confidence(_IQR_WARN_THRESHOLD):
                self.__add_warning("This could indicate system fluctuation.")

    def __add_warning(self, msg: str) -> None:
        riqr = self.iqr / self.median * 100
        self._warnings += (
            f"  WARNING: Interquartile range is {riqr:.1f}% "
            f"of the median measurement.\n           {msg}",
        )

    @property
    def metrics(self) -> List[float]:
        return [m / self.per_run for m in self.raw_metrics]

    @property
    def median(self) -> float:
        self._compute_stats()
        return self._median

    @property
    def mean(self) -> float:
        self._compute_stats()
        return self._mean

    @property
    def iqr(self) -> float:
        self._compute_stats()
        return self._p75 - self._p25

    @property
    def has_warnings(self) -> bool:
        self._compute_stats()
        return bool(self._warnings)

    @property
    def title(self) -> str:
        return self.metric.title

    @property
    def env(self) -> str:
        return "Unspecified env" if self.metric.env is None else cast(str, self.metric.env)  # noqa

    @property
    def row_name(self) -> str:
        return self.sub_label or "[Unknown]"

    def meets_confidence(self, threshold: float = _IQR_WARN_THRESHOLD) -> bool:
        return self.iqr / self.median < threshold

    def to_array(self):
        return np.array(self.metrics, dtype=np.float64)

    @staticmethod
    def merge(measurements: Iterable["Measurement"]) -> List["Measurement"]:
        """
        Merge measurement replicas into a single measurement.

        This method will extrapolate per_run=1 and will not transfer metadata.
        """
        groups = defaultdict(list)
        for m in measurements:
            groups[m.metric].append(m)

        def merge_group(metric: Metric, group: List["Measurement"]) -> "Measurement":
            metrics: List[float] = []
            for m in group:
                metrics.extend(m.metrics)

            return Measurement(
                per_run=1,
                raw_metrics=metrics,
                metric=metric,
                metadata=None
            )

        return [merge_group(t, g) for t, g in groups.items()]


def select_duration_unit(t: float) -> Tuple[str, float]:
    """
    Determine how to scale a duration to format for human readability.
    """
    unit = {-3: "ns", -2: "us", -1: "ms"}.get(int(np.log10(np.array(t)).item() // 3), "s")
    scale = {"ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1}[unit]
    return unit, scale


def humanize_duration(u: str) -> str:
    return {
        "ns": "nanosecond",
        "us": "microsecond",
        "ms": "millisecond",
        "s": "second",
    }[u]
