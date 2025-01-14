import click
import axinite.tools as axtools

@click.command("load")
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False), default="")
def load(input_path, output_path=""):
    "Load a system from a file."
    args = axtools.read(input_path)
    if output_path != "": axtools.load(args, output_path, verbose=True)
    else: axtools.load(args, f"{args.name}.ax", verbose=True)