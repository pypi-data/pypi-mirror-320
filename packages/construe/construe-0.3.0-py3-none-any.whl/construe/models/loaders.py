"""
Managers for loading models
"""

import os
import shutil

from functools import partial

from .manifest import load_manifest
from .download import download_model
from ..exceptions import ModelsError
from .path import model_archive, cleanup_model
from .path import find_model_path, get_model_home
from .path import NSFW, LOWLIGHT, OFFENSIVE, GLINER
from .path import MOONDREAM, WHISPER, MOBILENET, MOBILEVIT

from tensorflow import lite as tflite
from transformers import WhisperProcessor


__all__ = [
    "load_all_models", "cleanup_all_models",
    "load_moondream", "cleanup_moondream",
    "load_whisper", "cleanup_whisper",
    "load_mobilenet", "cleanup_mobilenet",
    "load_mobilevit", "cleanup_mobilevit",
    "load_nsfw", "cleanup_nsfw",
    "load_lowlight", "cleanup_lowlight",
    "load_offensive", "cleanup_offensive",
    "load_gliner", "cleanup_gliner",
]


MODELS = load_manifest()


def _info(model):
    if model not in MODELS:
        raise ModelsError(f"no model named {model} exists")
    return MODELS[model]


def _model_path(name, tflite=True, model_home=None):
    info = _info(name)
    if not model_archive(name, info["signature"], model_home=model_home):
        # If the model does not exist, download and extract it
        info.update({"model_home": model_home, "replace": True, "extract": True})
        download_model(**info)

    if tflite:
        return find_model_path(name, model_home=model_home, ext=".tflite")
    return find_model_path(name, model_home=model_home)


def load_moondream(model_home=None):
    pass


def load_whisper(model_home=None):
    """
    Returns a tflite interpreter with the whisper model and the whisper prepocessor.
    """
    model_path = _model_path(WHISPER, model_home=model_home)
    proccessor_path = _model_path(WHISPER, tflite=False, model_home=model_home)

    model = tflite.Interpreter(model_path)
    processor = WhisperProcessor.from_pretrained(proccessor_path)
    return model, processor


def load_mobilenet(model_home=None):
    pass


def load_mobilevit(model_home=None):
    pass


def load_nsfw(model_home=None):
    pass


def load_lowlight(model_home=None):
    pass


def load_offensive(model_home=None):
    pass


def load_gliner(model_home=None):
    pass


def load_all_models(model_home=None):
    """
    Load all available models as defined by __all__
    """
    models = {}
    module = globals()
    for name in __all__:
        if not name.startswith("load"):
            continue

        if name == "load_all_models":
            continue

        f = module[name]
        models[name] = f(model_home)

    return models


def cleanup_all_models(model_home=None):
    """
    Delete everything in the model home directory
    """
    with os.scandir(get_model_home(model_home)) as entries:
        for entry in entries:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)


cleanup_moondream = partial(cleanup_model, MOONDREAM)
cleanup_whisper = partial(cleanup_model, WHISPER)
cleanup_mobilenet = partial(cleanup_model, MOBILENET)
cleanup_mobilevit = partial(cleanup_model, MOBILEVIT)
cleanup_nsfw = partial(cleanup_model, NSFW)
cleanup_lowlight = partial(cleanup_model, LOWLIGHT)
cleanup_offensive = partial(cleanup_model, OFFENSIVE)
cleanup_gliner = partial(cleanup_model, GLINER)
