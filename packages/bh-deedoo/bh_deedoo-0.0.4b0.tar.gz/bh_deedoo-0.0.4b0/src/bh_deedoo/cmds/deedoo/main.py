#!/usr/bin/env python3
from pathlib import Path
import shelve
import time
import datetime
import hashlib
from threading import Thread

import schedule

from .lib.debug import DEBUG
from .lib.util import note, say, saytime
from .lib.kill import kill, killed, unkill
from .lib.stop import STOPS, stop4now

SHELF = shelve.open(Path.home()/'deedoo.shelf')

def clearall():
    unkill()
    STOPS.clear()

def run():
    say( 'starting deedoo server' )
    clearall()
    setup()
    while not killed():
        schedule.run_pending()
        time.sleep(1)
    say('stopping deedoo server')

def setup():
    if DEBUG:
        offsets = [0,10,20,30,40,50] # deedoo start every twenty seconds
        duration = 5       # deedoo last for fifteen seconds
        count = 5
        for offset in offsets:
            offset = ':'+str(offset).zfill(2)
            print( f'setup(): starting deedoo every minute at {offset}' )
            schedule.every().minute.at(offset).do(Deedoo, duration, count=count)
    else:
        offsets = range(0,60,15) # every 15 minutes
        duration = 300           # repeat for 5 minutes
        for offset in offsets:
            offset = ':'+str(offset).zfill(2)
            print( f'setup(): starting deedoo every hour at {offset}' )
            schedule.every().hour.at(offset).do(Deedoo, duration)

class Deedoo(Thread):
    def __init__(self
        , duration
        , count=10
        , name=None
        ):
        Thread.__init__(self)
        self._debug = (name is not None)
        if name is None:
            name = datetime.datetime.now().strftime('%H:%M:%S')
        self._name = name
        self._tick = 0
        self._stopcode = stop4now()
        self._duration = duration
        self._start_count = count
        self._count = count
        self._delay = self._duration/self._start_count
        self.start()
        if self:
            self._debug or saytime()

        while self:
            self._count = self._count - 1
            self.speak( f'deedoo: {self.count}' )
            time.sleep(self._delay)

    def speak(self, text):
        if not self._debug:
            say(text)

    def die(self, n):
        self.stat()
        exit(n)

    def run(self):
        while self:
            time.sleep(.001)
            self.stat()
            self._tick = self._tick + 1
        if killed():
            self.speak('killed')
            self.die(2)
        elif self.timeout:
            self.speak('timeout')
            kill()
            self.die(3)
        else:
            self.speak('stopped')
            self.die(0)

    @property
    def stopcode(self): return self._stopcode
    @property
    def count(self): return self._count
    @property
    def stopped(self): return self._stopcode in STOPS
    @property
    def timeout(self): return self.count <= 0
    @property
    def iskilled(self): return killed()
    @property
    def tick(self): return self._tick
    @property
    def alive(self): return bool(self)
    @property
    def delay(self): return self._delay
    @property
    def startcount(self): return self._start_count

    def __bool__(self):
        return not (killed() or self.stopped or self.timeout)

    def stat(self):
        acc = {}
        for name in """startcount delay stopcode count
                       stopped timeout iskilled
                       tick alive""".split():
            val = getattr(self, name)
            acc[name] = val
        SHELF[self._name] = acc

    def __repr__(self):
        d = self._duration
        s = self.stopcode
        c = self.count
        f = self._start_count
        n = self._name
        torf = bool(self)
        stopped = self.stopped
        return f'<Deedoo({n}) [{d=}] [{s}] [{c}/{f}] {torf=} {stopped=}>'


