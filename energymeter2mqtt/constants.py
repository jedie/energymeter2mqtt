from pathlib import Path

from bx_py_utils.path import assert_is_file

import energymeter2mqtt


CLI_EPILOG = 'Project Homepage: https://github.com/jedie/energymeter2mqtt'


PACKAGE_ROOT = Path(energymeter2mqtt.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')


SETTINGS_DIR_NAME = 'energymeter2mqtt'
SETTINGS_FILE_NAME = 'energymeter2mqtt'
