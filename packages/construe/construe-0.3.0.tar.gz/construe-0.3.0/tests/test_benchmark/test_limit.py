import pytest
from construe.benchmark.limit import limit_generator

"""
Test the benchmark generator helpers.
"""


@pytest.mark.parametrize(
    "limit,expected",
    [
        (None, 10),
        (10, 10),
        (15, 10),
        (5, 5),
        (1, 1),
        (0, 0),
        (-10, 0),
    ],
)
def test_limit_generator(limit, expected):
    def sample_generator():
        for i in range(10):
            yield i

    gen = limit_generator(sample_generator(), limit=limit)
    assert len(list(gen)) == expected
