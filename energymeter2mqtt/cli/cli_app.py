import logging
import sys
from pathlib import Path
import rich_click as click
from bx_py_utils.path import assert_is_file
from manageprojects.utilities import code_style
from manageprojects.utilities.publish import publish_package
from manageprojects.utilities.subprocess_utils import verbose_check_call
from manageprojects.utilities.version_info import print_version
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.pdu import ExceptionResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from rich import print  # noqa
from rich_click import RichGroup

import energymeter2mqtt
from energymeter2mqtt import constants


logger = logging.getLogger(__name__)


PACKAGE_ROOT = Path(energymeter2mqtt.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=False, writable=True, path_type=Path)
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def mypy(verbose: bool = True):
    """Run Mypy (configured in pyproject.toml)"""
    verbose_check_call('mypy', '.', cwd=PACKAGE_ROOT, verbose=verbose, exit_on_error=True)


cli.add_command(mypy)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def coverage(verbose: bool = True):
    """
    Run and show coverage.
    """
    verbose_check_call('coverage', 'run', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'combine', '--append', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'report', '--fail-under=30', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'xml', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'json', verbose=verbose, exit_on_error=True)


cli.add_command(coverage)


@click.command()
def install():
    """
    Run pip-sync and install 'energymeter2mqtt' via pip as editable.
    """
    verbose_check_call('pip-sync', PACKAGE_ROOT / 'requirements.dev.txt')
    verbose_check_call('pip', 'install', '--no-deps', '-e', '.')


cli.add_command(install)


@click.command()
def safety():
    """
    Run safety check against current requirements files
    """
    verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')


cli.add_command(safety)


@click.command()
def update():
    """
    Update "requirements*.txt" dependencies files
    """
    bin_path = Path(sys.executable).parent

    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip')
    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip-tools')

    extra_env = dict(
        CUSTOM_COMPILE_COMMAND='./cli.py update',
    )

    pip_compile_base = [
        bin_path / 'pip-compile',
        '--verbose',
        '--allow-unsafe',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--resolver=backtracking',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--upgrade',
        '--generate-hashes',
    ]

    # Only "prod" dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--output-file',
        'requirements.txt',
        extra_env=extra_env,
    )

    # dependencies + "dev"-optional-dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--extra=dev',
        '--output-file',
        'requirements.dev.txt',
        extra_env=extra_env,
    )

    verbose_check_call(bin_path / 'safety', 'check', '-r', 'requirements.dev.txt')

    # Install new dependencies in current .venv:
    verbose_check_call(bin_path / 'pip-sync', 'requirements.dev.txt')


cli.add_command(update)


@click.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    _run_unittest_cli(verbose=False, exit_after_run=False)  # Don't publish a broken state

    publish_package(
        module=energymeter2mqtt,
        package_path=PACKAGE_ROOT,
    )


