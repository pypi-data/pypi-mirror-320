"""
Handle downloading datasets from our content URL
"""

from functools import partial

from .path import get_data_home
from .manifest import load_manifest
from ..cloud.download import download_zip
from .path import DIALECTS, LOWLIGHT, REDDIT, MOVIES, ESSAYS, AEGIS, NSFW

from ..exceptions import DatasetsError


def download_data(
    url, signature, data_home=None, replace=False, extract=True, progress=True
):
    """
    Downloads the zipped data set specified at the given URL, saving it to
    the data directory specified by ``get_data_home``. This function verifies
    the download with the given signature and extracts the archive.
    """
    data_home = get_data_home(data_home)
    download_zip(
        url, data_home, signature, replace=replace, extract=extract, progress=progress
    )


def _download_dataset(
    name, sample=True, data_home=True, replace=False, extract=True, progress=True
):
    """
    Downloads the zipped data set specified using the manifest URL, saving it to the
    data directory specified by ``get_data_home``. The download is verified with
    the given signature then extracted.
    """
    if sample and not name.endswith("-sample"):
        name = name + "-sample"

    datasets = load_manifest()
    if name not in datasets:
        raise DatasetsError(f"no dataset named {name} exists")

    info = datasets[name]
    info.update({
        "data_home": data_home,
        "replace": replace,
        "extract": extract,
        "progress": progress,
    })
    download_data(**info)


download_dialects = partial(_download_dataset, DIALECTS)
download_lowlight = partial(_download_dataset, LOWLIGHT)
download_reddit = partial(_download_dataset, REDDIT)
download_movies = partial(_download_dataset, MOVIES)
download_essays = partial(_download_dataset, ESSAYS)
download_aegis = partial(_download_dataset, AEGIS)
download_nsfw = partial(_download_dataset, NSFW)


DOWNLOADERS = [
    download_dialects,
    download_lowlight,
    download_reddit,
    download_movies,
    download_essays,
    download_aegis,
    download_nsfw,
]


def download_all_datasets(
    sample=True, data_home=True, replace=True, extract=True, progress=True
):
    for f in DOWNLOADERS:
        f(
            sample=sample,
            data_home=data_home,
            replace=replace,
            extract=extract,
            progress=progress,
        )
