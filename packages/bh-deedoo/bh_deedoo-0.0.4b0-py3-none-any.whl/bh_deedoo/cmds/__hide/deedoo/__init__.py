import os

import typer

import bh_deedoo.cmds.deedoo.stoppers as STOPPERS
import bh_deedoo.cmds.deedoo.server as SERVER

app = typer.Typer()

@app.command()
def kill():
    """Kill a running server"""
    STOPPERS.kill()

@app.command()
def serve(debug: bool=False):
    """Run the server [& to run in backgound]"""
    SERVER.run_server( debug = debug )

@app.command()
def answer(candidate: str):
    """Answer a deedoo"""
    STOPPERS.create(candidate)

@app.command()
def stoppers(time: bool=False):
    """Show all stoppers [--time to add time]"""
    items = sorted(STOPPERS.stoppers().items())
    for hhmm,stop in items:
        if time:
            print(hhmm,stop)
        else:
            print(stop)



