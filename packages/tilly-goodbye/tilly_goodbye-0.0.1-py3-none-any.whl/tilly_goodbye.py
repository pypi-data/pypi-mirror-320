from click import echo
from tilly.plugins import hookimpl

@hookimpl
def til_command(cli):
    @cli.command()
    def goodbye():
        """Say goodbye."""
        echo("Goodbye from the tilly CLI!")