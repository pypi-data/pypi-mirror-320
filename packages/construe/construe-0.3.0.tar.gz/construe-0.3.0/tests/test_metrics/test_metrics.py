"""
Testing for the metrics module.
"""

import pytest

from construe.metrics import Metric, Measurement
from construe.metrics import select_duration_unit


class TestMetric(object):
    """
    Metric dataclass tests
    """

    @pytest.mark.parametrize(
        "metric,expected",
        [
            (Metric(), "Metric"),
            (Metric(label="Foo"), "Foo"),
            (Metric(label="Foo", sub_label="Bar"), "Foo: Bar"),
            (Metric(env="MediaTek"), "Metric for MediaTek"),
            (Metric(env="MediaTek", device="tflite"), "Metric for MediaTek on tflite"),
        ],
    )
    def test_title(self, metric, expected):
        """
        Test title rendering
        """
        assert metric.title == expected


@pytest.mark.usefixtures("completed_benchmark")
class TestMeasurement(object):
    """
    Measurement dataclass tests
    """

    def test_per_run_default(self):
        """
        Assert that per_run is one by default
        """
        m = Measurement(metric=Metric(), raw_metrics=[1, 2, 3])
        assert m.per_run == 1, "per run is not set to one!"

    def test_stats(self):
        """
        Test stats calculations of measurement
        """
        assert self.measurement.median == 23.260444076123438
        assert self.measurement.mean == 23.112752271750523
        assert self.measurement.iqr == 8.44631785879561


@pytest.mark.parametrize(
    "t,expected",
    [
        (1.000, ("s", 1)),
        (5.000, ("s", 1)),
        (10.000, ("s", 1)),
        (50.000, ("s", 1)),
        (100.000, ("s", 1)),
        (500.000, ("s", 1)),
        (0.1, ("ms", 1e-3)),
        (0.6, ("ms", 1e-3)),
        (0.01, ("ms", 1e-3)),
        (0.03, ("ms", 1e-3)),
        (0.001, ("ms", 1e-3)),
        (0.004, ("ms", 1e-3)),
        (0.0001, ("us", 1e-6)),
        (0.0008, ("us", 1e-6)),
        (0.00001, ("us", 1e-6)),
        (0.00002, ("us", 1e-6)),
        (0.000001, ("us", 1e-6)),
        (0.000007, ("us", 1e-6)),
        (0.0000001, ("ns", 1e-9)),
        (0.0000009, ("ns", 1e-9)),
        (0.00000001, ("ns", 1e-9)),
        (0.00000005, ("ns", 1e-9)),
        (0.000000001, ("ns", 1e-9)),
        (0.000000003, ("ns", 1e-9)),
    ],
)
def test_select_duration_unit(t, expected):
    assert select_duration_unit(t) == expected
