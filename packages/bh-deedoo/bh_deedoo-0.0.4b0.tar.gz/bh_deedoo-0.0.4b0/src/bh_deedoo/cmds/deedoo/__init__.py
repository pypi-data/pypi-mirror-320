#!/usr/bin/env python3

import typer
import schedule

from .lib.debug import DEBUG
from .lib.stop import STOPS, stoppers
from .main import run

app = typer.Typer()

@app.command()
def answer(code : str ):
    STOPS.add(code)

@app.command()
def list():
    """Show all stoppers"""
    items = sorted(stoppers().items())
    while items:
        for hhmm,stop in items[:4]:
            print(hhmm,stop, end='\t')
        items = items[4:]
        print()

@app.command()
def serve(debug : bool = False):
    DEBUG.set_state(debug)
    run()

