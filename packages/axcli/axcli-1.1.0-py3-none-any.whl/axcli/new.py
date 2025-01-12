import click
from colorama import Fore, Style
import axinite.tools as axtools
from astropy.units import Quantity
from astropy.coordinates import CartesianRepresentation
import json

@click.command("new")
def new():
    "Creates a new system."
    name = click.prompt("Enter the name of the system", type=str)
    author = click.prompt("Enter the author of the system", type=str)
    limit = click.prompt("Enter the time limit of the system in an interpretable form (-1 for infinite)", type=str)
    delta = click.prompt("Enter the change in time of the system in an interpretable form", type=str)
    rate = click.prompt("Enter the framerate the system should be shown at", type=int)
    
    bodies = []
    while click.confirm("Do you want to add a body?", default=True):
        body = {}
        body['mass'] = Quantity(click.prompt("Enter the mass of the body", type=float))
        body['r'] = CartesianRepresentation(
            x=click.prompt("Enter the x coordinate of the body", type=float),
            y=click.prompt("Enter the y coordinate of the body", type=float),
            z=click.prompt("Enter the z coordinate of the body", type=float)
        )
        body['v'] = CartesianRepresentation(
            x=click.prompt("Enter the x velocity of the body", type=float),
            y=click.prompt("Enter the y velocity of the body", type=float),
            z=click.prompt("Enter the z velocity of the body", type=float)
        )
        body['name'] = click.prompt("Enter the name of the body", type=str)
        body['radius'] = Quantity(click.prompt("Enter the radius of the body", type=float))
        body['color'] = click.prompt("Enter the color of the body", type=str)
        body['light'] = click.confirm("Does the body emit light?", default=False)
        body['retain'] = click.prompt("Enter the retain value of the body", type=int)
        body['radius_multiplier'] = click.prompt("Enter the radius multiplier of the body", type=float)
        bodies.append(body)
    
    system = {
        "name": name,
        "author": author,
        "limit": limit,
        "delta": delta,
        "t": 0,
        "rate": rate,
        "bodies": [
            {
                "name": body['name'],
                "mass": body['mass'].value,
                "radius": body['radius'].value,
                "r": {"x": body['r'].x.value, "y": body['r'].y.value, "z": body['r'].z.value},
                "v": {"x": body['v'].x.value, "y": body['v'].y.value, "z": body['v'].z.value},
                "color": body['color'],
                "light": body['light'],
                "retain": body['retain'],
                "radius_multiplier": body['radius_multiplier']
            } for body in bodies
        ]
    }

    path = click.prompt("Enter the path to save the system to", type=str)
    json.dump(system, open(path, "w"), indent=4)