import click
from axcli import *

@click.group()
def cli():
    pass

cli.add_command(new)
cli.add_command(read)
cli.add_command(load)
cli.add_command(catalog)
cli.add_command(run)
cli.add_command(show)
cli.add_command(live)
