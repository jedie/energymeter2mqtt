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
usage: ./cli.py [-h]
                {debug-settings,edit-settings,print-registers,print-values,probe-usb-ports,publish-loop,systemd-debug,
systemd-remove,systemd-setup,systemd-status,systemd-stop,version}



╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help        show this help message and exit                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ subcommands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ {debug-settings,edit-settings,print-registers,print-values,probe-usb-ports,publish-loop,systemd-debug,systemd-remo │
│ ve,systemd-setup,systemd-status,systemd-stop,version}                                                              │
│     debug-settings                                                                                                 │
│                   Display (anonymized) MQTT server username and password                                           │
│     edit-settings                                                                                                  │
│                   Edit the settings file. On first call: Create the default one.                                   │
│     print-registers                                                                                                │
│                   Print RAW modbus register data                                                                   │
│     print-values  Print all values from the definition in endless loop                                             │
│     probe-usb-ports                                                                                                │
│                   Probe through the USB ports and print the values from definition                                 │
│     publish-loop  Publish all values via MQTT to Home Assistant in a endless loop.                                 │
│     systemd-debug                                                                                                  │
│                   Print Systemd service template + context + rendered file content.                                │
│     systemd-remove                                                                                                 │
│                   Stops the systemd service and removed the service file. (May need sudo)                          │
│     systemd-setup                                                                                                  │
│                   Write Systemd service file, enable it and (re-)start the service. (May need sudo)                │
│     systemd-status                                                                                                 │
│                   Display status of systemd service. (May need sudo)                                               │
│     systemd-stop  Stops the systemd service. (May need sudo)                                                       │
│     version       Print version and exit                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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
usage: ./dev-cli.py [-h]
                    {check-code-style,coverage,create-default-settings,fix-code-style,install,mypy,nox,pip-audit,publi
sh,test,update,update-test-snapshot-files,version}



╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help        show this help message and exit                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ subcommands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ {check-code-style,coverage,create-default-settings,fix-code-style,install,mypy,nox,pip-audit,publish,test,update,u │
│ pdate-test-snapshot-files,version}                                                                                 │
│     check-code-style                                                                                               │
│                   Check code style by calling darker + flake8                                                      │
│     coverage      Run tests and show coverage report.                                                              │
│     create-default-settings                                                                                        │
│                   Create a default user settings file. (Used by CI pipeline ;)                                     │
│     fix-code-style                                                                                                 │
│                   Fix code style of all energymeter2mqtt source code files via darker                              │
│     install       Install requirements and 'energymeter2mqtt' via pip as editable.                                 │
│     mypy          Run Mypy (configured in pyproject.toml)                                                          │
│     nox           Run nox                                                                                          │
│     pip-audit     Run pip-audit check against current requirements files                                           │
│     publish       Build and upload this project to PyPi                                                            │
│     test          Run unittests                                                                                    │
│     update        Update "requirements*.txt" dependencies files                                                    │
│     update-test-snapshot-files                                                                                     │
│                   Update all test snapshot files (by remove and recreate all snapshot files)                       │
│     version       Print version and exit                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated dev help end ✂✂✂)


## History

[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v0.5.0](https://github.com/jedie/energymeter2mqtt/compare/v0.4.0...v0.5.0)
  * 2025-04-22 - Switch pip-tools to uv
  * 2024-09-06 - Update requirements
* [v0.4.0](https://github.com/jedie/energymeter2mqtt/compare/v0.3.0...v0.4.0)
  * 2024-09-04 - "retry_on_empty" -> "retries"
  * 2024-09-04 - update project via manageprojects
* [v0.3.0](https://github.com/jedie/energymeter2mqtt/compare/v0.2.0...v0.3.0)
  * 2024-07-12 - bugfix packaging
  * 2024-07-12 - Bugfix wrong path loading definitions
  * 2024-07-12 - Update requirements adn split CLI code
  * 2024-02-22 - Update requirements
  * 2024-01-01 - Update README.md
* [v0.2.0](https://github.com/jedie/energymeter2mqtt/compare/v0.1.2...v0.2.0)
  * 2023-08-29 - NEW command "probe-usb-ports"
  * 2023-08-29 - update requirements
  * 2023-08-29 - Remove nonsens doc string

<details><summary>Expand older history entries ...</summary>

* [v0.1.2](https://github.com/jedie/energymeter2mqtt/compare/v0.1.1...v0.1.2)
  * 2023-08-10 - adjust scale factor for double registers
  * 2023-06-27 - fix: adjust scale factor for double registers
* [v0.1.1](https://github.com/jedie/energymeter2mqtt/compare/v0.1.0...v0.1.1)
  * 2023-08-10 - Use https://github.com/jedie/cli-base-utilities
  * 2023-08-04 - Update requirements
* [v0.1.0](https://github.com/jedie/energymeter2mqtt/compare/3db8d32...v0.1.0)
  * 2023-05-21 - fix README example
  * 2023-05-21 - README
  * 2023-05-21 - Bugfix unit of "Power Factor (cos phi)"
  * 2023-05-21 - Bugfix systemd config
  * 2023-05-21 - Add logging to get_ha_values()
  * 2023-05-21 - fix wait
  * 2023-05-21 - Bugfix endless loop prints
  * 2023-05-21 - Bugfix voltage scale
  * 2023-05-21 - Publish all values via MQTT to Home Assistant in a endless loop.
  * 2023-05-21 - Fix CI
  * 2023-05-21 - More info in README
  * 2023-05-21 - Split commands
  * 2023-05-21 - Split CLI and use toml settings for energy meter modbus info
  * 2023-05-21 - Working "serial-test" with Saia PCD ALD1D5FD
  * 2023-04-28 - WIP: Test Serial connection
  * 2023-04-30 - Update README.md
  * 2023-04-28 - first commit

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)
