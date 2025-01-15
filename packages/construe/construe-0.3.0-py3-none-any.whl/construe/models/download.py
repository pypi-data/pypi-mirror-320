"""
Handle downloading models from content URLs
"""

from functools import partial

from .path import get_model_home
from .manifest import load_manifest
from ..cloud.download import download_zip
from .path import NSFW, LOWLIGHT, OFFENSIVE, GLINER
from .path import MOONDREAM, WHISPER, MOBILENET, MOBILEVIT

from ..exceptions import ModelsError


def download_model(
    url, signature, model_home=None, replace=False, extract=True, progress=True
):
    """
    Downloads the zipped model file specified at the given URL saving it to the models
    directory specified by ``get_model_home``. The download is verified with the
    given signature then extracted.
    """
    model_home = get_model_home(model_home)
    download_zip(
        url, model_home, signature, replace=replace, extract=extract, progress=progress
    )


def _download_model(name, model_home=None, replace=False, extract=True, progress=True):
    """
    Downloads the zipped model file specified using the manifest URL, saving it to the
    models directory specified by ``get_model_home``. The download is verified with
    the given signature then extracted.
    """
    models = load_manifest()
    if name not in models:
        raise ModelsError(f"no model named {name} exists")

    info = models[name]
    info.update(
        {
            "model_home": model_home,
            "replace": replace,
            "extract": extract,
            "progress": progress,
        }
    )
    download_model(**info)


download_moondream = partial(_download_model, MOONDREAM)
download_whisper = partial(_download_model, WHISPER)
download_mobilenet = partial(_download_model, MOBILENET)
download_mobilevit = partial(_download_model, MOBILEVIT)
download_nsfw = partial(_download_model, NSFW)
download_lowlight = partial(_download_model, LOWLIGHT)
download_offensive = partial(_download_model, OFFENSIVE)
download_gliner = partial(_download_model, GLINER)


DOWNLOADERS = [
    download_moondream,
    download_whisper,
    download_mobilenet,
    download_mobilevit,
    download_nsfw,
    download_lowlight,
    download_offensive,
    download_gliner,
]


def download_all_models(model_home=None, replace=True, extract=True, progress=True):
    for f in DOWNLOADERS:
        f(model_home=model_home, replace=replace, extract=extract, progress=progress)