cli.add_command(publish)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def fix_code_style(color: bool = True, verbose: bool = False):
    """
    Fix code style of all energymeter2mqtt source code files via darker
    """
    code_style.fix(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(fix_code_style)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def check_code_style(color: bool = True, verbose: bool = False):
    """
    Check code style by calling darker + flake8
    """
    code_style.check(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(check_code_style)


@click.command()
def update_test_snapshot_files():
    """
    Update all test snapshot files (by remove and recreate all snapshot files)
    """

    def iter_snapshot_files():
        yield from PACKAGE_ROOT.rglob('*.snapshot.*')

    removed_file_count = 0
    for item in iter_snapshot_files():
        item.unlink()
        removed_file_count += 1
    print(f'{removed_file_count} test snapshot files removed... run tests...')

    # Just recreate them by running tests:
    _run_unittest_cli(
        extra_env=dict(
            RAISE_SNAPSHOT_ERRORS='0',  # Recreate snapshot files without error
        ),
        verbose=False,
        exit_after_run=False,
    )

    new_files = len(list(iter_snapshot_files()))
    print(f'{new_files} test snapshot files created, ok.\n')


cli.add_command(update_test_snapshot_files)


def _run_unittest_cli(extra_env=None, verbose=True, exit_after_run=True):
    """
    Call the origin unittest CLI and pass all args to it.
    """
    if extra_env is None:
        extra_env = dict()

    extra_env.update(
        dict(
            PYTHONUNBUFFERED='1',
            PYTHONWARNINGS='always',
        )
    )

    args = sys.argv[2:]
    if not args:
        if verbose:
            args = ('--verbose', '--locals', '--buffer')
        else:
            args = ('--locals', '--buffer')

    verbose_check_call(
        sys.executable,
        '-m',
        'unittest',
        *args,
        timeout=15 * 60,
        extra_env=extra_env,
    )
    if exit_after_run:
        sys.exit(0)


@click.command()  # Dummy command
def test():
    """
    Run unittests
    """
    _run_unittest_cli()


cli.add_command(test)


def _run_tox():
    verbose_check_call(sys.executable, '-m', 'tox', *sys.argv[2:])
    sys.exit(0)


@click.command()  # Dummy "tox" command
def tox():
    """
    Run tox
    """
    _run_tox()


cli.add_command(tox)


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


###########################################################################################################
# energymeter2mqtt commands


@click.command()
@click.option('--port', default='/dev/ttyUSB0', show_default=True)
def serial_test(port):
    """
    WIP: Test serial connection
    """
    print(f'Connect to {port=}...')

    client = ModbusSerialClient(
        port,
        framer=ModbusRtuFramer,
        baudrate=19200,
        bytesize=8,
        parity='N',
        stopbits=2,
        timeout=0.5,
        retry_on_empty=True,
        broadcast_enable=False,
        debug=True,
    )
    print('connected:', client.connect())
    print(client)

    slave_id = 0x0001
    print(f'{slave_id=}')

    while True:
        print('Energiezähler total:', end='')
        response = client.read_holding_registers(
            address=0x1C,  # == dez: 28 + 29
            count=2,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result} kWh')

        print('Energiezähler partiell:', end='')
        response = client.read_holding_registers(
            address=0x1E,  # == dez: 30 + 31
            count=2,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result} kWh')

        print('Spannung:', end='')
        response = client.read_holding_registers(
            address=0x23,  # == dez: 35
            count=1,
            slave=slave_id,
        )
        voltage = response.registers[0]
        print(f'{voltage} V')

        print('Strom:', end='')
        response = client.read_holding_registers(
            address=0x24,  # == dez: 36
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        current = result * 0.1
        print(f'{current} A')

        print(f'{voltage} V * {current} A = {voltage*current} W')

        print(' *** Leistung: ', end='')
        response = client.read_holding_registers(
            address=0x25,  # == dez: 37
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 10
        print(f'{result} W')

        print('Blindleistung: ', end='')
        response = client.read_holding_registers(
            address=0x26,  # == dez: 38
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 10
        print(f'{result} W')

        print('Phase (Cos Phi):', end='')
        response = client.read_holding_registers(
            address=0x27,  # == dez: 39
            count=1,
            slave=slave_id,
        )
        result = response.registers[0]
        result = result * 0.01
        print(f'{result}')

        for address in range(0x1C, 0x28):
            print(f'Read register dez: {address:02} hex: {address:04x}  : ', end='')

            response = client.read_holding_registers(address=address, count=1, slave=slave_id)
            if isinstance(response, (ExceptionResponse, ModbusIOException)):
                print('Error:', response)
            else:
                assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
                for value in response.registers:
                    print(f'Result: dez:{value:05} hex:{value:08x}', end=' ')
                print()


cli.add_command(serial_test)

###########################################################################################################


def main():
    print_version(energymeter2mqtt)

    if len(sys.argv) >= 2:
        # Check if we just pass a command call
        command = sys.argv[1]
        if command == 'test':
            _run_unittest_cli()
        elif command == 'tox':
            _run_tox()

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
