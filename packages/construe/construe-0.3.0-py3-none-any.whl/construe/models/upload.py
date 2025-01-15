"""
Helper utility for uploading models to GCP
"""

import os

from .path import FIXTURES
from .source import SOURCE_MODELS
from ..version import get_version
from ..utils import resolve_exclude
from ..cloud.gcp import connect_storage, upload
from ..cloud.manifest import make_fixture_path, MODELS


def upload_models(fixtures=FIXTURES, exclude=None, include=None, credentials=None):
    """
    Upload all models from the model fixtures directory.
    """
    exclude = resolve_exclude(exclude, include, SOURCE_MODELS)

    version = get_version(short=True)
    client = connect_storage(credentials)

    for name in SOURCE_MODELS:
        if name in exclude:
            continue

        name += ".zip"
        dst = make_fixture_path(name, MODELS, version=version)
        src = os.path.join(fixtures, name)

        upload(dst, src, client)
