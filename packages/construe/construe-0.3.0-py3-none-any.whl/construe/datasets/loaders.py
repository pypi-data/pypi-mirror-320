"""
Managers for loading datasets
"""

import os
import glob
import json
import shutil

from functools import partial

from .manifest import load_manifest
from .download import download_data
from ..exceptions import DatasetsError
from .path import find_dataset_path, get_data_home
from .path import dataset_archive, cleanup_dataset
from .path import DIALECTS, LOWLIGHT, REDDIT, MOVIES, ESSAYS, AEGIS, NSFW


__all__ = [
    "load_all_datasets", "cleanup_all_datasets",
    "load_dialects", "cleanup_dialects",
    "load_lowlight", "cleanup_lowlight",
    "load_reddit", "cleanup_reddit",
    "load_movies", "cleanup_movies",
    "load_essays", "cleanup_essays",
    "load_aegis", "cleanup_aegis",
    "load_nsfw", "cleanup_nsfw",
]


DATASETS = load_manifest()


def _info(dataset):
    if dataset not in DATASETS:
        raise DatasetsError(f"no dataset named {dataset} exists")
    return DATASETS[dataset]


def _load_prepare(name, sample=True, data_home=None):
    if sample and not name.endswith("-sample"):
        name = name + "-sample"

    info = _info(name)
    if not dataset_archive(name, info["signature"], data_home=data_home):
        # If the dataset does not exist, download and extract it
        info.update({"data_home": data_home, "replace": True, "extract": True})
        download_data(**info)

    return find_dataset_path(name, data_home=data_home, fname=None, ext=None)


def _load_file_dataset(name, sample=True, data_home=None):
    data_path = _load_prepare(name, sample=sample, data_home=data_home)
    for path in glob.glob(os.path.join(data_path, "**", "*")):
        yield path


def _load_jsonl_dataset(name, sample=True, data_home=None):
    data_path = _load_prepare(name, sample=sample, data_home=data_home)
    for path in glob.glob(os.path.join(data_path, "*.jsonl")):
        with open(path, "r") as f:
            for line in f:
                yield json.load(f)


def _cleanup_dataset(name, sample=True, data_home=None):
    if sample and not name.endswith("-sample"):
        name = name + "-sample"
    return cleanup_dataset(name, data_home=data_home)


load_dialects = partial(_load_file_dataset, DIALECTS)
cleanup_dialects = partial(_cleanup_dataset, DIALECTS)

load_lowlight = partial(_load_file_dataset, LOWLIGHT)
cleanup_lowlight = partial(_cleanup_dataset, LOWLIGHT)

load_reddit = partial(_load_jsonl_dataset, REDDIT)
cleanup_reddit = partial(_cleanup_dataset, REDDIT)

load_movies = partial(_load_file_dataset, MOVIES)
cleanup_movies = partial(_cleanup_dataset, MOVIES)

load_essays = partial(_load_jsonl_dataset, ESSAYS)
cleanup_essays = partial(_cleanup_dataset, ESSAYS)

load_aegis = partial(_load_jsonl_dataset, AEGIS)
cleanup_aegis = partial(_cleanup_dataset, AEGIS)

load_nsfw = partial(_load_file_dataset, NSFW)
cleanup_nsfw = partial(_cleanup_dataset, NSFW)


def load_all_datasets(sample=True, data_home=None):
    """
    Load all available datasets as defined by __all__
    """
    module = globals()
    for name in __all__:
        if not name.startswith("load"):
            continue

        if name == "load_all_datasets":
            continue

        f = module[name]
        for row in f(sample=sample, data_home=data_home):
            yield row


def cleanup_all_datasets(data_home=None):
    """
    Delete everything in the data home directory
    """
    with os.scandir(get_data_home(data_home)) as entries:
        for entry in entries:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)
