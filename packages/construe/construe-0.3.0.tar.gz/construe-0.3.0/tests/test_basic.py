"""
Tests for the basic benchmarking module.
"""

import torch

from construe.basic import *


def test_batched_dot():
    # Input for benchmarking
    x = torch.randn(10000, 64)

    # Ensure that both functions compute the same output
    assert batched_dot_mul_sum(x, x).allclose(batched_dot_bmm(x, x))
