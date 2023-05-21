import atexit
import datetime
import locale
import logging
import sys
from decimal import Decimal
from pathlib import Path

import rich_click
import rich_click as click
from bx_py_utils.path import assert_is_file
from ha_services.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from ha_services.systemd.api import ServiceControl
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from rich import get_console, print  # noqa
from rich.pretty import pprint
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import energymeter2mqtt
from energymeter2mqtt import constants
from energymeter2mqtt.api import get_modbus_client
from energymeter2mqtt.mqtt_publish import publish_forever
from energymeter2mqtt.user_settings import EnergyMeter, get_systemd_settings, get_toml_settings, get_user_settings


logger = logging.getLogger(__name__)


PACKAGE_ROOT = Path(energymeter2mqtt.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=False, writable=True, path_type=Path)
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


###########################################################################################################


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def edit_settings(verbosity: int):
    """
    Edit the settings file. On first call: Create the default one.
    """
    setup_logging(verbosity=verbosity)
    toml_settings = get_toml_settings()
    toml_settings.open_in_editor()


cli.add_command(edit_settings)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def debug_settings(verbosity: int):
    """
    Display (anonymized) MQTT server username and password
    """
    setup_logging(verbosity=verbosity)
    toml_settings = get_toml_settings()
    toml_settings.print_settings()


cli.add_command(debug_settings)


######################################################################################################
# Manage systemd service commands:


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def systemd_debug(verbosity: int):
    """
    Print Systemd service template + context + rendered file content.
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).debug_systemd_config()


cli.add_command(systemd_debug)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def systemd_setup(verbosity: int):
    """
    Write Systemd service file, enable it and (re-)start the service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).setup_and_restart_systemd_service()


cli.add_command(systemd_setup)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def systemd_remove(verbosity: int):
    """
    Stops the systemd service and removed the service file. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).remove_systemd_service()


cli.add_command(systemd_remove)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def systemd_status(verbosity: int):
    """
    Display status of systemd service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).status()


cli.add_command(systemd_status)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def systemd_stop(verbosity: int):
    """
    Stops the systemd service. (May need sudo)
    """
    setup_logging(verbosity=verbosity)
    systemd_settings = get_systemd_settings(verbosity)

    ServiceControl(info=systemd_settings).stop()


cli.add_command(systemd_stop)


###########################################################################################################
# energymeter2mqtt commands


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def print_values(verbosity: int):
    """
    Print all values from the definition in endless loop
    """
    setup_logging(verbosity=verbosity)

    systemd_settings = get_user_settings(verbosity)
    energy_meter: EnergyMeter = systemd_settings.energy_meter
    definitions = energy_meter.get_definitions(verbosity)

    client = get_modbus_client(energy_meter, definitions, verbosity)

    parameters = definitions['parameters']
    if verbosity > 1:
        pprint(parameters)

    slave_id = energy_meter.slave_id
    print(f'{slave_id=}')

    while True:
        for parameter in parameters:
            print(f'{parameter["name"]:>30}', end=' ')
            address = parameter['register']
            count = parameter.get('count', 1)
            if verbosity:
                print(f'(Register dez: {address:02} hex: {address:04x}, {count=})', end=' ')
            response = client.read_holding_registers(address=address, count=count, slave=slave_id)
            if isinstance(response, (ExceptionResponse, ModbusIOException)):
                print('Error:', response)
            else:
                assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
                value = response.registers[0]
                if count > 1:
                    value += response.registers[1] * 100000

                scale = Decimal(str(parameter['scale']))
                value = value * scale
                print(f'{value} [blue]{parameter.get("uom", "")}')
        print('\n')


cli.add_command(print_values)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def print_registers(verbosity: int):
    """
    Print RAW modbus register data
    """
    setup_logging(verbosity=verbosity)

    systemd_settings = get_user_settings(verbosity)
    energy_meter: EnergyMeter = systemd_settings.energy_meter
    definitions = energy_meter.get_definitions(verbosity)

    client = get_modbus_client(energy_meter, definitions, verbosity)

    parameters = definitions['parameters']
    if verbosity > 1:
        pprint(parameters)

    slave_id = energy_meter.slave_id
    print(f'{slave_id=}')

    error_count = 0
    address = 0
    while error_count < 5:
        print(f'[blue]Read register[/blue] dez: {address:02} hex: {address:04x} ->', end=' ')

        response = client.read_holding_registers(address=address, count=1, slave=slave_id)
        if isinstance(response, (ExceptionResponse, ModbusIOException)):
            print('Error:', response)
            error_count += 1
        else:
            assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
            for value in response.registers:
                print(f'[green]Result[/green]: dez:{value:05} hex:{value:08x}', end=' ')
            print()

        address += 1


cli.add_command(print_registers)


@click.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def publish_loop(verbosity: int):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    setup_logging(verbosity=verbosity)
    publish_forever(verbosity=verbosity)


cli.add_command(publish_loop)


###########################################################################################################


def exit_func():
    console = get_console()
    console.rule(datetime.datetime.now().strftime('%c'))


def main():
    print(f'[bold][green]{energymeter2mqtt.__name__}[/green] v[cyan]{energymeter2mqtt.__version__}')
    locale.setlocale(locale.LC_ALL, '')

    console = get_console()
    rich_traceback_install(
        width=console.size.width,  # full terminal width
        show_locals=True,
        suppress=[click, rich_click],
        max_frames=2,
    )

    atexit.register(exit_func)

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
