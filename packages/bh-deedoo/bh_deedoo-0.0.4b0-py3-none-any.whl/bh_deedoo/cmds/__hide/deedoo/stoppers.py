#!/usr/bin/env python3
from pathlib import Path

import os

from . import util as UU

KILL_PATH   = Path.home()/'die'

STOPPERS=Path('/tmp/deedoo.stoppers')
STOPPERS.is_dir() or STOPPERS.mkdir()

def kill():
    KILL_PATH.touch()

def create(stop):
    file4stop(stop).touch()

def found(stop):
    return file4stop(stop).exists()

def file4stop(stop):
    return STOPPERS/stop

def files():
    """return list of stopfiles"""
    return list( STOPPERS.glob("*") )

def init():
    if not STOPPERS.is_dir():
        STOPPERS.mkdir()
    for file in files():
        os.remove(file)
    if KILL_PATH.exists():
        print( "removing killpath" )
        os.remove(str(KILL_PATH))

def killed():
    if KILL_PATH.exists(): exit("SERVER KILLED1")
    return False


def stoppers():
    def dd(n): return str(n+100)[-2:]
    acc={}
    for hh in range(0,24):
        for mm in range(0,60,15):
            hhmm = dd(hh) + dd(mm)
            acc[hhmm] = UU.hash4hhmm(hhmm)
    return acc
