import os
import sys
import tempfile
import platform
from collections import OrderedDict

MEM_BASED_FS = ['tmpfs', 'ramfs']
SUITABLE_PATHS = ['/tmp', '/run/user/{uid}', '/run/shm', '/dev/shm']


class MemoryTempfile:
    def __init__(self, preferred_paths: list = None, remove_paths: list or bool = None,
                 additional_paths: list = None, filesystem_types: list = None,
                 fallback: str or bool = None):
        self.os_tempdir = tempfile.gettempdir()
        suitable_paths = [self.os_tempdir] + SUITABLE_PATHS
        
        if isinstance(fallback, bool):
            self.fallback = self.os_tempdir if fallback else None
        else:
            self.fallback = fallback

        if platform.system() == "Linux":
            self.filesystem_types = list(filesystem_types) if filesystem_types is not None else MEM_BASED_FS
            
            preferred_paths = [] if preferred_paths is None else preferred_paths

            if isinstance(remove_paths, bool) and remove_paths:
                suitable_paths = []
            elif isinstance(remove_paths, list) and len(remove_paths) > 0:
                suitable_paths = [i for i in suitable_paths if i not in remove_paths]
            
            additional_paths = [] if additional_paths is None else additional_paths

            self.suitable_paths = preferred_paths + suitable_paths + additional_paths
    
            uid = os.geteuid()
            
            with open('/proc/self/mountinfo', 'r') as file:
                mnt_info = {i[2]: i for i in [line.split() for line in file]}
            
            self.usable_paths = OrderedDict()
            for path in self.suitable_paths:
                path = path.replace('{uid}', str(uid))
                
                # We may have repeated
                if self.usable_paths.get(path) is not None:
                    continue
                self.usable_paths[path] = False
                try:
                    dev = os.stat(path).st_dev
                    major, minor = os.major(dev), os.minor(dev)
                    mp = mnt_info.get("{}:{}".format(major, minor))
                    if mp and mp[8] in self.filesystem_types:
                        self.usable_paths[path] = mp
                except FileNotFoundError:
                    pass
            
            for key in [k for k, v in self.usable_paths.items() if not v]:
                del self.usable_paths[key]
            
            if len(self.usable_paths) > 0:
                self.tempdir = next(iter(self.usable_paths.keys()))
            else:
                if fallback:
                    self.tempdir = self.fallback
                else:
                    raise RuntimeError('No memory temporary dir found and fallback is disabled.')

    def found_mem_tempdir(self):
        return len(self.usable_paths) > 0
    
    def using_mem_tempdir(self):
        return self.tempdir in self.usable_paths
    
    def get_usable_mem_tempdir_paths(self):
        return list(self.usable_paths.keys())
    
    def gettempdir(self):
        return self.tempdir

    def gettempdirb(self):
        return self.tempdir.encode(sys.getfilesystemencoding(), 'surrogateescape')

    def mkdtemp(self, suffix=None, prefix=None, dir=None):
        return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir)
    
    def mkstemp(self, suffix=None, prefix=None, dir=None, text=False):
        return tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir, text=text)

    def TemporaryDirectory(self, suffix=None, prefix=None, dir=None):
        return tempfile.TemporaryDirectory(suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir)
    
    def SpooledTemporaryFile(self, max_size=0, mode='w+b', buffering=-1, encoding=None, newline=None,
                             suffix=None, prefix=None, dir=None):
        return tempfile.SpooledTemporaryFile(max_size=max_size, mode=mode, buffering=buffering, encoding=encoding,
                                             newline=newline, suffix=suffix, prefix=prefix,
                                             dir=self.tempdir if not dir else dir)

    def NamedTemporaryFile(self, mode='w+b', buffering=-1, encoding=None, newline=None,
                           suffix=None, prefix=None, dir=None, delete=True):
        return tempfile.NamedTemporaryFile(mode=mode, buffering=buffering, encoding=encoding, newline=newline,
                                           suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir,
                                           delete=delete)
    
    def TemporaryFile(self, mode='w+b', buffering=-1, encoding=None, newline=None,
                      suffix=None, prefix=None, dir=None):
        return tempfile.TemporaryFile(mode=mode, buffering=buffering, encoding=encoding, newline=newline,
                                      suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir)
    
    def gettempprefix(self):
        return tempfile.gettempdir()
    
    def gettempprefixb(self):
        return tempfile.gettempprefixb()
