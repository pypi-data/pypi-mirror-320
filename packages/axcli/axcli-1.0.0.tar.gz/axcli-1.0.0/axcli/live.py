import axinite.tools as axtools
import click

@click.command("live")
@click.argument("path", type=click.Path(exists=True))
@click.option("-f", "--frontend", type=str, default="vpython")
def live(path, frontend):
    "Watch a system live."
    name_to_frontend = {
        "vpython": axtools.vpython_frontend,
    }
    args = axtools.read(path)
    axtools.live(args, name_to_frontend[frontend](args, "live"))