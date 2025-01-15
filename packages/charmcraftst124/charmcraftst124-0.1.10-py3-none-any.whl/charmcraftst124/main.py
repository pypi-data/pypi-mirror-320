import contextlib
import importlib.metadata
import json
import logging
import os
import pathlib
import platform as platform_
import re
import shutil
import subprocess

import packaging.version
import requests
import rich.console
import rich.text
import typer
import typing_extensions
import yaml

app = typer.Typer(
    help="(deprecated) Temporary compatibility wrapper to use ST124 shorthand notation with older versions of "
    "charmcraft 3 that don't support ST124"
)
Verbose = typing_extensions.Annotated[bool, typer.Option("--verbose", "-v")]
running_in_ci = os.environ.get("CI") == "true"
if running_in_ci:
    # Show colors in CI (https://rich.readthedocs.io/en/stable/console.html#terminal-detection)
    console = rich.console.Console(highlight=False, force_terminal=True, force_interactive=False)
else:
    console = rich.console.Console(highlight=False)
logger = logging.getLogger(__name__)


class RichHandler(logging.Handler):
    """Use rich to print logs"""

    def emit(self, record):
        try:
            message = self.format(record)
            if getattr(record, "disable_wrap", False):
                console.print(message, overflow="ignore", crop=False)
            else:
                console.print(message)
        except Exception:
            self.handleError(record)


handler = RichHandler()


class WarningFormatter(logging.Formatter):
    """Only show log level if level >= logging.WARNING or verbose enabled"""

    def format(self, record):
        if record.levelno >= logging.WARNING or state.verbose:
            level = rich.text.Text(record.levelname, f"logging.level.{record.levelname.lower()}")
            replacement = f"{level.markup} "
        else:
            replacement = ""
        old_format = self._style._fmt
        self._style._fmt = old_format.replace("{levelname} ", replacement)
        result = super().format(record)
        self._style._fmt = old_format
        return result


class State:
    def __init__(self):
        self._verbose = None
        self.verbose = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        if value == self._verbose:
            return
        self._verbose = value
        log_format = "\[charmcraftst124] {levelname} {message}"
        if value:
            log_format = "{asctime} " + log_format
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.removeHandler(handler)
        handler.setFormatter(WarningFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S", style="{"))
        logger.addHandler(handler)
        logger.debug(f"Version: {installed_version}")


class Platform(str):
    """Platform in charmcraft.yaml 'platforms' (e.g. 'ubuntu@22.04:amd64')"""

    def __new__(cls, value: str, *, parsing_typer_parameter=True):
        match = re.fullmatch(
            r"(?P<base>ubuntu@[0-9]{2}\.[0-9]{2}):(?P<architecture>[a-z0-9]+)", value
        )
        if not match:
            if parsing_typer_parameter:
                raise typer.BadParameter(
                    f"{repr(value)} is not a valid ST124 shorthand notation platform.\n\n"
                    "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
                )
            else:
                raise ValueError(
                    "Invalid ST124 shorthand notation in charmcraft.yaml 'platforms': "
                    f"{repr(value)}\n\n"
                    "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
                )
        instance: Platform = super().__new__(cls, value)
        instance.base = match.group("base")
        instance.architecture = match.group("architecture")
        return instance


@contextlib.contextmanager
def converted_charmcraft_yaml(platform: Platform, /):
    """Convert charmcraft.yaml ST124 syntax to older charmcraft 3 syntax

    Example older charmcraft 3 syntax:
    ```yaml
    base: ubuntu@22.04
    platforms:
      amd64:
    ```
    """
    yaml_data = yaml.safe_load(charmcraft_yaml.read_text())
    yaml_data["base"] = platform.base
    yaml_data["platforms"] = {platform.architecture: None}
    shutil.move(charmcraft_yaml, charmcraft_yaml_backup)
    charmcraft_yaml.write_text(yaml.dump(yaml_data))
    logger.debug(
        f"Set charmcraft.yaml 'base' to {repr(yaml_data['base'])} and 'platforms' to "
        f"{repr(yaml_data['platforms'])}"
    )
    try:
        yield
    finally:
        shutil.move(charmcraft_yaml_backup, charmcraft_yaml)


def run_charmcraft(command: list[str], *, platform: Platform):
    try:
        version = json.loads(
            subprocess.run(
                ["charmcraft", "version", "--format", "json"],
                capture_output=True,
                check=True,
                text=True,
            ).stdout
        )["version"]
    except FileNotFoundError:
        version = None
    if packaging.version.parse(version or "0.0.0") < packaging.version.parse("3"):
        raise Exception(f'charmcraft {version or "not"} installed. charmcraft >=3 required')
    command = ["charmcraft", *command]
    if state.verbose:
        command.append("-v")
    try:
        with converted_charmcraft_yaml(platform):
            logger.debug(f"Running {command}")
            subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exception:
        # `charmcraft` stderr will be shown in terminal, no need to raise exception—just log
        # traceback.
        logger.exception("charmcraft command failed:")
        exit(exception.returncode)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}, deprecated=True
)
def pack(
    context: typer.Context,
    platform: typing_extensions.Annotated[
        Platform,
        typer.Option(
            parser=Platform,
            help="Platform in charmcraft.yaml 'platforms' (e.g. 'ubuntu@22.04:amd64'). Shorthand "
            "notation required ('build-on' and 'build-for' not supported) in charmcraft.yaml",
        ),
    ],
    verbose: Verbose = False,
):
    """`charmcraft pack` for ST124 platform

    Unrecognized command arguments are passed to `charmcraft pack`

    To pack multiple platforms, run this command once per platform
    """
    if verbose:
        # Verbose can be globally enabled from command level or app level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True
    if context.args:
        logger.info(
            f'Passing unrecognized arguments to `charmcraft pack`: {" ".join(context.args)}'
        )
    check_charmcraft_yaml()
    platforms = yaml.safe_load(charmcraft_yaml.read_text())["platforms"]
    if platform not in platforms:
        raise ValueError(
            f"Platform {repr(platform)} not found in charmcraft.yaml 'platforms': "
            f"{repr(list(platforms))}"
        )

    logger.info(f"Packing platform: {repr(platform)}")
    run_charmcraft(["pack", *context.args], platform=platform)

    # Rename *.charm file to include platform so that different platforms don't have overlapping
    # file names
    charm_files = list(pathlib.Path().glob(f"*_{platform.architecture}.charm"))
    if not charm_files:
        logger.error("No *.charm file found. Failed to rename *.charm file")
        exit(1)
    elif len(charm_files) > 1:
        logger.warning(f"{len(charm_files)} *.charm files found. Expected 1 file")
    for charm_file in charm_files:
        charm_file: pathlib.Path
        # Example `charm_file.name`: "mysql-router-k8s_amd64.charm"
        # Example `new_path.name`: "mysql-router-k8s_ubuntu-22.04-amd64.charm" (matches file name
        # from old charmcraft.yaml `bases` syntax)
        new_path = charm_file.parent / charm_file.name.replace(
            f"_{platform.architecture}.", f'_{platform.replace("@", "-").replace(":", "-")}.'
        )
        shutil.move(charm_file, new_path)
        logger.info(f"Moved {charm_file} to {new_path}")


