"""
Top-level exceptions for handling construe errors.
"""

import re

from click import ClickException


class ConstrueError(ClickException):
    pass


class DownloadError(ConstrueError):
    pass


class UploadError(ConstrueError):
    pass


class DatasetsError(ConstrueError):
    pass


class ModelsError(ConstrueError):
    pass


class InferenceError(ConstrueError):
    pass


class BenchmarkError(ConstrueError):
    pass


class DeviceError(ConstrueError):

    def __init__(self, e):
        """
        Expects a runtime error to parse from PyTorch
        """
        tre = re.compile(r"^Expected one of ([\w,\s]+) device type at start of device string: ([\w\d:]+)$", re.I) # noqa
        match = tre.match(str(e))
        if match:
            unknown = match.groups()[1]
            devices = match.groups()[0]
            super(DeviceError, self).__init__((
                f"Cannot set pytorch device (unknown device \"{unknown}\")\n"
                f"Device must be one of the following:\n{devices}"
            ))
        else:
            super(DeviceError, self).__init__(str(e))
