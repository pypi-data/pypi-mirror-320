"""
Manages datasets used for inferencing
"""

from .loaders import * # noqa
from .download import download_data
from .path import get_data_home, cleanup_dataset
