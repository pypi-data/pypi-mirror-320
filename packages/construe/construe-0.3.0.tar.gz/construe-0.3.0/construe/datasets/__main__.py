"""
Admin utility for managing datasets.
"""

import click

from construe.version import get_version

from .source import download_source_datasets, SOURCE_DATASETS
from .source import sample_source_datasets
from .manifest import generate_manifest
from .upload import upload_datasets
from .path import FIXTURES


CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}

EPILOG = "This tool is intended for construe developer use and not construe users."


@click.group(context_settings=CONTEXT_SETTINGS, epilog=EPILOG)
@click.version_option(get_version(), message="%(prog)s v%(version)s")
def main():
    pass


@main.command(epilog=EPILOG)
@click.option(
    "-f",
    "--fixtures",
    type=str,
    default=FIXTURES,
    help="path to fixtures directory to generate manifest from",
)
@click.option(
    "-o",
    "--out",
    type=str,
    default=None,
    help="path to write the manifest to",
)
def manifest(fixtures=FIXTURES, out=None):
    """
    Generate a manifest file from local fixtures.
    """
    generate_manifest(fixtures, out)


@main.command(epilog=EPILOG)
@click.option(
    "-f",
    "--fixtures",
    type=str,
    default=FIXTURES,
    help="path to fixtures directory to download source datasets to",
)
@click.option(
    "-e",
    "--exclude",
    type=click.Choice(SOURCE_DATASETS, case_sensitive=False),
    default=None,
    multiple=True,
    help="specify datasets to exclude from source download",
)
@click.option(
    "-i",
    "--include",
    type=click.Choice(SOURCE_DATASETS, case_sensitive=False),
    default=None,
    multiple=True,
    help="specify datasets to explicitly include in source download",
)
def originals(fixtures=FIXTURES, exclude=None, include=None):
    """
    Download original datasets and store them in fixtures.
    """
    download_source_datasets(out=FIXTURES, exclude=exclude, include=include)


@main.command(epilog=EPILOG)
@click.option(
    "-f",
    "--fixtures",
    type=str,
    default=FIXTURES,
    help="path to fixtures directory to find source datasets in",
)
@click.option(
    "-o",
    "--out",
    type=str,
    default=FIXTURES,
    help="directory to write the sampled data to",
)
@click.option(
    "-s",
    "--size",
    type=float,
    default=0.25,
    help="approximate random sample size",
)
@click.option(
    "-S",
    "--suffix",
    type=str,
    default="-sample",
    help="suffix to append to the dataset name",
)
@click.argument(
    "dataset",
    nargs=-1,
    required=True,
    type=click.Choice(SOURCE_DATASETS, case_sensitive=False),
)
def sample(dataset, fixtures=FIXTURES, out=FIXTURES, size=0.25, suffix="-sample"):
    """
    Create a sample dataset from the original that is smaller.
    """
    sample_source_datasets(dataset, fixtures, out, size, suffix)


@main.command(epilog=EPILOG)
@click.option(
    "-f",
    "--fixtures",
    type=str,
    default=FIXTURES,
    help="path to fixtures directory where source datasets have been downloaded",
)
@click.option(
    "-e",
    "--exclude",
    type=click.Choice(SOURCE_DATASETS, case_sensitive=False),
    default=None,
    multiple=True,
    help="specify datasets to exclude from upload",
)
@click.option(
    "-i",
    "--include",
    type=click.Choice(SOURCE_DATASETS, case_sensitive=False),
    default=None,
    multiple=True,
    help="specify datasets to explicitly include in upload",
)
@click.option(
    "-c",
    "--credentials",
    type=str,
    default=None,
    help="path to service account json credentials for upload",
)
def upload(**kwargs):
    """
    Upload datasets to GCP for user downloads.
    """
    upload_datasets(**kwargs)


if __name__ == "__main__":
    main(
        obj={},
        prog_name="python -m construe.datasets",
    )
