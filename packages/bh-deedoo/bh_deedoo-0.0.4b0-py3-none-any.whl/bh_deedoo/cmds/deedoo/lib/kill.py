#!/usr/bin/env python3

from pathlib import Path

class Killpath:
    def __init__(self, path):
        self._path = Path(path)
    def killed(self):
        return self._path.exists()
    def unkill(self):
        self._path.exists() and self._path.unlink()
    def kill(self):
        self._path.exists() or self._path.touch()

_KILLPATH = Killpath( Path.home()/'die' )

def kill():
    return _KILLPATH.kill()
def killed():
    return _KILLPATH.killed()
def unkill():
    return _KILLPATH.unkill()


