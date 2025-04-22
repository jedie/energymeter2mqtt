"""
    Manage systemd service commands
"""

import logging

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.systemd.api import ServiceControl
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import get_console  # noqa
from rich import print  # noqa

from energymeter2mqtt.cli_app import app
from energymeter2mqtt.user_settings import get_systemd_settings


logger = logging.getLogger(__name__)


@app.command
def systemd_debug(verbosity: TyroVerbosityArgType):
    """
    Print Systemd service template + context + rendered file content.
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).debug_systemd_config()


@app.command
def systemd_setup(verbosity: TyroVerbosityArgType):
    """
    Write Systemd service file, enable it and (re-)start the service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).setup_and_restart_systemd_service()


@app.command
def systemd_remove(verbosity: TyroVerbosityArgType):
    """
    Stops the systemd service and removed the service file. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).remove_systemd_service()


@app.command
def systemd_status(verbosity: TyroVerbosityArgType):
    """
    Display status of systemd service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).status()


@app.command
def systemd_stop(verbosity: TyroVerbosityArgType):
    """
    Stops the systemd service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).stop()
