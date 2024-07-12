import logging

import rich_click
import rich_click as click
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from rich import get_console  # noqa
from rich import print  # noqa; noqa

from energymeter2mqtt.cli_app import cli
from energymeter2mqtt.mqtt_publish import publish_forever


logger = logging.getLogger(__name__)


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def publish_loop(verbosity: int):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    setup_logging(verbosity=verbosity)
    publish_forever(verbosity=verbosity)
