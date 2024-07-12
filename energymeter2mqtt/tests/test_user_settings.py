import dataclasses
from unittest import TestCase

from bx_py_utils.test_utils.snapshot import assert_snapshot

from energymeter2mqtt.user_settings import EnergyMeter


class UserSettingsTestCase(TestCase):
    def test_energy_meter_dataclass(self):
        energy_meter = EnergyMeter()
        self.assertEqual(energy_meter.verbose_name, 'Saia PCD ALD1D5FD')

        definitions = energy_meter.get_definitions(verbosity=0)
        self.assertIsInstance(definitions, dict)

        # Check samples:
        self.assertEqual(definitions['connection']['baudrate'], 19200)
        self.assertEqual(definitions['parameters'][0]['name'], 'Energy Counter Total')
        assert_snapshot(got=definitions)

        assert_snapshot(got=dataclasses.asdict(energy_meter))
