import logging
import os
import sys

import rich_click
import rich_click as click
import tomlkit
from cli_base.click_defaults import OPTION_ARGS_DEFAULT_FALSE
from cli_base.toml_settings.api import TomlSettings
from cli_base.toml_settings.serialize import dataclass2toml
from rich import get_console  # noqa
from rich import print  # noqa; noqa
from tomlkit import TOMLDocument

from energymeter2mqtt.cli_dev import cli
from energymeter2mqtt.constants import SETTINGS_DIR_NAME, SETTINGS_FILE_NAME
from energymeter2mqtt.user_settings import UserSettings


logger = logging.getLogger(__name__)


@cli.command()
@click.option('--force', **OPTION_ARGS_DEFAULT_FALSE)
def create_default_settings(force):
    """
    Create a default user settings file. (Used by CI pipeline ;)
    """
    if not force and 'CI' not in os.environ:
        print('We are not running in CI pipeline and "--force" not used -> Abort.')
        sys.exit(-1)

    settings_dataclass = UserSettings()
    toml_settings = TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=settings_dataclass,
    )

    settings_path = toml_settings.file_path
    if settings_path.is_file():
        print(f'[green]Use settings file already exists here: {settings_path}')
        return

    document: TOMLDocument = dataclass2toml(instance=settings_dataclass)
    doc_str = tomlkit.dumps(document, sort_keys=False)

    settings_path.write_text(doc_str, encoding='UTF-8')
    print(f'[green]Default settings file created here: {settings_path}')
