'''
This file is part of ConfigShell.
Copyright (c) 2011-2013 by Datera, Inc

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
'''

import inspect
import os
import time
import traceback

from .console import Console
from .prefs import Prefs

class Log(object):
    '''
    Implements a file and console logger using python's logging facility.
    Log levels are, in raising criticality:
        - debug
        - verbose
        - info
        - warning
        - error
        - critical
    It uses configshell's Prefs() backend for storing some of its parameters,
    who can then be read/changed by other objects using Prefs()
    '''
    __borg_state = {}
    levels = ['critical', 'error', 'warning', 'info', 'verbose', 'debug']
    colors = {'critical': 'red', 'error': 'red', 'warning': 'yellow',
              'info': 'green', 'verbose': 'blue', 'debug': 'blue'}

    def __init__(self, console_level=None,
                 logfile=None, file_level=None):
        '''
        This class implements the Borg pattern.
        @param console_level: Console log level, defaults to 'info'
        @type console_level: str
        @param logfile: Optional logfile.
        @type logfile: str
        @param file_level: File log level, defaults to 'debug'.
        @type file_level: str
        '''
        self.__dict__ = self.__borg_state
        self.con = Console()
        self.prefs = Prefs()

        if console_level:
            self.prefs['loglevel_console'] = console_level
        elif not self.prefs['loglevel_console']:
            self.prefs['loglevel_console'] = 'info'

        if file_level:
            self.prefs['loglevel_file'] = file_level
        elif not self.prefs['loglevel_file']:
            self.prefs['loglevel_file'] = 'debug'

        if logfile:
            self.prefs['logfile'] = logfile

    # Private methods

    def _append(self, msg, level):
        '''
        Just appends the message to the logfile if it exists, prefixing it with
        the current time and level.
        @param msg: The message to log
        @type msg: str
        @param level: The debug level to prefix the message with.
        @type level: str
        '''
        date_fields = time.localtime()
        date = "%d-%02d-%02d %02d:%02d:%02d" \
                % (date_fields[0], date_fields[1], date_fields[2],
                   date_fields[3], date_fields[4], date_fields[5])

        if self.prefs['logfile']:
            path =  os.path.expanduser(self.prefs['logfile'])
            handle = open(path, 'a')
            try:
                handle.write("[%s] %s %s\n" % (level, date, msg))
            finally:
                handle.close()

    def _log(self, level, msg):
        '''
        Do the actual logging.
        @param level: The log level of the message.
        @type level: str
        @param msg: The message to log.
        @type msg: str
        '''
        if self.levels.index(self.prefs['loglevel_file']) \
           >= self.levels.index(level):
            self._append(msg, level.upper())

        if self.levels.index(self.prefs['loglevel_console']) \
           >= self.levels.index(level):
            if self.prefs["color_mode"]:
                msg = self.con.render_text(msg, self.colors[level])
            else:
                msg = "%s: %s" % (level.capitalize(), msg)
            error = False
            if self.levels.index(level) <= self.levels.index('error'):
                error = True
            self.con.display(msg, error=error)

    # Public methods

    def debug(self, msg):
        '''
        Logs a debug message.
        @param msg: The message to log.
        @type msg: str
        '''
        caller = inspect.stack()[1]
        msg = "%s:%d %s() %s" % (caller[1], caller[2], caller[3], msg)
        self._log('debug', msg)

    def exception(self, msg=None):
        '''
        Logs an error message and dumps a full stack trace.
        @param msg: The message to log.
        @type msg: str
        '''
        trace = traceback.format_exc().rstrip()
        if msg:
            trace += '\n%s' % msg
        self._log('error', trace)

    def verbose(self, msg):
        '''
        Logs a verbose message.
        @param msg: The message to log.
        @type msg: str
        '''
        self._log('verbose', msg)

    def info(self, msg):
        '''
        Logs an info message.
        @param msg: The message to log.
        @type msg: str
        '''
        self._log('info', msg)

    def warning(self, msg):
        '''
        Logs a warning message.
        @param msg: The message to log.
        @type msg: str
        '''
        self._log('warning', msg)

    def error(self, msg):
        '''
        Logs an error message.
        @param msg: The message to log.
        @type msg: str
        '''
        self._log('error', msg)

    def critical(self, msg):
        '''
        Logs a critical message.
        @param msg: The message to log.
        @type msg: str
        '''
        self._log('critical', msg)