@app.command(deprecated=True)
def check_charmcraft_yaml(verbose: Verbose = False):
    """Check if supported ST124 shorthand notation syntax is used in charmcraft.yaml

    Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage
    """
    if verbose:
        # Verbose can be globally enabled from app level or command level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True
    if not charmcraft_yaml.exists():
        raise FileNotFoundError(
            "charmcraft.yaml not found. `cd` into the directory with charmcraft.yaml"
        )
    yaml_data = yaml.safe_load(charmcraft_yaml.read_text())
    for key in ("base", "bases"):
        if key in yaml_data:
            raise ValueError(
                f"'{key}' key in charmcraft.yaml not supported with ST124. Use 'platforms' key "
                "instead.\n\n"
                "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
            )
    platforms = yaml_data.get("platforms")
    if not platforms:
        raise ValueError(
            "'platforms' key in charmcraft.yaml required\n\n"
            "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
        )
    if not isinstance(platforms, dict):
        raise TypeError(
            "Expected charmcraft.yaml 'platforms' with type 'dict', got "
            f"{repr(type(platforms).__name__)}: {repr(platforms)}\n\n"
            "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
        )
    for value in platforms.values():
        if value is not None:
            raise ValueError(
                "Shorthand notation required ('build-on' and 'build-for' not supported) in "
                "charmcraft.yaml 'platforms'.\n\n"
                "Docs: https://github.com/canonical/charmcraftst124?tab=readme-ov-file#usage"
            )
    for platform in platforms:
        # Validate `platform` string with regex
        Platform(platform, parsing_typer_parameter=False)


@app.command(deprecated=True)
def clean(verbose: Verbose = False):
    """`charmcraft clean`"""
    if verbose:
        # Verbose can be globally enabled from app level or command level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True
    all_platforms = [
        Platform(platform, parsing_typer_parameter=False)
        for platform in yaml.safe_load(charmcraft_yaml.read_text())["platforms"]
    ]
    architecture = {"x86_64": "amd64", "aarch64": "arm64"}[platform_.machine()]
    platforms = [platform for platform in all_platforms if platform.architecture == architecture]
    if not platforms:
        raise ValueError(
            f"No platforms for this machine's architecture ({architecture}): {repr(all_platforms)}"
        )
    for platform in platforms:
        logger.info(f"Cleaning platform: {repr(platform)}")
        run_charmcraft(["clean"], platform=platform)


@app.callback()
def main(verbose: Verbose = False):
    if verbose:
        # Verbose can be globally enabled from app level or command level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True


installed_version = importlib.metadata.version("charmcraftst124")
state = State()
logger.warning("`charmcraftst124` is deprecated. Use charmcraft >=3.3.0 instead")
if running_in_ci:
    # "::warning::" for https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#setting-a-warning-message
    console.print("::warning::`charmcraftst124` is deprecated. Use charmcraft >=3.3.0 instead")
charmcraft_yaml = pathlib.Path("charmcraft.yaml")
charmcraft_yaml_backup = pathlib.Path("charmcraft.yaml.backup")

response = requests.get("https://pypi.org/pypi/charmcraftst124/json")
response.raise_for_status()
latest_pypi_version = response.json()["info"]["version"]
if installed_version != latest_pypi_version:
    logger.info(
        f"Update available. Run `pipx upgrade charmcraftst124` ({installed_version} -> "
        f"{latest_pypi_version})"
    )
