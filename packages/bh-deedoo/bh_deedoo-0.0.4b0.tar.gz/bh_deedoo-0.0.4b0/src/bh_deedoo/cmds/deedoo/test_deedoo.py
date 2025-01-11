import time
from pathlib import Path
from threading import Thread
from pprint import pprint

import pytest

from .main import clearall, Deedoo, SHELF
from .lib.stop import STOPS

def theshelf():
    return dict(SHELF)

def now():
    return time.time()

class Runner:
    def __init__(self, name):
        self.name = name
        self.t_init = now()
        while not self.alive():
            time.sleep(0.001)
            if now() - self.t_init > 3:
                raise TimeOut
        self.t_alive = now()
    def stat(self):
        return theshelf().get(self.name, {})
    def expire(self):
        while self.alive():
            time.sleep(0.01)
    def alive(self):
        return self.stat().get('alive', None)
    def count(self):
        return self.stat().get('count', None)
    def stopcode(self):
        return self.stat().get('stopcode', None)

def countdown(start, duration):
    t0 = now()
    old = start
    while old > 0:
        time.sleep(0.0001)
        elapsed = now() - t0
        percent = (duration-elapsed)/duration
        new = int(percent * start)
        if new < old:
            old = new
            yield old

def run(duration, count=10):
    clearall()
    name = str(time.time())
    args = (duration, count, name)
    thread = Thread(target=Deedoo, args=args)
    thread.start()
    return Runner(name)

def test_exercise_duration():
    for duration in [0.5, 1.0]:
        runner = run(duration)
        while runner.alive():
            time.sleep(0.01)
        lifetime = now() - runner.t_alive
        ratio = lifetime/duration
        assert ratio == pytest.approx(1.0, abs=0.1)

def test_count_and_stop():
    startcount = 20
    duration = 1
    target = 15
    runner = run(duration, count=startcount)
    for count in countdown(startcount, duration):
        assert (count - runner.count()) <= 2
        if runner.count() == target:
            STOPS.add(runner.stat()['stopcode'])
            break
    runner.expire()
    stat = runner.stat()
    assert stat['count'] == target
    assert stat['stopped'] == True
    assert stat['iskilled'] == False

