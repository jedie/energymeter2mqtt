import logging

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import (
    get_console,  # noqa
    )

from energymeter2mqtt.cli_app import app
from energymeter2mqtt.mqtt_publish import publish_forever


logger = logging.getLogger(__name__)


@app.command
def publish_loop(verbosity: TyroVerbosityArgType):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    setup_logging(verbosity=verbosity)
    publish_forever(verbosity=verbosity)
