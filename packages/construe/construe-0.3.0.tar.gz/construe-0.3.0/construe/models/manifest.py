"""
Manifest handlers for models
"""

from ..cloud.manifest import MODELS
from .path import FIXTURES, MANIFEST
from ..cloud.manifest import load_manifest as _load_manifest
from ..cloud.manifest import generate_manifest as _generate_manifest


def load_manifest(path=MANIFEST):
    return _load_manifest(path)


def generate_manifest(fixtures=FIXTURES, out=MANIFEST):
    out = out or MANIFEST
    return _generate_manifest(fixtures, out, MODELS)
