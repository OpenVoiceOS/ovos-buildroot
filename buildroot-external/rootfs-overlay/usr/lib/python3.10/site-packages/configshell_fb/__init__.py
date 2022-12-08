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

if __name__ == 'configshell-fb':
    from warnings import warn
    warn("'configshell' package name for configshell-fb is deprecated, please"
         + " instead import 'configshell_fb'", UserWarning, stacklevel=2)

from .console import Console
from .log import Log
from .node import ConfigNode, ExecutionError
from .prefs import Prefs
from .shell import ConfigShell

__version__ = '1.1.29'
__url__ = 'http://github.com/open-iscsi/configshell-fb'
__description__ = 'A framework to implement simple but nice CLIs.'
__license__ = 'Apache 2.0'
