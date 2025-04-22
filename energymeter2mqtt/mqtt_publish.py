import logging
import time

from cli_base.cli_tools.verbosity import setup_logging
from pymodbus.client import ModbusSerialClient

from energymeter2mqtt.api import get_ha_values, get_modbus_client
from energymeter2mqtt.mqtt_handler import EnergyMeterMqttHandler
from energymeter2mqtt.user_settings import EnergyMeter, UserSettings, get_user_settings


logger = logging.getLogger(__name__)


def wait(*, sec: int, verbosity: int):
    if verbosity > 1:
        print('Wait', end='...')
    for i in range(sec, 1, -1):
        time.sleep(1)
        if verbosity > 1:
            print(i, end='...')
    if verbosity > 1:
        print('\n', flush=True)


def publish_forever(*, verbosity: int):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    setup_logging(verbosity=verbosity)

    user_settings: UserSettings = get_user_settings(verbosity)

    energymeter_mqtt_handler = EnergyMeterMqttHandler(
        user_settings=user_settings,
        verbosity=verbosity,
    )

    energy_meter: EnergyMeter = user_settings.energy_meter
    definitions = energy_meter.get_definitions()

    client: ModbusSerialClient = get_modbus_client(energy_meter, definitions, verbosity)

    parameters = definitions['parameters']
    # parameters = [{'register': 28,
    #                 'reg_count': 2,
    #                 'name': 'Energy Counter Total',
    #                 'class': 'energy',
    #                 'state_class': 'total',
    #                 'uom': 'kWh',
    #                 'scale': 0.01},
    #                {...

    slave_id = energy_meter.slave_id
    logger.info('Slave ID: %r', slave_id)

    while True:
        # Collect information:
        try:
            register2values = get_ha_values(client=client, parameters=parameters, slave_id=slave_id)
        except Exception as err:
            logger.error('Error collection values: %s', err)
        else:
            # Publish values:
            energymeter_mqtt_handler(register2values)

        wait(sec=10, verbosity=verbosity)
