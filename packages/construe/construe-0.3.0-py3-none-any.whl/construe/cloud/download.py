"""
Handle HTTP download requests from content URLs
"""

import os
import shutil
import zipfile

from tqdm import tqdm
from urllib.request import urlopen
from construe.exceptions import DownloadError

from .signature import sha256sum


# Download chunk size
CHUNK = 524288


def download_zip(url, out, signature, replace=False, extract=True, progress=True):
    """
    Download a zipped file at the given URL saving it to the out directory. Once
    downloaded, verify the signature to make sure the download hasn't been tampered
    with or corrupted. If the file already exists it will be overwritten only if
    replace=True. If extract=True then the file will be unzipped.
    """
    # Get the name of the file from the URL
    basename = os.path.basename(url)
    name, _ = os.path.splitext(basename)

    # Get the archive and data directory paths
    archive = os.path.join(out, basename)
    datadir = os.path.join(out, name)

    # If the archive exists cleanup or raise override exception
    if os.path.exists(archive):
        if not replace:
            raise DownloadError(
                f"file already exists at {archive}, set replace=False to overwrite"
            )

        shutil.rmtree(datadir)
        os.remove(archive)

    # Create the output directory if it does not exist
    if not os.path.exists(datadir):
        os.mkdir(datadir)

    # Fetch the response in a streaming fashion and write it to disk.
    response = urlopen(url)
    content_length = int(response.headers["Content-Length"])

    pbar = None
    if progress:
        pbar = tqdm(
            unit="B", total=content_length, desc=f"Downloading {basename}", leave=False
        )

    with open(archive, "wb") as f:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)

            if pbar:
                pbar.update(len(chunk))

    # Compare the signature of the archive to the expected one
    if sha256sum(archive) != signature:
        raise DownloadError("Download signature does not match hardcoded signature!")

    # If extract, extract the zipfile.
    if extract:
        zf = zipfile.ZipFile(archive)
        zf.extractall(path=datadir)
