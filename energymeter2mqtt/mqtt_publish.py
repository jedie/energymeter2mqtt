import logging
import time

from ha_services.mqtt4homeassistant.converter import values2mqtt_payload
from ha_services.mqtt4homeassistant.data_classes import HaValues
from ha_services.mqtt4homeassistant.mqtt import HaMqttPublisher
from rich.pretty import pprint

from energymeter2mqtt.api import get_ha_values, get_modbus_client
from energymeter2mqtt.user_settings import EnergyMeter, get_user_settings


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
    user_settings = get_user_settings(verbosity)

    publisher = HaMqttPublisher(
        settings=user_settings.mqtt,
        verbosity=verbosity,
        config_count=1,  # Send every time the config
    )

    energy_meter: EnergyMeter = user_settings.energy_meter
    definitions = energy_meter.get_definitions(verbosity)

    client = get_modbus_client(energy_meter, definitions, verbosity)

    parameters = definitions['parameters']
    if verbosity > 1:
        pprint(parameters)

    slave_id = energy_meter.slave_id
    print(f'{slave_id=}')

    while True:
        # Collect information:
        try:
            values = get_ha_values(client=client, parameters=parameters, slave_id=slave_id)
        except Exception as err:
            logger.error('Error collection values: %s', err)
        else:
            ha_values = HaValues(
                device_name=energy_meter.verbose_name,
                values=values,
            )

            # Create Payload:
            ha_mqtt_payload = values2mqtt_payload(values=ha_values, name_prefix=energy_meter.mqtt_payload_prefix)

            # Send vial MQTT to HomeAssistant:
            publisher.publish2homeassistant(ha_mqtt_payload=ha_mqtt_payload)

        wait(sec=10, verbosity=verbosity)
