"""
Benchmark ABC and global benchmark runner.
"""

import time
import dataclasses

from .base import Benchmark
from ..utils import humanize_duration
from ..metrics import Metric, Measurement, dump
from ..exceptions import ConstrueError, BenchmarkError

from tqdm import tqdm
from datetime import datetime, timezone
from typing import Iterable, List, Dict, Optional, Type


DATEFMT = "%Y-%m-%dT%H:%M:%S.%fZ"


class BenchmarkRunner(object):
    """
    Executes one or more benchmarks, configuring them with a top-level config and
    collecting all measurements, merging as necessary and outputing them to a file.
    """

    def __init__(
        self,
        benchmarks: List[Benchmark],
        device: str = None,
        env: str = None,
        n_runs: int = 1,
        limit: int = None,
        data_home: str = None,
        model_home: str = None,
        use_sample: bool = True,
        cleanup: bool = True,
        verbose: bool = True,
    ):
        self.env = env
        self.device = device
        self.n_runs = n_runs
        self.limit = limit
        self.benchmark_kwargs = {
            "data_home": data_home,
            "model_home": model_home,
            "use_sample": use_sample,
            "progress": verbose,
        }
        self.cleanup = cleanup
        self.verbose = verbose
        self.benchmarks = benchmarks

        for b in self.benchmarks:
            if not issubclass(b, Benchmark):
                raise BenchmarkError(f"{b.__name__} is not a Benchmark")

    @property
    def is_complete(self):
        return getattr(self, "run_complete_", False)

    def run(self):
        self.results_ = Results(
            n_runs=self.n_runs,
            limit=self.limit,
            benchmarks=[b.__name__ for b in self.benchmarks],
            started=datetime.now(timezone.utc).strftime(DATEFMT),
            env=self.env,
            device=self.device,
            options=self.benchmark_kwargs,
            errors=[],
        )

        self.run_complete_ = False
        self.measurements_ = []

        started = time.time()

        for cls in self.benchmarks:
            total = self.limit or cls.total(**self.benchmark_kwargs)
            for i in range(self.n_runs):
                self.run_benchmark(i, total, cls)

        self.results_.duration = time.time() - started
        self.results_.measurements = Measurement.merge(self.measurements_)
        self.run_complete_ = True

        if self.verbose:
            print(f"{len(self.benchmarks)} benchmark(s) complete in {humanize_duration(self.results_.duration)}")
            if self.cleanup:
                print("cleaned up data and model caches: all downloaded data removed")

    def run_benchmark(self, idx: int, total: int, Runner: Type):
        # TODO: do we need to pass separate metadata to the kwargs?
        progress = tqdm(total=total, desc=f"Running {Runner.__name__} Benchmark {idx+1}", leave=False)
        benchmark = Runner(**self.benchmark_kwargs)

        try:
            for measurement in self.execute(idx, benchmark, progress):
                self.measurements_.append(measurement)
                self.results_.successes += 1
        except ConstrueError as e:
            self.results_.failures += 1
            self.results_.errors.append(str(e))

    def execute(self, idx: int, benchmark: Benchmark, progress: tqdm) -> Iterable[Measurement]:
        # Setup the benchmark
        benchmark.before()

        ptimes = []  # preproccess times
        itimes = []  # inference times

        try:
            # Time each inference
            # TODO: measure memory usage during inferencing
            for instance in benchmark.instances(limit=self.limit):
                t1 = time.time()
                features = benchmark.preprocess(instance)
                t2 = time.time()
                benchmark.inference(features)
                t3 = time.time()

                ptimes.append(t2 - t1)
                itimes.append(t3 - t2)
                progress.update(1)
        finally:
            # Ensure benchmark is cleaned up despite any errors if this is the last
            # run of the benchmark and cleanup is specified (otherwise leave cache).
            cleanup = self.cleanup and idx == self.n_runs - 1
            benchmark.after(cleanup=cleanup)

        # Create the process times measurement
        yield Measurement(
            per_run=1,
            raw_metrics=ptimes,
            units="s",
            metric=Metric(
                label=benchmark.__class__.__name__,
                sub_label="preprocessing",
                description=benchmark.description,
                device=self.device,
                env=self.env,
            ),
        )

        # Create the inference times measurement
        yield Measurement(
            per_run=1,
            raw_metrics=itimes,
            units="s",
            metric=Metric(
                label=benchmark.__class__.__name__,
                sub_label="inferencing",
                description=benchmark.description,
                device=self.device,
                env=self.env,
            ),
        )

    def save(self, path):
        if not self.is_complete:
            raise BenchmarkError("cannot save benchmarks that haven't been run")

        with open(path, "w") as o:
            dump(self.results_, o)

        if self.verbose:
            print("benchmark results saved to", path)


@dataclasses.dataclass(init=True, repr=False, eq=True)
class Results:
    """
    A result of all runs of a Benchmark including benchmarking information.
    """

    n_runs: int
    benchmarks: List[str]
    started: str
    errors: List[str] = list
    limit: Optional[int] = None
    duration: Optional[float] = None
    env: Optional[str] = None
    device: Optional[str] = None
    options: Optional[Dict] = None
    successes: Optional[int] = 0
    failures: Optional[int] = 0
    measurements: Optional[List[Measurement]] = None
