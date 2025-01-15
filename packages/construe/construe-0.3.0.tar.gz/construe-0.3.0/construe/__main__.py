"""
Primary entry point for construe CLI application
"""

import click
import torch
import platform

from datetime import datetime

from .version import get_version
from .utils import resolve_exclude
from .exceptions import DeviceError

from .datasets.path import get_data_home
from .datasets.loaders import cleanup_all_datasets
from .datasets.download import (
    download_all_datasets,
    download_dialects,
    download_lowlight,
    download_reddit,
    download_movies,
    download_essays,
    download_aegis,
    download_nsfw,
)

from .models.path import get_model_home
from .models.loaders import cleanup_all_models
from .models.download import (
    download_all_models,
    download_moondream,
    download_whisper,
    download_mobilenet,
    download_mobilevit,
    download_nsfw as download_nsfw_model,
    download_offensive,
    download_lowlight as download_lowlight_model,
    download_gliner,
)


from .whisper import Whisper
from .basic import BasicBenchmark
from .moondream import MoonDreamBenchmark

from .benchmark import BenchmarkRunner


CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}

DATASETS = [
    "all",
    "dialects",
    "lowlight",
    "reddit",
    "movies",
    "essays",
    "aegis",
    "nsfw",
]

MODELS = [
    "all",
    "moondream",
    "whisper",
    "mobilenet",
    "mobilevit",
    "nsfw",
    "offensive",
    "lowlight",
    "gliner",
]

