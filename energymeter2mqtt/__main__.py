"""
    Allow energymeter2mqtt to be executable
    through `python -m energymeter2mqtt`.
"""


from energymeter2mqtt.cli import cli_app


def main():
    cli_app.main()


if __name__ == '__main__':
    main()
