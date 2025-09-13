from unittest import TestCase

from pymodbus.pdu.register_message import ReadHoldingRegistersResponse

from energymeter2mqtt.api import get_ha_values


class ModbusClientMock:
    def __init__(self, *, mock_data: dict):
        self.mock_data = mock_data
        self.calls = []

    def read_holding_registers(self, **kwargs):
        self.calls.append(kwargs)
        values = self.mock_data[kwargs['address']]
        response = ReadHoldingRegistersResponse()
        response.registers = values
        return response


class ApiTestCase(TestCase):
    def test_get_ha_values(self):
        client = ModbusClientMock(mock_data={28: [1, 0]})
        parameters = [
            {
                'register': 28,
                'reg_count': 2,
                'name': 'Energy Counter Total',
                'class': 'energy',
                'state_class': 'total',
                'uom': 'kWh',
                'scale': 0.01,
            }
        ]
        register2values = get_ha_values(client=client, parameters=parameters, slave_id=0x001)
        self.assertEqual(register2values, {28: 0.01})
