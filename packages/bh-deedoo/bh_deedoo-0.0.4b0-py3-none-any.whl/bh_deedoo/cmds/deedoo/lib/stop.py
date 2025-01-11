#!/usr/bin/env python3

import datetime
import hashlib
import shutil
from pathlib import Path

class Flags:
    def __init__(self, path):
        self.__path = Path(path)
        if not self.__path.is_dir():
            self.__path.mkdir()
    def __contains__(self, flag):
        return (self.__path/flag).exists()
    def clear(self):
        shutil.rmtree(self.__path)
        self.__path.mkdir()
    def add(self,flag):
        (self.__path/flag).touch()
    def remove(self,flag):
        if flag in self:
            (self._path/flag).unlink()

def stoppers():
    def dd(n): return str(n+100)[-2:]
    acc={}
    for hh in range(0,24):
        for mm in range(0,60,15):
            hhmm = dd(hh) + dd(mm)
            acc[hhmm] = hash4txt(hhmm)
    return acc

def hash4txt(text):
    a=hashlib.md5()
    a.update(text.encode())
    return a.hexdigest()[:4]

def stop4dt(dt):
    def hhmm4dt(dt):
        return dt.strftime("%H%M")
    return hash4txt(hhmm4dt(dt))

def stop4now():
    return stop4dt(datetime.datetime.now())

STOPS = Flags('/tmp/bh-monitor.d')
