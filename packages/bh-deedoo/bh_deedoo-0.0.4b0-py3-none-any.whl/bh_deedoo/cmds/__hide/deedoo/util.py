import hashlib
import sys
import os
import time
def sayspell(text):
    aa = ''.join( f"{ch}. " for ch in text )
    debug(aa + '\n')
    say(aa)
def say(text):
    os.system(f'say {text}')
def hash(text):
    a=hashlib.md5()
    a.update(text.encode())
    return a.hexdigest()[:4]
def hash4hhmm(x):
    return hash(x)
def errout(text):
    back = '\b'*(len(text)+10)
    sys.stderr.write(text + back)
    sys.stderr.flush()

def sliced_sleep(duration, step):
    for _ in range(int(duration/step)):
        yield
        time.sleep(step)

def debug_note(x):
    if debug():
        sys.stdout.write(x)
        sys.stdout.flush()

def debug_set(debug=True):
    sys.bh_deedoo_debug = debug

def debug():
    try:
        return sys.bh_deedoo_debug
    except AttributeError:
        return False

