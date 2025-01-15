"""
Path handling for downloads
"""

import os
import shutil

from pathlib import Path
from ..cloud.signature import sha256sum
from construe.exceptions import DatasetsError


# Fixtures is where data being prepared is stored
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
MANIFEST = os.path.join(os.path.dirname(__file__), "manifest.json")

# Data dir is the location of downloaded datasets
DATADIR = Path.home() / ".construe" / "data"

# Names of the datasets
DIALECTS = "dialects"
LOWLIGHT = "lowlight"
REDDIT = "reddit"
MOVIES = "movies"
ESSAYS = "essays"
AEGIS = "aegis"
NSFW = "nsfw"


def get_data_home(path=None):
    """
    Return the path of the Construe data directory. This folder is used by
    dataset loaders to avoid downloading data several times.

    By default, this folder is colocated with the code in the install directory
    so that data shipped with the package can be easily located. Alternatively
    it can be set by the ``$CONSTRUE_DATA`` environment variable, or
    programmatically by giving a folder path. Note that the ``'~'`` symbol is
    expanded to the user home directory, and environment variables are also
    expanded when resolving the path.
    """
    if path is None:
        path = os.environ.get("CONSTRUE_DATA", DATADIR)

    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def find_dataset_path(dataset, data_home=None, fname=None, ext=None, raises=True):
    """
    Looks up the path to the dataset specified in the data home directory,
    which is found using the ``get_data_home`` function. By default data home
    is in a config directory in the user's home folder, but can be modified with the
    $CONSTRUE_DATA environment variable, or passing in a different directory.

    If the dataset is not found a ``DatasetsError`` is raised by default.
    """
    # Figure out the root directory of the datasets
    data_home = get_data_home(data_home)

    # Figure out the relative path to the dataset
    if fname is None:
        if ext is None:
            path = os.path.join(data_home, dataset)
        else:
            path = os.path.join(data_home, dataset, "{}{}".format(dataset, ext))
    else:
        path = os.path.join(data_home, dataset, fname)

    # Determine if the path exists
    if not os.path.exists(path):

        # Suppress exceptions if required
        if not raises:
            return None

        raise DatasetsError(
            f"could not find dataset at {path} - does it need to be downloaded?"
        )

    return path


def dataset_exists(dataset, data_home=None):
    """
    Checks to see if a directory with the name of the specified dataset exists
    in the data home directory, found with ``get_data_home``.
    """
    data_home = get_data_home(data_home)
    path = os.path.join(data_home, dataset)

    return os.path.exists(path) and os.path.isdir(path)


def dataset_archive(dataset, signature, data_home=None, ext=".zip"):
    """
    Checks to see if the dataset archive file exists in the data home directory,
    found with ``get_data_home``. By specifying the signature, this function
    also checks to see if the archive is the latest version by comparing the
    sha256sum of the local archive with the specified signature.
    """
    data_home = get_data_home(data_home)
    path = os.path.join(data_home, dataset + ext)

    if os.path.exists(path) and os.path.isfile(path):
        return sha256sum(path) == signature

    return False


def cleanup_dataset(dataset, data_home=None, ext=".zip"):
    """
    Removes the dataset directory and archive file from the data home directory.
    """
    removed = 0
    data_home = get_data_home(data_home)

    # Paths to remove
    datadir = os.path.join(data_home, dataset)
    archive = os.path.join(data_home, dataset + ext)

    # Remove directory and contents
    if os.path.exists(datadir):
        shutil.rmtree(datadir)
        removed += 1

    # Remove the archive file
    if os.path.exists(archive):
        os.remove(archive)
        removed += 1

    return removed
