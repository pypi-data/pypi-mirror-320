"""
Manifest handlers for downloading cloud resources and checking signatures.
"""

import os
import json
import glob

from urllib.parse import urljoin

from .signature import sha256sum
from ..version import get_version


BUCKET = "construe"
BASE_URL = "https://storage.googleapis.com/"

MODELS = "models"
DATASETS = "datasets"


def load_manifest(path):
    with open(path, "r") as f:
        return json.load(f)


def generate_manifest(fixtures, out, upload_type):
    manifest = {}
    version = get_version(short=True)

    for path in glob.glob(os.path.join(fixtures, "*.zip")):
        fname = os.path.basename(path)
        name, _ = os.path.splitext(fname)

        manifest[name] = {
            "url": make_fixture_url(fname, upload_type=upload_type, version=version),
            "signature": sha256sum(path),
        }

    with open(out, "w") as o:
        json.dump(manifest, o, indent=2)


def make_fixture_url(fname, upload_type, version=None):
    path = make_fixture_path(fname, upload_type, version)
    return urljoin(BASE_URL, path)


def make_fixture_path(fname, upload_type, version=None):
    version = version or get_version(short=True)
    return os.path.join(BUCKET, f"v{version}", upload_type, fname)
