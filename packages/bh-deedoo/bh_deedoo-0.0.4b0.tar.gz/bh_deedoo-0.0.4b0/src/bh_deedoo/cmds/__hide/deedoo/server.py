#!/usr/bin/env pyth  on3
import time
import sys
import datetime
from pathlib import Path

from . import stoppers as SS
from . import util as UTIL
from .util import say as SAY
from .util import debug
from .util import debug_set
from .util import debug_note


from .defaults import ALARM_SLEEP
from .defaults import MISSES
from .defaults import SLICES

DIE_IF_KILLED=SS.killed


def gSLEEP():
    if debug(): return 1
    else:       return ALARM_SLEEP

def run_server(debug=False):
    SAY(f"The time is {phone4dt(datetime.datetime.now())}")
    debug_set(debug)
    Server().run()

def phone4dt(dt):
    hh = dt.strftime("%H")
    mm = dt.strftime("%M")
    if mm == '00': return f"{hh} hundred"
    else:          return f"{hh} {mm}"


class Now:
    def __init__(self):
        self.dt = datetime.datetime.now()
        self.ALARMS = set()
        self.DINGS = set()
        self.stop = UTIL.hash(self.show())
        self.stopfile = SS.file4stop(self.stop)

    def show(s):
        if debug(): return s.dt.strftime("%H%M%S")
        else:       return s.dt.strftime("%H%M")

    def is_deedoo_time(s):
        if debug(): return s.dt.second % 15 == 0
        else:       return s.dt.minute % 15 == 0

    def is_ding_time(s):
        if debug(): return s.dt.second % 5 == 0
        else:       return s.dt.minute % 5 == 0

    def __repr__(s):
        b = f"stop={s.stop}"
        t = f"t={s.show()}"
        return f"<{s.__class__.__name__}: {t} {b}>"

    def phone(self):
        hh = self.dt.strftime("%H")
        mm = self.dt.strftime("%M")
        if mm == '00': return f"{hh} hundred"
        else:          return f"{hh} {mm}"

    def ding(s):
        if s.is_ding_time() and not s.stop in s.DINGS:
            s.DINGS.add(s.stop)
            SAY(f"The time is {phone4dt(s.dt)}")

    def handle(self):
        DIE_IF_KILLED()
        debug_note( str(self) + '\n' )
        self.ding()
        if self.is_deedoo_time():
            self.poll()
            self.stopped() or SAY('giving up')
            self.stopped() or exit()
            SAY('stopped' )

    def poll(self):
        for count in range(MISSES, 0, -1):
            SAY( f'deedoo {count}' )
            for _ in UTIL.sliced_sleep(gSLEEP(), SLICES):
                DIE_IF_KILLED()
                debug_note('.')
                if self.stopped():
                    return

    def stopped(s):
        SS.found(s.stop) and s.ALARMS.add(s.stop)
        return s.stop in s.ALARMS


class Server:
    def __init__(self):
        pass

    def run(self):
        debug_note('--run--\n')
        SS.init()
        while True:
            Now().handle()
            time.sleep(.5)





