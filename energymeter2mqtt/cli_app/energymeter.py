import logging

import rich_click
import rich_click as click
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from pymodbus.exceptions import ModbusIOException
from pymodbus.pdu import ExceptionResponse
from pymodbus.pdu.register_read_message import ReadHoldingRegistersResponse
from rich import get_console  # noqa
from rich import print  # noqa; noqa
from rich.pretty import pprint

from energymeter2mqtt.api import get_modbus_client
from energymeter2mqtt.cli_app import cli
from energymeter2mqtt.probe_usb_ports import print_parameter_values, probe_one_port
from energymeter2mqtt.user_settings import EnergyMeter, get_user_settings


logger = logging.getLogger(__name__)


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
@click.option('--max-port', default=10, help='Maximum USB port number')
@click.option('--port-template', default='/dev/ttyUSB{i}', help='USB device path template')
def probe_usb_ports(verbosity: int, max_port: int, port_template: str):
    """
    Probe through the USB ports and print the values from definition
    """
    setup_logging(verbosity=verbosity)

    systemd_settings = get_user_settings(verbosity)
    energy_meter: EnergyMeter = systemd_settings.energy_meter
    definitions = energy_meter.get_definitions(verbosity)

    for port_number in range(0, max_port):
        port = port_template.format(i=port_number)
        print(f'Probe port: {port}...')

        energy_meter.port = port
        try:
            probe_one_port(energy_meter, definitions, verbosity)
        except Exception as err:
            print(f'ERROR: {err}')


@cli.command()
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
        print_parameter_values(client, parameters, slave_id, verbosity)


@cli.command()
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
