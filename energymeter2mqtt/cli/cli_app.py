import atexit
import datetime
import locale
import logging
import sys
from pathlib import Path

import rich_click
import rich_click as click
from bx_py_utils.path import assert_is_file
from ha_services.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from ha_services.systemd.api import ServiceControl
from ha_services.toml_settings.api import TomlSettings
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.pdu import ExceptionResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from rich import get_console, print  # noqa
from rich.pretty import pprint
from rich.traceback import install as rich_traceback_install
from rich_click import RichGroup

import energymeter2mqtt
from energymeter2mqtt import constants
from energymeter2mqtt.constants import SETTINGS_DIR_NAME, SETTINGS_FILE_NAME
from energymeter2mqtt.user_settings import EnergyMeter, SystemdServiceInfo, UserSettings


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


def get_toml_settings() -> TomlSettings:
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=UserSettings(),
        not_exist_exit_code=None,  # Don't sys.exit() if settings file not present, yet.
    )
    return toml_settings


def get_user_settings(verbosity) -> UserSettings:
    toml_settings = get_toml_settings()
    user_settings = toml_settings.get_user_settings(debug=verbosity > 1)
    return user_settings


def get_systemd_settings(verbosity) -> SystemdServiceInfo:
    user_settings = get_user_settings(verbosity)
    systemd_settings = user_settings.systemd
    return systemd_settings


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
    Write Systemd service file, enable it and (re-)start the service. (May need sudo)
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
def serial_test(verbosity: int):
    """
    WIP: Test serial connection
    """
    systemd_settings = get_user_settings(verbosity)
    energy_meter: EnergyMeter = systemd_settings.energy_meter

    definitions = energy_meter.get_definitions()
    if verbosity > 1:
        pprint(definitions)
    conn_settings = definitions['connection']
    parameters = definitions['parameters']
    if verbosity > 1:
        pprint(parameters)

    print(f'Connect to {energy_meter.port}...')
    conn_kwargs = dict(
        baudrate=conn_settings['baudrate'],
        bytesize=conn_settings['bytesize'],
        parity=conn_settings['parity'],
        stopbits=conn_settings['stopbits'],
        timeout=energy_meter.timeout,
        retry_on_empty=energy_meter.retry_on_empty,
    )
    if verbosity:
        print('Connection arguments:')
        pprint(conn_kwargs)

    client = ModbusSerialClient(energy_meter.port, framer=ModbusRtuFramer, broadcast_enable=False, **conn_kwargs)
    if verbosity > 1:
        print('connected:', client.connect())
        print(client)

    slave_id = energy_meter.slave_id
    print(f'{slave_id=}')

    while True:
        print('Energiezähler total:', end='')
        response = client.read_holding_registers(
            address=0x1C,  # == dez: 28 + 29
            count=2,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result} kWh')

        print('Energiezähler partiell:', end='')
        response = client.read_holding_registers(
            address=0x1E,  # == dez: 30 + 31
            count=2,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result} kWh')

        print('Spannung:', end='')
        response = client.read_holding_registers(
            address=0x23,  # == dez: 35
            count=1,
            slave=slave_id,
        )
        voltage = response.registers[0]
        print(f'{voltage} V')

        print('Strom:', end='')
        response = client.read_holding_registers(
            address=0x24,  # == dez: 36
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        current = result * 0.1
        print(f'{current} A')

        print(f'{voltage} V * {current} A = {voltage*current} W')

        print(' *** Leistung: ', end='')
        response = client.read_holding_registers(
            address=0x25,  # == dez: 37
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 10
        print(f'{result} W')

        print('Blindleistung: ', end='')
        response = client.read_holding_registers(
            address=0x26,  # == dez: 38
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 10
        print(f'{result} W')

        print('Phase (Cos Phi):', end='')
        response = client.read_holding_registers(
            address=0x27,  # == dez: 39
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result}')

        for address in range(0x1C, 0x28):
            print(f'Read register dez: {address:02} hex: {address:04x}  : ', end='')

            response = client.read_holding_registers(address=address, count=1, slave=slave_id)
            if isinstance(response, (ExceptionResponse, ModbusIOException)):
                print('Error:', response)
            else:
                assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
                for value in response.registers:
                    print(f'Result: dez:{value:05} hex:{value:08x}', end=' ')
                print()

        for parameter in parameters:
            print(parameter['name'], end=' ')
            address = parameter['register']
            count = parameter.get('count', 1)
            if verbosity:
                print(f'(Register dez: {address:02} hex: {address:04x}, {count=})', end=' ')
            response = client.read_holding_registers(address=address, count=count, slave=slave_id)
            if isinstance(response, (ExceptionResponse, ModbusIOException)):
                print('Error:', response)
            else:
                assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
                if count > 1:
                    # TODO: use all values!
                    pass
                value = response.registers[0]
                scale = parameter['scale']
                value = value * scale
                print(f'{value} {parameter.get("uom", "")}')
                print()


cli.add_command(serial_test)

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
