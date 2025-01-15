"""
Utilities for construe
"""

from datetime import timedelta
from typing import Iterable, Set, Union


def resolve_exclude(
    exclude: Iterable[str] = None,
    include: Iterable[str] = None,
    all: Iterable[str] = None,
) -> Set[str]:
    """
    Given an exclusion list and an inclusion list, merge them to produce a definitive
    exclusion list such that if there are any inclusions, then everything not in the
    inclusion list from all is added to the exclusion list. If an item is both in the
    exclusion list and the inclusion list it is excluded.
    """
    exclude = exclude or []
    exclude = set([item.strip().lower() for item in exclude])

    include = include or []
    include = set([
        item.strip().lower() for item in include
    ])

    if include:
        for item in all:
            if item not in include:
                exclude.add(item)

    return exclude


def humanize_duration(duration: Union[int, float, timedelta]) -> str:
    """
    Represent a duration as a human readable string. If an int or a float are passed
    then it is assumed to be in seconds.
    """
    if not isinstance(duration, timedelta):
        duration = timedelta(seconds=duration)

    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
