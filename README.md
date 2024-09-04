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

# Quick start

## Overview:

* Clone the sources
* Create your config: `./cli.py edit-settings`
* Test: `./cli.py print-values`
* Setup and start MQTT publishing: `sudo ./cli.py systemd-setup`

Note: It's a good idea to use the `/dev/serial/by-id/{your-device-id}` path as serial port, instead of `/dev/ttyUSB1`
Call `udevadm info -n /dev/ttyUSB*` to get information about all USB serial devices and `ls -l /dev/serial/by-id/` to see the existing links.


```bash
~$ git clone https://github.com/jedie/energymeter2mqtt.git
~$ cd energymeter2mqtt
~/energymeter2mqtt$ ./dev-cli.py --help
```


[comment]: <> (✂✂✂ auto generated main help start ✂✂✂)
```
Usage: ./cli.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ debug-settings   Display (anonymized) MQTT server username and password                          │
│ edit-settings    Edit the settings file. On first call: Create the default one.                  │
│ print-registers  Print RAW modbus register data                                                  │
│ print-values     Print all values from the definition in endless loop                            │
│ probe-usb-ports  Probe through the USB ports and print the values from definition                │
│ publish-loop     Publish all values via MQTT to Home Assistant in a endless loop.                │
│ systemd-debug    Print Systemd service template + context + rendered file content.               │
│ systemd-remove   Stops the systemd service and removed the service file. (May need sudo)         │
│ systemd-setup    Write Systemd service file, enable it and (re-)start the service. (May need     │
│                  sudo)                                                                           │
│ systemd-status   Display status of systemd service. (May need sudo)                              │
│ systemd-stop     Stops the systemd service. (May need sudo)                                      │
│ version          Print version and exit                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated main help end ✂✂✂)




# start development

```bash
~$ git clone https://github.com/jedie/energymeter2mqtt.git
~$ cd energymeter2mqtt
~/energymeter2mqtt$ ./dev-cli.py --help
```


# dev CLI

[comment]: <> (✂✂✂ auto generated dev help start ✂✂✂)
```
Usage: ./dev-cli.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ check-code-style            Check code style by calling darker + flake8                          │
│ coverage                    Run tests and show coverage report.                                  │
│ create-default-settings     Create a default user settings file. (Used by CI pipeline ;)         │
│ fix-code-style              Fix code style of all cli_base source code files via darker          │
│ install                     Run pip-sync and install 'cli_base' via pip as editable.             │
│ mypy                        Run Mypy (configured in pyproject.toml)                              │
│ pip-audit                   Run pip-audit check against current requirements files               │
│ publish                     Build and upload this project to PyPi                                │
│ test                        Run unittests                                                        │
│ tox                         Run tox                                                              │
│ update                      Update "requirements*.txt" dependencies files                        │
│ update-test-snapshot-files  Update all test snapshot files (by remove and recreate all snapshot  │
│                             files)                                                               │
│ version                     Print version and exit                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated dev help end ✂✂✂)




