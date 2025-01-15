"""
Path handling for model downloads
"""

import os
import shutil

from pathlib import Path
from ..cloud.signature import sha256sum
from construe.exceptions import ModelsError


# Fixtures is where model data being prepared is stored
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
MANIFEST = os.path.join(os.path.dirname(__file__), "manifest.json")

# Models dir is the location of downloaded model files
MODELSDIR = Path.home() / ".construe" / "models"

# Names of the models
MOONDREAM = "moondream"
WHISPER = "whisper"
MOBILENET = "mobilenet"
MOBILEVIT = "mobilevit"
NSFW = "nsfw"
LOWLIGHT = "lowlight"
OFFENSIVE = "offensive"
GLINER = "gliner"


def get_model_home(path=None):
    """
    Return the path of the Construe models directory. This folder is used by
    model loaders to avoid downloading model parameters several times.

    By default, this folder is in a config directory in the users home folderso the
    model can be can be easily located. Alternatively it can be set by the
    ``$CONSTRUE_MODELS`` environment variable, or programmatically by giving a folder
    path. Note that the ``'~'`` symbol is expanded to the user home directory, and
    environment variables are also expanded when resolving the path.
    """
    if path is None:
        path = os.environ.get("CONSTRUE_MODELS", MODELSDIR)

    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def find_model_path(model, model_home=None, fname=None, ext=None, raises=True):
    """
    Looks up the path to the model specified in the models home directory. The storage
    location of the models can be set with the $CONSTRUE_MODELS environment variable.

    If the model is not found a ``ModelsError`` is raised by default.
    """
    # Resolve the root directory that stores the models
    model_home = get_model_home(model_home)

    # Determine the path to the model
    if fname is None:
        if ext is None:
            path = os.path.join(model_home, model)
        else:
            path = os.path.join(model_home, model, "{}{}".format(model, ext))
    else:
        path = os.path.join(model_home, model, fname)

    if not os.path.exists(path):
        if not raises:
            return None

        raise ModelsError(
            f"could not find model at {path} - does it need to be downloaded?"
        )

    return path


def model_exists(model, model_home=None, fname=None, ext=None):
    """
    Checks to see if the specified model exists in the model home directory.
    """
    path = find_model_path(model, model_home, fname, ext, False)
    if path is not None:
        return os.path.exists(path)
    return False


def model_tflite_exists(model, model_home):
    """
    Checks to see if the model .tflite file exists or not.
    """
    return model_exists(model, model_home=model_home, ext=".tflite")


def model_archive(model, signature, model_home=None, ext=".zip"):
    """
    Checks to see if the model archive file exists and determines if it is the latest
    version by comparing the signature specified with the archive signature.
    """
    model_home = get_model_home(model_home)
    path = os.path.join(model_home, model+ext)

    if os.path.exists(path) and os.path.isfile(path):
        return sha256sum(path) == signature
    return False


def cleanup_model(model, model_home=None, archive=".zip"):
    removed = 0
    model_home = get_model_home(model_home)

    # Paths to remove
    datadir = os.path.join(model_home, model)
    archive = os.path.join(model_home, model+archive)

    if os.path.exists(datadir):
        shutil.rmtree(datadir)
        removed += 1

    if os.path.exists(archive):
        os.remove(archive)
        removed += 1

    return removed
