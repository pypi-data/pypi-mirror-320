"""
Helper utility for uploading datasets to GCP
"""

import os

from .path import FIXTURES
from .source import SOURCE_DATASETS
from ..version import get_version
from ..utils import resolve_exclude
from ..cloud.gcp import connect_storage, upload
from ..cloud.manifest import make_fixture_path, DATASETS


def upload_datasets(fixtures=FIXTURES, exclude=None, include=None, credentials=None):
    """
    Upload all datasets from the model fixtures directory.
    """
    exclude = resolve_exclude(exclude, include, SOURCE_DATASETS)

    version = get_version(short=True)
    client = connect_storage(credentials)

    for name in SOURCE_DATASETS:
        if name in exclude:
            continue

        for fname in (name + ".zip", name + "-sample.zip"):
            dst = make_fixture_path(fname, DATASETS, version=version)
            src = os.path.join(fixtures, fname)
            upload(dst, src, client)
