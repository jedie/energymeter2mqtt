# energymeter2mqtt

[![tests](https://github.com/jedie/energymeter2mqtt/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/energymeter2mqtt/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/energymeter2mqtt/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/energymeter2mqtt)
[![energymeter2mqtt @ PyPi](https://img.shields.io/pypi/v/energymeter2mqtt?label=energymeter2mqtt%20%40%20PyPi)](https://pypi.org/project/energymeter2mqtt/)
[![Python Versions](https://img.shields.io/pypi/pyversions/energymeter2mqtt)](https://github.com/jedie/energymeter2mqtt/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/energymeter2mqtt)](https://github.com/jedie/energymeter2mqtt/blob/main/LICENSE)

Get values from modbus energy meter to MQTT / HomeAssistant


Energy Meter -> modbus -> RS485-USB-Adapter -> energymeter2mqtt -> MQTT -> Home Assistant


The current focus is on the energy meter "Saia PCD ALD1D5FD"
However, the code is kept flexible, so that similar meters can be quickly put into operation.
