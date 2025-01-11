#!/usr/bin/env python3

import os
import sys
import datetime
from .debug import logger
INFO = logger.info

def note(text, end='\n'):
    text = text + end
    sys.stdout.write(text)
    sys.stdout.flush()

def say(text):
    os.system(f'say {text}')

def text4now():
    dt=datetime.datetime.now()
    hh = dt.strftime("%H")
    mm = dt.strftime("%M")
    if mm == '00': return f"{hh} hundred"
    else:          return f"{hh} {mm}"

def saytime(debug=False):
    INFO( 'saytime()' )
    #dt=datetime.datetime.now()
    #hh = dt.strftime("%H")
   # mm = dt.strftime("%M")
    #if mm == '00': text = f"{hh} hundred"
    #else:          text = f"{hh} {mm}"
    #say(f"The time is {text}")
    if debug:
        say(f"{text4now()}")
    else:
        say(f"The time is {text4now()}")

