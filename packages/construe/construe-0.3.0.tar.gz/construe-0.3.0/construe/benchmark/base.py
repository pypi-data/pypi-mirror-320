"""
Defines the base class for all Benchmarks.
"""

import abc

from ..models import get_model_home
from ..datasets import get_data_home

from typing import Any, Generator, Dict, Union


class Benchmark(abc.ABC):
    """
    All benchmarks must subclass this class to ensure all properties and methods are
    correctly set for generic benchmarks to be run correctly.
    """

    @staticmethod
    @abc.abstractmethod
    def total(**kwargs):
        """
        For progress bar purposes should report the total number of instances in one
        run of the Benchmark. Generally this should be hard-coded but can also be
        computed if necessary.
        """
        pass

    def __init__(self, **kwargs):
        self._data_home = get_data_home(kwargs.pop("data_home", None))
        self._model_home = get_model_home(kwargs.pop("model_home", None))
        self._use_sample = kwargs.pop("use_sample", True)
        self._progress = kwargs.pop("progress", True)
        self._options = kwargs

    @property
    def data_home(self) -> str:
        if hasattr(self, "_data_home"):
            return self._data_home
        return get_data_home()

    @property
    def model_home(self) -> str:
        if hasattr(self, "_model_home"):
            return self._model_home
        return get_model_home()

    @property
    def use_sample(self) -> bool:
        return getattr(self, "_use_sample", True)

    @property
    def metadata(self) -> Dict:
        return getattr(self, "_metadata", None)

    @property
    def options(self) -> Union[Dict, None]:
        return getattr(self, "_options", {})

    @property
    @abc.abstractmethod
    def description(self):
        pass

    @abc.abstractmethod
    def before(self):
        """
        This method is called before the benchmark runs and should cause it to
        setup any datasets and models needed for the benchmark to run.
        """
        pass

    @abc.abstractmethod
    def after(self, cleanup: bool = True):
        """
        This method is called after the benchamrk is run; if cleanup is True the
        class should delete any cached datasets or models.
        """
        pass

    @abc.abstractmethod
    def instances(self, limit=None) -> Generator[Any, None, None]:
        """
        This method should yield all instances in the dataset at least once.
        """
        pass

    @abc.abstractmethod
    def preprocess(self, instance: Any) -> Any:
        """
        Any preprocessing that must be performed on an instance is handled with this
        method. This method is measured for latency and memory usage as well.
        """
        pass

    @abc.abstractmethod
    def inference(self, instance: Any) -> Any:
        """
        This represents the primary inference of the benchmark and is measured for
        latency and memory usage to add to the metrics.
        """
        pass
