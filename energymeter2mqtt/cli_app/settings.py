import logging

import rich_click
import rich_click as click
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from rich import get_console  # noqa
from rich import print  # noqa

from energymeter2mqtt.cli_app import cli
from energymeter2mqtt.user_settings import get_toml_settings


logger = logging.getLogger(__name__)


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def edit_settings(verbosity: int):
    """
    Edit the settings file. On first call: Create the default one.
    """
    setup_logging(verbosity=verbosity)
    toml_settings = get_toml_settings()
    toml_settings.open_in_editor()


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def debug_settings(verbosity: int):
    """
    Display (anonymized) MQTT server username and password
    """
    setup_logging(verbosity=verbosity)
    toml_settings = get_toml_settings()
    toml_settings.print_settings()
