"""
Convert source models into tflite format.
"""

import os
import shutil
import tensorflow as tf

from .path import FIXTURES
from ..utils import resolve_exclude

from .source import SOURCE_MODELS
from .source import MOONDREAM_DIR, MOONDREAM_SAVED_MODEL_DIR
from .source import WHISPER_DIR, WHISPER_SAVED_MODEL_DIR
from .source import MOBILENET_DIR, MOBILENET_SAVED_MODEL_DIR
from .source import MOBILEVIT_DIR, MOBILEVIT_SAVED_MODEL_DIR
from .source import NSFW_DIR, NSFW_SAVED_MODEL_DIR
from .source import LOWLIGHT_DIR, LOWLIGHT_SAVED_MODEL_DIR
from .source import OFFENSIVE_DIR, OFFENSIVE_SAVED_MODEL_DIR
from .source import GLINER_DIR, GLINER_SAVED_MODEL_DIR

from transformers import MobileViTImageProcessor, MobileViTForImageClassification
from transformers import AutoModelForImageClassification, AutoImageProcessor
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import ViTImageProcessor
from transformers import WhisperProcessor

from gliner import GLiNER
from huggingface_hub import from_pretrained_keras

MOONDREAM_TFLITE = "moondream.tflite"
WHISPER_TFLITE = "whisper.tflite"
MOBILENET_TFLITE = "mobilenet.tflite"
MOBILEVIT_TFLITE = "mobilevit.tflite"
NSFW_TFLITE = "nsfw.tflite"
LOWLIGHT_TFLITE = "lowlight.tflite"
OFFENSIVE_TFLITE = "offensive.tflite"
GLINER_TFLITE = "gliner.tflite"


def convert_source_models(out=FIXTURES, exclude=None, include=None):
    """
    Convert all source models to tflite format, excluding any by name.
    """
    converter = {
        MOONDREAM_DIR: convert_moondream,
        WHISPER_DIR: convert_whisper,
        MOBILENET_DIR: convert_mobilenet,
        MOBILEVIT_DIR: convert_mobilevit,
        NSFW_DIR: convert_nsfw,
        LOWLIGHT_DIR: convert_lowlight,
        OFFENSIVE_DIR: convert_offensive,
        GLINER_DIR: convert_gliner,
    }

    exclude = resolve_exclude(exclude, include, SOURCE_MODELS)

    for name, convert in converter.items():
        if name in exclude:
            continue
        convert(out=out)


def convert_moondream(out=FIXTURES):
    """
    Convert the moondream model to tflite and save it to fixtures.
    """
    path = os.path.join(out, MOONDREAM_DIR, MOONDREAM_SAVED_MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(path)

    assert model is not None
    assert tokenizer is not None

    out = os.path.join(out, MOONDREAM_DIR, MOBILENET_TFLITE)
    print(f"moondream converted to {out}")


def convert_whisper(out=FIXTURES):
    """
    Convert the whisper tiny english model to tflite and save it to fixtures.
    """
    path = os.path.join(out, WHISPER_DIR, WHISPER_SAVED_MODEL_DIR)

    # Convert the model
    converter = tf.lite.TFLiteConverter.from_saved_model(path)
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,  # enable TensorFlow Lite ops.
        tf.lite.OpsSet.SELECT_TF_OPS     # enable TensorFlow ops.
    ]
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite = converter.convert()

    converted = os.path.join(out, WHISPER_DIR, WHISPER_DIR)
    os.mkdir(converted)

    tfpath = os.path.join(converted, WHISPER_TFLITE)
    with open(tfpath, 'wb') as f:
        f.write(tflite)

    # Load and save the whisper preprocessor
    processor = WhisperProcessor.from_pretrained(path)
    processor.save_pretrained(converted)

    # Zip the model for packaging
    zipname = os.path.join(out, WHISPER_DIR)
    shutil.make_archive(zipname, "zip", converted)
    print(f"whisper converted to {zipname+".zip"}")


def convert_mobilenet(out=FIXTURES):
    """
    Convert the mobilenet model to tflite and save it to fixtures.
    """
    path = os.path.join(out, MOBILENET_DIR, MOBILENET_SAVED_MODEL_DIR)
    preprocessor = AutoImageProcessor.from_pretrained(path)
    model = AutoModelForImageClassification.from_pretrained(
        path, trust_remote_code=True
    )

    assert preprocessor is not None
    assert model is not None

    out = os.path.join(out, MOBILENET_DIR, MOBILENET_TFLITE)
    print(f"mobilenet converted to {out}")


def convert_mobilevit(out=FIXTURES):
    """
    Convert the mobilevit model to tflite and save it to fixtures.
    """
    path = os.path.join(out, MOBILEVIT_DIR, MOBILEVIT_SAVED_MODEL_DIR)
    preprocessor = MobileViTImageProcessor.from_pretrained(path)
    model = MobileViTForImageClassification.from_pretrained(path)

    assert preprocessor is not None
    assert model is not None

    out = os.path.join(out, MOBILEVIT_DIR, MOBILEVIT_TFLITE)
    print(f"mobilevit converted to {out}")


def convert_nsfw(out=FIXTURES):
    """
    Convert the mobilevit model to tflite and save it to fixtures.
    """
    path = os.path.join(out, NSFW_DIR, NSFW_SAVED_MODEL_DIR)
    preprocessor = ViTImageProcessor.from_pretrained(path)
    model = AutoModelForImageClassification.from_pretrained(path)

    assert preprocessor is not None
    assert model is not None

    out = os.path.join(out, NSFW_DIR, NSFW_TFLITE)
    print(f"nsfw converted to {out}")


def convert_lowlight(out=FIXTURES):
    """
    Convert the mobilevit model to tflite and save it to fixtures.
    """
    path = os.path.join(out, LOWLIGHT_DIR, LOWLIGHT_SAVED_MODEL_DIR)
    model = from_pretrained_keras(path)

    assert model is not None

    out = os.path.join(out, LOWLIGHT_DIR, LOWLIGHT_TFLITE)
    print(f"lowlight converted to {out}")


def convert_offensive(out=FIXTURES):
    """
    Convert the mobilevit model to tflite and save it to fixtures.
    """
    path = os.path.join(out, OFFENSIVE_DIR, OFFENSIVE_SAVED_MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(
        path, trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(path)

    assert model is not None
    assert tokenizer is not None

    out = os.path.join(out, OFFENSIVE_DIR, OFFENSIVE_TFLITE)
    print(f"offensive converted to {out}")


def convert_gliner(out=FIXTURES):
    """
    Convert the mobilevit model to tflite and save it to fixtures.
    """
    path = os.path.join(out, GLINER_DIR, GLINER_SAVED_MODEL_DIR)
    model = GLiNER.from_pretrained(path)

    assert model is not None

    out = os.path.join(out, GLINER_DIR, GLINER_TFLITE)
    print(f"gliner converted to {out}")
