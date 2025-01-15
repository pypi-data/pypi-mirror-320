"""
This module handles downloading data from original data sources and converting them
into the source format expected by the construe library.
"""

import os
import json
import random
import shutil
import zipfile
import soundfile as sf

from .path import FIXTURES
from .download import CHUNK

from datasets import Audio
from functools import partial
from datasets import load_dataset
from urllib.request import urlopen
from click.exceptions import UsageError


AEGIS = "aegis"
AEGIS_BASENAME = "aegis.zip"
AEGIS_ZIPNAME = "aegis.jsonl"
AEGIS_DATASET_URL = "nvidia/Aegis-AI-Content-Safety-Dataset-1.0"

LOWLIGHT = "lowlight"
LOWLIGHT_BASENAME = "lowlight.zip"
LOWLIGHT_DATASET_URL = (
    "https://drive.google.com/uc?id=1DdGIJ4PZPlF2ikl8mNM9V-PdVxVLbQi6"
)

DIALECTS = "dialects"
DIALECTS_BASENAME = "dialects.zip"
DIALECTS_DATASET_URL = "ylacombe/english_dialects"

REDDIT = "reddit"
REDDIT_BASENAME = "reddit.zip"
REDDIT_ZIPNAME = "reddit.jsonl"
REDDIT_DATASETS_URL = "ummagumm-a/reddit_posts_comments"

ESSAYS = "essays"
ESSAYS_BASENAME = "essays.zip"
ESSAYS_ZIPNAME = "essays.jsonl"
ESSAYS_DATASETS_URL = "knarasi1/student_and_llm_essays"

NSFW = "nsfw"
NSFW_BASENAME = "nsfw.zip"
NSFW_DATASETS_URL = "zanderlewis/nsfw_detection_large"

MOVIES = "movies"
MOVIES_BASENAME = "movies.zip"
MOVIES_DATASETS_URL = "unography/movie-scenes"

SOURCE_DATASETS = [
    AEGIS, LOWLIGHT, DIALECTS, REDDIT, ESSAYS, NSFW, MOVIES
]


##########################################################################
## Downloaders
##########################################################################

def download_source_datasets(out=FIXTURES, exclude=None):
    """
    Download all source datasets to the specified out directory,
    excluding any by name in the downloaders dictionary.
    """
    downloaders = {
        AEGIS: download_aegis,
        LOWLIGHT: download_lowlight,
        DIALECTS: download_dialects,
        REDDIT: download_reddit,
        ESSAYS: download_essays,
        NSFW: download_nsfw,
        MOVIES: download_movies,
    }

    exclude = exclude or []
    exclude = set([
        item.strip().lower() for item in exclude
    ])

    # Always exclude lowlight for now
    exclude.add("lowlight")

    for name, download in downloaders.items():
        if name in exclude:
            continue
        download(out=out)


def download_aegis(out=FIXTURES):
    """
    Download the AEGIS AI safety dataset from hugging faced and save as
    a zip compressed json lines file.
    """
    path = os.path.join(out, AEGIS_BASENAME)
    ds = load_dataset(AEGIS_DATASET_URL, split=None)
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        with z.open(AEGIS_ZIPNAME, "w") as d:
            for split in ds.values():
                for row in split:
                    d.write(json.dumps(row).encode("utf-8"))
                    d.write("\n".encode("utf-8"))


def download_lowlight(url=LOWLIGHT_DATASET_URL, out=FIXTURES):
    """
    Download the lowlight dataset from Google Drive.

    NOTE: this dataset needs to be downloaded manually from a browser
    because a javascript button click is necessary to start the download.
    """
    path = os.path.join(out, LOWLIGHT_BASENAME)

    response = urlopen(url)
    with open(path, "wb") as f:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)

    # TODO: unzip the download and create only one folder with all
    # the high and low photos without separation.


def download_dialects(out=FIXTURES):
    configs = [
        "irish_male",
        "midlands_female",
        "midlands_male",
        "northern_female",
        "northern_male",
        "scottish_female",
        "scottish_male",
        "southern_female",
        "southern_male",
        "welsh_female",
        "welsh_male",
    ]

    dirname, _ = os.path.splitext(DIALECTS_BASENAME)
    dir = os.path.join(out, dirname)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for config in configs:
        ds = load_dataset(DIALECTS_DATASET_URL, config)
        cdir = os.path.join(dir, config)
        if not os.path.exists(cdir):
            os.makedirs(cdir)

        for split in ds.values():
            split = split.cast_column("audio", Audio(sampling_rate=16000))
            for row in split:
                path = os.path.join(cdir, row["audio"]["path"])
                audio = row["audio"]["array"] * 32767
                audio = audio.astype('int16')
                sf.write(path, audio, 16000)

    shutil.make_archive(dir, "zip", dir)


def download_reddit(out=FIXTURES):
    path = os.path.join(out, REDDIT_BASENAME)
    ds = load_dataset(REDDIT_DATASETS_URL, split=None)
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        with z.open(REDDIT_ZIPNAME, "w") as d:
            for split in ds.values():
                for row in split:
                    d.write(json.dumps(row).encode("utf-8"))
                    d.write("\n".encode("utf-8"))


