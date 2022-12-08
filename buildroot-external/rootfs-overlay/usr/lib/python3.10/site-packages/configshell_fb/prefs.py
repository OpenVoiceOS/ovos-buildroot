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

import os
import six
import fcntl

class Prefs(object):
    '''
    This is a preferences backend object used to:
        - Hold the ConfigShell preferences
        - Handle persistent storage and retrieval of these preferences
        - Share the preferences between the ConfigShell and ConfigNode objects

    As it is inherently destined to be shared between objects, this is a Borg.
    '''
    _prefs = {}
    filename = None
    autosave = False
    __borg_state = {}

    def __init__(self, filename=None):
        '''
        Instanciates the ConfigShell preferences object.
        @param filename: File to store the preferencces to.
        @type filename: str
        '''
        self.__dict__ = self.__borg_state
        if filename is not None:
            self.filename = filename

    def __getitem__(self, key):
        '''
        Proxies dict-like references to prefs.
        One specific behavior, though, is that if the key does not exists,
        we will return None instead of raising an exception.
        @param key: The preferences dictionnary key to get.
        @type key: any valid dict key
        @return: The key value
        @rtype: n/a
        '''
        if key in self._prefs:
            return self._prefs[key]
        else:
            return None

    def __setitem__(self, key, value):
        '''
        Proxies dict-like references to prefs.
        @param key: The preferences dictionnary key to set.
        @type key: any valid dict key
        '''
        self._prefs[key] = value
        if self.autosave:
            self.save()

    def __contains__(self, key):
        '''
        Do the preferences contain key ?
        @param key: The preferences dictionnary key to check.
        @type key: any valid dict key
        '''
        if key in self._prefs:
            return True
        else:
            return False

    def __delitem__(self, key):
        '''
        Deletes a preference key.
        @param key: The preference to delete.
        @type key: any valid dict key
        '''
        del self._prefs[key]
        if self.autosave:
            self.save()

    def __iter__(self):
        '''
        Generic iterator for the preferences.
        '''
        return self._prefs.__iter__()

    # Public methods

    def keys(self):
        '''
        @return: Returns the list of keys in preferences.
        @rtype: list
        '''
        return self._prefs.keys()

    def items(self):
        '''
        @return: Returns the list of items in preferences.
        @rtype: list of (key, value) tuples
        '''
        return self._prefs.items()

    def iteritems(self):
        '''
        @return: Iterates on the items in preferences.
        @rtype: yields items that are (key, value) pairs
        '''
        return six.iteritems(self._prefs)

    def save(self, filename=None):
        '''
        Saves the preferences to disk. If filename is not specified,
        use the default one if it is set, else do nothing.
        @param filename: Optional alternate file to use.
        @type filename: str
        '''
        if filename is None:
            filename = self.filename

        if filename is not None:
            fsock = open(filename, 'wb')
            fcntl.lockf(fsock, fcntl.LOCK_UN)
            try:
                six.moves.cPickle.dump(self._prefs, fsock, 2)
            finally:
                fsock.close()

    def load(self, filename=None):
        '''
        Loads the preferences from file. Use either the supplied filename,
        or the default one if set. Else, do nothing.
        '''
        if filename is None:
            filename = self.filename

        if filename is not None and os.path.exists(filename):
            fsock = open(filename, 'rb')
            fcntl.lockf(fsock, fcntl.LOCK_SH)
            try:
                self._prefs = six.moves.cPickle.load(fsock)
            finally:
                fsock.close()