BENCHMARKS = {
    "whisper": Whisper,
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(get_version(), message="%(prog)s v%(version)s")
@click.option(
    "-o",
    "--out",
    default=None,
    type=str,
    help="specify the path to write the benchmark results to",
)
@click.option(
    "-d",
    "--device",
    default=None,
    type=str,
    envvar=["CONSTRUE_DEVICE", "TORCH_DEVICE"],
    help="specify the pytorch device to run on e.g. cpu, mps or cuda",
)
@click.option(
    "-e",
    "--env",
    default=None,
    envvar=["CONSTRUE_ENV", "ENV"],
    help="name of the experimental environment for comparison (default is hostname)",
)
@click.option(
    "-c",
    "--count",
    default=1,
    type=int,
    help="specify the number of times to run each benchmark",
)
@click.option(
    "-l",
    "--limit",
    default=None,
    type=int,
    help="limit the number of instances to inference on in each benchmark",
)
@click.option(
    "-D",
    "--datadir",
    default=None,
    envvar="CONSTRUE_DATA",
    help="specify the location to download datasets to",
)
@click.option(
    "-M",
    "--modeldir",
    default=None,
    envvar="CONSTRUE_MODELS",
    help="specify the location to download models to",
)
@click.option(
    "-S",
    "--sample/--no-sample",
    default=True,
    help="use sample dataset instead of full dataset for benchmark",
)
@click.option(
    "-C",
    "--cleanup/--no-cleanup",
    default=True,
    help="cleanup all downloaded datasets after the benchmark is run",
)
@click.option(
    "-Q",
    "--verbose/--quiet",
    default=True,
    help="specify the verbosity of the output and progress bars",
)
@click.pass_context
def main(
    ctx,
    out=None,
    env=None,
    device=None,
    count=1,
    limit=None,
    datadir=None,
    modeldir=None,
    sample=True,
    cleanup=True,
    verbose=True,
):
    """
    A utility for executing inferencing benchmarks.
    """
    if device is not None:
        try:
            torch.set_default_device(device)
        except RuntimeError as e:
            raise DeviceError(e)

        click.echo(f'using torch.device("{device}")')

    if env is None:
        env = platform.node()

    if out is None:
        out = f"construe-results-{datetime.now().strftime("%Y%m%d%H%M%S")}.json"

    ctx.ensure_object(dict)
    ctx.obj["out"] = out
    ctx.obj["device"] = device
    ctx.obj["env"] = env
    ctx.obj["n_runs"] = count
    ctx.obj["limit"] = limit
    ctx.obj["data_home"] = get_data_home(datadir)
    ctx.obj["model_home"] = get_model_home(modeldir)
    ctx.obj["use_sample"] = sample
    ctx.obj["cleanup"] = cleanup
    ctx.obj["verbose"] = verbose


@main.command()
@click.option(
    "-E",
    "--exclude",
    default=None,
    type=click.Choice(BENCHMARKS.keys(), case_sensitive=False),
    help="specify benchmarks to exclude from runner",
)
@click.option(
    "-I",
    "--include",
    default=None,
    type=click.Choice(BENCHMARKS.keys(), case_sensitive=False),
    help="specify benchmarks to include in runner",
)
@click.pass_context
def run(ctx, **kwargs):
    """
    Executes all available benchmarks.
    """
    out = ctx.obj.pop("out")
    exclude = resolve_exclude(
        kwargs.pop("exclude"), kwargs.pop("include"), BENCHMARKS.keys()
    )
    benchmarks = [bench for name, bench in BENCHMARKS.items() if name not in exclude]

    runner = BenchmarkRunner(benchmarks=benchmarks, **ctx.obj)
    runner.run()
    runner.save(out)


@main.command()
@click.option(
    "-o",
    "--saveto",
    default=None,
    help="path to write the measurements pickle data to",
)
@click.option(
    "-t",
    "--num-threads",
    default=None,
    type=int,
    help="specify number of threads for benchmark (default to maximum)",
)
@click.option(
    "-F",
    "--fuzz/--no-fuzz",
    default=False,
    help="fuzz the tensor sizes of the inputs to the benchmark",
)
@click.option(
    "-S",
    "--seed",
    default=None,
    type=int,
    help="set the random seed for random generation",
)
@click.pass_context
def basic(ctx, **kwargs):
    """
    Runs basic dot product performance benchmarks.
    """
    kwargs["env"] = ctx.obj["env"]
    if kwargs["saveto"] is None:
        kwargs["saveto"] = ctx.obj["out"]

    benchmark = BasicBenchmark(**kwargs)
    benchmark.run()


@main.command()
@click.pass_context
def moondream(ctx, **kwargs):
    """
    Executes image-to-text inferencing benchmarks.
    """
    kwargs["env"] = ctx.obj["env"]
    benchmark = MoonDreamBenchmark(**kwargs)
    benchmark.run()


@main.command()
@click.pass_context
def whisper(ctx, **kwargs):
    """
    Executes audio-to-text inferencing benchmarks.
    """
    out = ctx.obj.pop("out")
    runner = BenchmarkRunner(benchmarks=[Whisper], **ctx.obj)
    runner.run()
    runner.save(out)


@main.command()
@click.option(
    "-C",
    "--clean/--no-clean",
    default=False,
    help="cleanup the downloaded data cache and exit",
)
@click.option(
    "-d",
    "--download",
    default=None,
    type=click.Choice(DATASETS, case_sensitive=False),
)
@click.option(
    "-S",
    "--sample/--no-sample",
    default=True,
    help="if downloading a dataset, download only a sample",
)
@click.option(
    "-v",
    "--verbose/--no-verbose",
    default=False,
    help="print verbose info, otherwise just print the datasets path",
)
@click.pass_context
def datasets(ctx, clean=False, download=None, sample=True, verbose=False):
    """
    Helper utility for managing the dataset cache.
    """
    if clean and download:
        raise click.ClickException("cannot specify both --clean and --download")

    data_home = ctx.obj["data_home"]
    if clean:
        cleanup_all_datasets(data_home)
        return

    if download is not None:
        downloader = {
            "all": download_all_datasets,
            "dialects": download_dialects,
            "lowlight": download_lowlight,
            "reddit": download_reddit,
            "movies": download_movies,
            "essays": download_essays,
            "aegis": download_aegis,
            "nsfw": download_nsfw,
        }[download]

        downloader(sample=sample, data_home=data_home, progress=True)
        return

    # Provide some info
    if verbose:
        print(f"downloaded datasets are stored in {data_home}")
    else:
        print(data_home)


@main.command()
@click.option(
    "-C",
    "--clean/--no-clean",
    default=False,
    help="cleanup the downloaded models cache and exit",
)
@click.option(
    "-d",
    "--download",
    default=None,
    type=click.Choice(MODELS, case_sensitive=False),
)
@click.option(
    "-v",
    "--verbose/--no-verbose",
    default=False,
    help="print verbose info, otherwise just print the models path",
)
@click.pass_context
def models(ctx, clean=False, download=None, sample=True, verbose=False):
    """
    Helper utility for managing the models cache.
    """
    if clean and download:
        raise click.ClickException("cannot specify both --clean and --download")

    model_home = ctx.obj["model_home"]
    if clean:
        cleanup_all_models(model_home)
        return

    if download is not None:
        downloader = {
            "all": download_all_models,
            "moondream": download_moondream,
            "whisper": download_whisper,
            "mobilenet": download_mobilenet,
            "mobilevit": download_mobilevit,
            "nsfw": download_nsfw_model,
            "offensive": download_offensive,
            "lowlight": download_lowlight_model,
            "gliner": download_gliner,
        }[download]

        downloader(model_home=model_home, progress=True)
        return

    # Provide some info
    if verbose:
        print(f"downloaded models are stored in {model_home}")
    else:
        print(model_home)


if __name__ == "__main__":
    main(
        obj={},
        prog_name="construe",
    )
