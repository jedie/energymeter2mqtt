import dataclasses
import sys

from ha_services.toml_settings.api import TomlSettings
from rich.pretty import pprint


try:
    import tomllib  # New in Python 3.11
except ImportError:
    import tomli as tomllib  # noqa:F401

from bx_py_utils.path import assert_is_file
from ha_services.mqtt4homeassistant.data_classes import MqttSettings as OriginMqttSettings
from ha_services.systemd.data_classes import BaseSystemdServiceInfo, BaseSystemdServiceTemplateContext
from rich import print  # noqa

from energymeter2mqtt.constants import PACKAGE_ROOT, SETTINGS_DIR_NAME, SETTINGS_FILE_NAME


@dataclasses.dataclass
class MqttSettings(OriginMqttSettings):
    """
    MQTT server settings.
    """

    host: str = 'mqtt.your-server.tld'


@dataclasses.dataclass
class EnergyMeter:
    """
    The "name" is the prefix of "energymeter2mqtt/definitions/*.yaml" files!

    Set "ip" of the inverter if it's always the same. (Hint: Pin it in FritzBox settings ;)
    You can leave it empty, but then you must always pass "--ip" to CLI commands.
    Even if it is specified here, you can always override it in the CLI with "--ip".
    """

    name: str = 'saia_pcd_ald1d5fd'
    verbose_name: str = 'Saia PCD ALD1D5FD'
    mqtt_payload_prefix: str = 'ald1d5fd'  # FIXME: Use serial number?!?

    port: str = '/dev/ttyUSB0'
    slave_id: int = 0x001  # Modbus address

    timeout: float = 0.5
    retry_on_empty: bool = True

    def get_definitions(self, verbosity) -> dict:
        definition_file_path = PACKAGE_ROOT / 'energymeter2mqtt' / 'definitions' / f'{self.name}.toml'
        assert_is_file(definition_file_path)
        content = definition_file_path.read_text(encoding='UTF-8')
        definitions = tomllib.loads(content)

        if verbosity > 1:
            pprint(definitions)

        return definitions


@dataclasses.dataclass
class SystemdServiceTemplateContext(BaseSystemdServiceTemplateContext):
    """
    Context values for the systemd service file content
    """

    verbose_service_name: str = 'energymeter2mqtt'
    exec_start: str = f'{sys.executable} -m energymeter2mqtt publish-loop'


@dataclasses.dataclass
class SystemdServiceInfo(BaseSystemdServiceInfo):
    """
    Information for systemd helper functions
    """

    template_context: SystemdServiceTemplateContext = dataclasses.field(default_factory=SystemdServiceTemplateContext)


@dataclasses.dataclass
class UserSettings:
    """
    User settings for inverter-connect
    """

    systemd: dataclasses = dataclasses.field(default_factory=SystemdServiceInfo)
    mqtt: dataclasses = dataclasses.field(default_factory=MqttSettings)
    energy_meter: dataclasses = dataclasses.field(default_factory=EnergyMeter)


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
