import logging

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.device import MainMqttDevice, MqttDevice
from ha_services.mqtt4homeassistant.mqtt import get_connected_client
from ha_services.mqtt4homeassistant.utilities.string_utils import slugify

import energymeter2mqtt
from energymeter2mqtt.user_settings import EnergyMeter, UserSettings


logger = logging.getLogger(__name__)


class EnergyMeterMqttHandler:
    def __init__(self, user_settings: UserSettings, verbosity: int):
        self.user_settings = user_settings
        energy_meter: EnergyMeter = self.user_settings.energy_meter

        mqtt_settings: MqttSettings = user_settings.mqtt

        self.mqtt_client = get_connected_client(settings=mqtt_settings, verbosity=verbosity)
        self.mqtt_client.loop_start()

        self.main_device = MainMqttDevice(
            name='energymeter2mqtt',
            uid=mqtt_settings.main_uid,
            manufacturer='energymeter2mqtt',
            sw_version=energymeter2mqtt.__version__,
            config_throttle_sec=mqtt_settings.publish_config_throttle_seconds,
        )
        self.mqtt_device = MqttDevice(
            main_device=self.main_device,
            name=energy_meter.verbose_name,
            uid=energy_meter.name,
            manufacturer=energy_meter.manufacturer,
            sw_version=None,
            config_throttle_sec=mqtt_settings.publish_config_throttle_seconds,
        )

        #################################################################################

        definitions: dict = energy_meter.get_definitions()
        # definitions = {'connection': {'baudrate': 19200, 'bytesize': 8, 'parity': 'N', 'stopbits': 2},
        #              'parameters': [{'register': 28,
        #                              'reg_count': 2,
        #                              'name': 'Energy Counter Total',
        #                              'class': 'energy',
        #                              'state_class': 'total',
        #                              'uom': 'kWh',
        #                              'scale': 0.01},
        #                             {...

        self.register2sensor = {}
        for parameter in definitions['parameters']:
            sensor = Sensor(
                device=self.mqtt_device,
                name=parameter['name'],
                uid=slugify(parameter['name'].lower(), sep='_'),
                device_class=parameter['class'],
                state_class=parameter['state_class'],
                unit_of_measurement=parameter['uom'],
                suggested_display_precision=parameter.get('suggested_display_precision'),
                min_value=parameter.get('min_value'),
                max_value=parameter.get('max_value'),
            )
            self.register2sensor[parameter['register']] = sensor

    def __call__(self, register2values: dict):
        logger.debug('Process: %r', register2values)

        self.main_device.poll_and_publish(self.mqtt_client)

        for register, value in register2values.items():
            if sensor := self.register2sensor.get(register):
                sensor.set_state(value)
                sensor.publish(self.mqtt_client)
            else:
                logger.warning('No sensor found for register %i', register)
