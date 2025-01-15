import pytest

from datetime import timedelta
from construe.utils import resolve_exclude
from construe.utils import humanize_duration


@pytest.mark.parametrize("exclude,include,expected", [
    (
        None, None, set(),
    ),
    (
        ["red", "orange", "black"], None, {"red", "orange", "black"},
    ),
    (
        None, ["red", "orange", "black"], {"blue", "green", "pink", "purple", "violet"},
    ),
    (
        ["red", "orange"], ["purple", "violet"], {"red", "blue", "orange", "green", "pink", "black"},
    ),
    (
        ["red", "orange"], ["red", "purple", "violet"], {"red", "blue", "orange", "green", "pink", "black"},
    )
])
def test_resolve_exclude(exclude, include, expected):
    """
    Test that exclusions are resolved correctly
    """
    ALL = [
        "red", "blue", "green", "pink", "purple", "orange", "violet", "black",
    ]
    resolved = resolve_exclude(exclude, include, ALL)
    assert resolved == expected


@pytest.mark.parametrize("duration,expected", [
    (0, "0s"),
    (59, "59s"),
    (60, "1m 0s"),
    (61, "1m 1s"),
    (3600, "1h 0m 0s"),
    (3661, "1h 1m 1s"),
    (86400, "1d 0h 0m 0s"),
    (90061, "1d 1h 1m 1s"),
    (timedelta(days=1, hours=1, minutes=1, seconds=1), "1d 1h 1m 1s"),
    (timedelta(seconds=59), "59s"),
    (timedelta(minutes=1), "1m 0s"),
    (timedelta(hours=1), "1h 0m 0s"),
])
def test_humanize_duration(duration, expected):
    """
    Test that durations are humanized correctly
    """
    assert humanize_duration(duration) == expected
