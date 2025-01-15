"""
Handles limiting the output of generators.
"""

from typing import Generator, Optional


def limit_generator(generator: Generator, limit: Optional[int] = None) -> Generator:
    """
    Limit the output of a generator to a certain number of items.
    """
    if limit is None:
        yield from generator
        return

    for i, item in enumerate(generator):
        if i >= limit:
            return
        yield item
