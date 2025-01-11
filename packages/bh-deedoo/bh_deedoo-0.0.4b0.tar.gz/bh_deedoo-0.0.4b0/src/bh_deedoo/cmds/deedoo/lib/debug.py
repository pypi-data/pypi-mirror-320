#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
logging.basicConfig(
    filename=Path.home()/'deedoo.log'
    , level=logging.INFO
    , format='[%(asctime)s] %(message)s'
)
logger = logging.getLogger('foo')

from .util import note as NOTE

class Debug:
    state = False
    def __init__(self, state=None, log=None):
        self._logger = logging.getLogger('foo')
        self._logger.info( 'DEBUG initiated' )
        if state in (True, False):
            self.set_state(state)
    def set_state(self,state : bool):
        self.__class__.state = state
    def note(self, text, end='\n'):
        text = text + end
        if self:
            NOTE(text,end)
        self._logger.info(text)
    def __bool__(self):
        return self.__class__.state
    def __repr__(self):
        return f'<Debug:{bool(self)}>'


DEBUG = Debug()