def download_essays(out=FIXTURES):
    path = os.path.join(out, ESSAYS_BASENAME)
    ds = load_dataset(ESSAYS_DATASETS_URL, split=None)
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        with z.open(ESSAYS_ZIPNAME, "w") as d:
            for split in ds.values():
                for row in split:
                    d.write(json.dumps(row).encode("utf-8"))
                    d.write("\n".encode("utf-8"))


def download_nsfw(out=FIXTURES):
    img = 0
    path = os.path.join(out, NSFW_BASENAME)
    fname, _ = os.path.splitext(NSFW_BASENAME)
    ds = load_dataset(NSFW_DATASETS_URL, split=None)

    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for split in ds.values():
            for row in split:
                img += 1
                folder = "nsfw" if row["label"] == 0 else "safe"
                imgpath = os.path.join(fname, folder, f"img{img:0>3}.jpg")
                with z.open(imgpath, "w") as d:
                    image = row["image"]
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(d, format="jpeg")


def download_movies(out=FIXTURES):
    img = 0
    path = os.path.join(out, MOVIES_BASENAME)
    fname, _ = os.path.splitext(MOVIES_BASENAME)
    ds = load_dataset(MOVIES_DATASETS_URL, split=None)

    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for split in ds.values():
            for row in split:
                img += 1
                imgpath = os.path.join(fname, f"img{img:0>6}.jpg")
                with z.open(imgpath, "w") as d:
                    image = row["image"]
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(d, format="jpeg")


##########################################################################
## Sampling
##########################################################################


def sample_source_datasets(
    datasets, fixtures=FIXTURES, out=FIXTURES, size=0.25, suffix="-sample"
):
    """
    Sample the specified datasets creating a smaller dataset for benchmarking.
    """
    samplers = {
        AEGIS: sample_aegis,
        LOWLIGHT: sample_lowlight,
        DIALECTS: sample_dialects,
        REDDIT: sample_reddit,
        ESSAYS: sample_essays,
        NSFW: sample_nsfw,
        MOVIES: sample_movies,
    }

    # Check that the samplers are available
    for dataset in datasets:
        dataset = dataset.strip().lower()
        if dataset not in samplers:
            raise UsageError(f"unknown dataset '{dataset}': cannot run sampler")

    # Execute samplers
    for dataset in datasets:
        dataset = dataset.strip().lower()
        samplers[dataset](fixtures, out, size, suffix)


def _sample_files(name, fixtures=FIXTURES, out=FIXTURES, size=0.25, suffix="-sample"):
    files_read, files_written = 0, 0
    inpath, outpath = _sample_paths(name, fixtures, out, suffix)

    with zipfile.ZipFile(inpath, "r") as zi:
        with zipfile.ZipFile(outpath, "x", compression=zipfile.ZIP_DEFLATED) as zo:
            for fp in zi.infolist():
                if fp.is_dir() or fp.filename.startswith("."):
                    continue

                with zi.open(fp.filename, "r") as f:
                    files_read += 1
                    if random.random() <= size:
                        with zo.open(fp.filename, "w") as o:
                            o.write(f.read())
                            files_written += 1

    print(f"sample {outpath} wrote {files_written} out of {files_read}")


def _sample_jsonl(name, fixtures=FIXTURES, out=FIXTURES, size=0.25, suffix="-sample"):
    fname, _ = os.path.splitext(name)
    fname += ".jsonl"

    lines_read, lines_written = 0, 0

    inpath, outpath = _sample_paths(name, fixtures, out, suffix)
    with zipfile.ZipFile(inpath, "r") as zi:
        with zipfile.ZipFile(outpath, "x", compression=zipfile.ZIP_DEFLATED) as zo:
            with zi.open(fname, "r") as f:
                with zo.open(fname, "w") as o:
                    for line in f:
                        lines_read += 1
                        if random.random() <= size:
                            o.write(line)
                            lines_written += 1

    print(f"sample {outpath} wrote {lines_written} out of {lines_read}")


def _sample_paths(name, fixtures, out, suffix):
    inpath = os.path.join(fixtures, name)
    basename, ext = os.path.splitext(name)
    outpath = os.path.join(out, f"{basename}{suffix}{ext}")

    if os.path.exists(outpath):
        os.remove(outpath)

    return inpath, outpath


sample_aegis = partial(_sample_jsonl, AEGIS_BASENAME)
sample_lowlight = partial(_sample_files, LOWLIGHT_BASENAME)
sample_dialects = partial(_sample_files, DIALECTS_BASENAME)
sample_reddit = partial(_sample_jsonl, REDDIT_BASENAME)
sample_essays = partial(_sample_jsonl, ESSAYS_BASENAME)
sample_nsfw = partial(_sample_files, NSFW_BASENAME)
sample_movies = partial(_sample_files, MOVIES_BASENAME)
