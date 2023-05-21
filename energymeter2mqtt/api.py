import logging
from decimal import Decimal

from ha_services.mqtt4homeassistant.data_classes import HaValue
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.pdu import ExceptionResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from rich.pretty import pprint

from energymeter2mqtt.user_settings import EnergyMeter


logger = logging.getLogger(__name__)


def get_modbus_client(energy_meter: EnergyMeter, definitions: dict, verbosity: int) -> ModbusSerialClient:
    conn_settings = definitions['connection']

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

    return client


def get_ha_values(*, client, parameters, slave_id) -> list[HaValue]:
    values = []
    for parameter in parameters:
        address = parameter['register']
        count = parameter.get('count', 1)
        logger.debug('Read register %i (dez, count: %i, slave id: %i)', address, count, slave_id)

        response = client.read_holding_registers(address=address, count=count, slave=slave_id)
        if isinstance(response, (ExceptionResponse, ModbusException)):
            logger.error(
                'Error read register %i (dez, count: %i, slave id: %i): %s', address, count, slave_id, response
            )
        else:
            assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
            value = response.registers[0]
            if count > 1:
                value += response.registers[1] * 100000

            scale = Decimal(str(parameter['scale']))
            value = float(value * scale)

            ha_value = HaValue(
                name=parameter['name'],
                value=value,
                device_class=parameter['class'],
                state_class=parameter['state_class'],
                unit=parameter['uom'],
            )
            values.append(ha_value)
    return values
