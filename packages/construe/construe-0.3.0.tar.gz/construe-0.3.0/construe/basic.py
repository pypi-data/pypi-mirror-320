"""
Benchmarks basic dot product torch operators.

See: https://pytorch.org/tutorials/recipes/recipes/benchmark.html
"""

import tqdm
import torch
import pickle
import torch.utils.benchmark as benchmark

from itertools import product
from torch.utils.benchmark import Fuzzer, FuzzedParameter, FuzzedTensor


def batched_dot_mul_sum(a, b):
    """
    Computes batched dot by multiplying and summing
    """
    return a.mul(b).sum(-1)


def batched_dot_bmm(a, b):
    """
    Computes batched dot by reducing to bmm
    """
    a = a.reshape(-1, 1, a.shape[-1])
    b = b.reshape(-1, b.shape[-1], 1)
    return torch.bmm(a, b).flatten(-3)


class BasicBenchmark(object):

    def __init__(self, env=None, saveto=None, num_threads=None, fuzz=False, seed=None):
        if num_threads is None:
            num_threads = torch.get_num_threads()

        self.env = env
        self.saveto = saveto
        self.num_threads = num_threads
        self.fuzz = fuzz
        self.seed = seed

    def run(self):
        results = []
        dataset = self.fuzzer().take(10) if self.fuzz else list(self.static())

        kwargs = {
            "label": "Batched Dot",
            "num_threads": self.num_threads,
            "env": self.env,
        }

        for tensors, tensor_params, params in tqdm.tqdm(dataset, leave=False):
            sub_label = f"{params['k0']:<6} x {params['k1']:<4} {'' if tensor_params['x']['is_contiguous'] else '(discontiguous)'}"  # noqa
            results.append(
                benchmark.Timer(
                    stmt="batched_dot_mul_sum(x, x)",
                    setup="from construe.basic import batched_dot_mul_sum",
                    globals=tensors,
                    sub_label=sub_label,
                    description="mul/sum",
                    **kwargs
                ).blocked_autorange(min_run_time=1)
            )
            results.append(
                benchmark.Timer(
                    stmt="batched_dot_bmm(x, x)",
                    setup="from construe.basic import batched_dot_bmm",
                    globals=tensors,
                    sub_label=sub_label,
                    description="bmm",
                    **kwargs
                ).blocked_autorange(min_run_time=1)
            )

        if self.saveto is not None:
            with open(self.saveto, "wb") as f:
                pickle.dump(results, f)

        compare = benchmark.Compare(results)
        compare.print()

    def fuzzer(self):
        """
        Generates random tensors with 128 to 10000000 elements and sizes k0 and k1
        chosen from a loguniform distribution in [1, 10000], 40% of which will be
        discontiguous on average.
        """
        return Fuzzer(
            parameters=[
                FuzzedParameter(
                    "k0", minval=1, maxval=10000, distribution="loguniform"
                ),
                FuzzedParameter(
                    "k1", minval=1, maxval=10000, distribution="loguniform"
                ),
            ],
            tensors=[
                FuzzedTensor(
                    "x",
                    size=("k0", "k1"),
                    min_elements=128,
                    max_elements=10000000,
                    probability_contiguous=0.6,
                )
            ],
            seed=self.seed,
        )

    def static(self):
        sizes = [16, 64, 1024, 16384]
        for k0, k1 in product(sizes, sizes):
            params = {
                "k0": k0,
                "k1": k1,
            }

            tensors = {
                "x": torch.ones((k0, k1))
            }

            tensor_params = {
                "x": {
                    "is_contiguous": True
                }
            }

            yield tensors, tensor_params, params
