from py_mplayer.log import LOG
from subprocess import Popen, PIPE
from queue import Queue
import sys
from pyee import EventEmitter
import threading
from urllib.request import Request
from urllib.request import urlopen
from re import sub


class BaseMplayerCtrlException(Exception):
    '''The exception is used as base for all other exceptions,
    useful to catch all exception thrown by the MplayerCtrl'''

    def __init__(self, *args):
        self.args = [repr(a).strip('\'') for a in args]

    def __str__(self):
        ret = ', '.join(self.args)
        LOG.error('Exception: <%s>: %s' % (self.__class__.__name__, ret))
        return ret


class AnsError(BaseMplayerCtrlException):
    '''The Exception is raised, if an ANS_ERROR is returned by the
    mplayer process.
    Reasons can be:
        * wrong value
        * unknown property
        * property is unavailable, e.g. the chapter property used
        while playing a stream'''


class BuildProcessError(BaseMplayerCtrlException):
    '''The Exception is raised, if the path to the mplayer(.exe) is incorrect
    or another error occurs while building the mplayer path'''


class NoMplayerRunning(BaseMplayerCtrlException):
    '''The Exception is raised, if you try to call a method/property of the
    MplayerCtrl and no mplayer process is running'''


class MplayerStdoutEvents(threading.Thread):
    '''Class to handle the Stdout of a (Mplayer)process

    Some Events are posted

    * EVT_STDOUT
    * EVT_MEDIA_STARTED
    * EVT_MEDIA_FINISHED
    * EVT_PROCESS_STOPPED
    '''

    def __init__(self, mpc, stdout, queue):
        threading.Thread.__init__(self, name='MplayerStdoutEvents')
        self.setDaemon(True)
        self.mpc = mpc
        self.stdout = stdout
        self.queue = queue

    def run(self):
        self.mpc.ee.emit("mplayer_process_started", {})
        media = False
        while True:
            line = self.stdout.readline()
            if self.mpc.debug:
                LOG.debug("stdout: " + line)
            if not line:
                self.mpc.ee.emit("mplayer_process_stopped", {})
                break
            elif line == '\n':  # universal_newlines = True (subprocess)!
                if media:
                    self.mpc.ee.emit("mplayer_media_finished", {})
                    media = False
                    continue
            elif 'icy info' in line.lower():
                if not media:
                    self.mpc.ee.emit("mplayer_media_started", {"data": line.rstrip()})
                    media = True
                    continue
            elif line.lower() == 'starting playback...\n':
                if not media:
                    self.mpc.ee.emit("mplayer_media_started", {})
                    media = True
                    continue
            else:
                if line.upper().startswith('ANS_') and '=' in line:
                    self.queue.put_nowait(line)
                self.mpc.ee.emit("mplayer_stdout", {"data": line.rstrip()})


class MplayerStderrEvents(threading.Thread):
    '''Class to handle the Stderr of a (Mplayer)process

    Some Events are posted, using wx.PostEvent
    * EVT_STDERR'''

    def __init__(self, mpc, stderr, stdout_event_thread):
        threading.Thread.__init__(self, name='MplayerStderrEvents')
        self.setDaemon(True)
        self.mpc = mpc
        self.stderr = stderr
        self._stdout_event_thread = stdout_event_thread

    def run(self):
        while self._stdout_event_thread.isAlive():
            line = self.stderr.readline().strip()
            if self.mpc.debug:
                LOG.debug('stderr ' + line)
            if not line:
                break
            else:
                self.mpc.ee.emit("mplayer_stderr", {"data": line})


class MplayerCtrl(object):
    ''' handles the mplayer process, using the subprocess-module'''
    ee = EventEmitter()
    # -slave http://www.mplayerhq.hu/DOCS/tech/slave.txt
    if sys.version_info[:2] < (2, 6):
        float_ = lambda x: sys.maxint if x == 'inf' else -sys.maxint
    else:
        float_ = float

    VO_DRIVER = 'xmega,xv,'
    AO_DRIVER = 'alsa,'
    STARTUPINFO = None
    # A dictionary with all available properties
    # mplayer_prop : information
    PROPERTIES = {'angle': {'doc': 'select angle',
                            'get': True,
                            'max': float_('inf'),
                            'min': 0.0,
                            'name': 'angle',
                            'set': True,
                            'step': True,
                            'type': 'int'},
                  'aspect': {'doc': '',
                             'get': True,
                             'max': float_('inf'),
                             'min': float_('-inf'),
                             'name': 'aspect',
                             'set': False,
                             'step': False,
                             'type': 'float'},
                  'audio_bitrate': {'doc': '',
                                    'get': True,
                                    'max': float_('inf'),
                                    'min': float_('-inf'),
                                    'name': 'audio_bitrate',
                                    'set': False,
                                    'step': False,
                                    'type': 'int'},
                  'audio_codec': {'doc': '',
                                  'get': True,
                                  'max': float_('inf'),
                                  'min': float_('-inf'),
                                  'name': 'audio_codec',
                                  'set': False,
                                  'step': False,
                                  'type': 'string'},
                  'audio_delay': {'doc': '',
                                  'get': True,
                                  'max': 100.0,
                                  'min': -100.0,
                                  'name': 'audio_delay',
                                  'set': True,
                                  'step': True,
                                  'type': 'float'},
                  'audio_format': {'doc': '',
                                   'get': True,
                                   'max': float_('inf'),
                                   'min': float_('-inf'),
                                   'name': 'audio_format',
                                   'set': False,
                                   'step': False,
                                   'type': 'int'},
                  'balance': {'doc': 'change audio balance',
                              'get': True,
                              'max': 1.0,
                              'min': -1.0,
                              'name': 'balance',
                              'set': True,
                              'step': True,
                              'type': 'float'},
                  'border': {'doc': '',
                             'get': True,
                             'max': 1.0,
                             'min': 0.0,
                             'name': 'border',
                             'set': True,
                             'step': True,
                             'type': 'flag'},
                  'brightness': {'doc': '',
                                 'get': True,
                                 'max': 100.0,
                                 'min': -100.0,
                                 'name': 'brightness',
                                 'set': True,
                                 'step': True,
                                 'type': 'int'},
                  'channels': {'doc': '',
                               'get': True,
                               'max': float_('inf'),
                               'min': float_('-inf'),
                               'name': 'channels',
                               'set': False,
                               'step': False,
                               'type': 'int'},
                  'chapter': {'doc': 'select chapter',
                              'get': True,
                              'max': float_('inf'),
                              'min': 0.0,
                              'name': 'chapter',
                              'set': True,
                              'step': True,
                              'type': 'int'},
                  'chapters': {'doc': 'number of chapters',
                               'get': True,
                               'max': float_('inf'),
                               'min': float_('-inf'),
                               'name': 'chapters',
                               'set': False,
                               'step': False,
                               'type': 'int'},
                  'contrast': {'doc': '',
                               'get': True,
                               'max': 100.0,
                               'min': -100.0,
                               'name': 'contrast',
                               'set': True,
                               'step': True,
                               'type': 'int'},
                  'deinterlace': {'doc': '',
                                  'get': True,
                                  'max': 1.0,
                                  'min': 0.0,
                                  'name': 'deinterlace',
                                  'set': True,
                                  'step': True,
                                  'type': 'flag'},
                  'demuxer': {'doc': 'demuxer used',
                              'get': True,
                              'max': float_('inf'),
                              'min': float_('-inf'),
                              'name': 'demuxer',
                              'set': False,
                              'step': False,
                              'type': 'string'},
                  'filename': {'doc': 'file playing wo path',
                               'get': True,
                               'max': float_('inf'),
                               'min': float_('-inf'),
                               'name': 'filename',
                               'set': False,
                               'step': False,
                               'type': 'string'},
                  'fps': {'doc': '',
                          'get': True,
                          'max': float_('inf'),
                          'min': float_('-inf'),
                          'name': 'fps',
                          'set': False,
                          'step': False,
                          'type': 'float'},
                  'framedropping': {'doc': '1 = soft, 2 = hard',
                                    'get': True,
                                    'max': 2.0,
                                    'min': 0.0,
                                    'name': 'framedropping',
                                    'set': True,
                                    'step': True,
                                    'type': 'int'},
                  'fullscreen': {'doc': '',
                                 'get': True,
                                 'max': 1.0,
                                 'min': 0.0,
                                 'name': 'fullscreen',
                                 'set': True,
                                 'step': True,
                                 'type': 'flag'},
                  'gamma': {'doc': '',
                            'get': True,
                            'max': 100.0,
                            'min': -100.0,
                            'name': 'gamma',
                            'set': True,
                            'step': True,
                            'type': 'int'},
                  'height': {'doc': '"display" height',
                             'get': True,
                             'max': float_('inf'),
                             'min': float_('-inf'),
                             'name': 'height',
                             'set': False,
                             'step': False,
                             'type': 'int'},
                  'hue': {'doc': '',
                          'get': True,
                          'max': 100.0,
                          'min': -100.0,
                          'name': 'hue',
                          'set': True,
                          'step': True,
                          'type': 'int'},
                  'length': {'doc': 'length of file in seconds',
                             'get': True,
                             'max': float_('inf'),
                             'min': float_('-inf'),
                             'name': 'length',
                             'set': False,
                             'step': False,
                             'type': 'time'},
                  'loop': {'doc': 'as -loop',
                           'get': True,
                           'max': float_('inf'),
                           'min': -1.0,
                           'name': 'loop',
                           'set': True,
                           'step': True,
                           'type': 'int'},
                  'metadata': {'doc': 'list of metadata key/value',
                               'get': True,
                               'max': float_('inf'),
                               'min': float_('-inf'),
                               'name': 'metadata',
                               'set': False,
                               'step': False,
                               'type': 'str list'},
                  'mute': {'doc': '',
                           'get': True,
                           'max': 1.0,
                           'min': 0.0,
                           'name': 'mute',
                           'set': True,
                           'step': True,
                           'type': 'flag'},
                  'ontop': {'doc': '',
                            'get': True,
                            'max': 1.0,
                            'min': 0.0,
                            'name': 'ontop',
                            'set': True,
                            'step': True,
                            'type': 'flag'},
                  'osdlevel': {'doc': 'as -osdlevel',
                               'get': True,
                               'max': 3.0,
                               'min': 0.0,
                               'name': 'osdlevel',
                               'set': True,
                               'step': True,
                               'type': 'int'},
                  'panscan': {'doc': '',
                              'get': True,
                              'max': 1.0,
                              'min': 0.0,
                              'name': 'panscan',
                              'set': True,
                              'step': True,
                              'type': 'float'},
                  'path': {'doc': 'file playing',
                           'get': True,
                           'max': float_('inf'),
                           'min': float_('-inf'),
                           'name': 'path',
                           'set': False,
                           'step': False,
                           'type': 'string'},
                  'pause': {'doc': '1 if paused, use with '
                                    'pausing_keep_force',
                            'get': True,
                            'max': 1.0,
                            'min': 0.0,
                            'name': 'paused',
                            'set': False,
                            'step': False,
                            'type': 'flag'},
                  'percent_pos': {'doc': 'position in percent',
                                  'get': True,
                                  'max': 100.0,
                                  'min': 0.0,
                                  'name': 'percent_pos',
                                  'set': True,
                                  'step': True,
                                  'type': 'int'},
                  'rootwin': {'doc': '',
                              'get': True,
                              'max': 1.0,
                              'min': 0.0,
                              'name': 'rootwin',
                              'set': True,
                              'step': True,
                              'type': 'flag'},
                  'samplerate': {'doc': '',
                                 'get': True,
                                 'max': float_('inf'),
                                 'min': float_('-inf'),
                                 'name': 'samplerate',
                                 'set': False,
                                 'step': False,
                                 'type': 'int'},
                  'saturation': {'doc': '',
                                 'get': True,
                                 'max': 100.0,
                                 'min': -100.0,
                                 'name': 'saturation',
                                 'set': True,
                                 'step': True,
                                 'type': 'int'},
                  'speed': {'doc': 'as -speed',
                            'get': True,
                            'max': 100.0,
                            'min': 0.01,
                            'name': 'speed',
                            'set': True,
                            'step': True,
                            'type': 'float'},
                  'stream_end': {'doc': 'end pos in stream',
                                 'get': True,
                                 'max': float_('inf'),
                                 'min': 0.0,
                                 'name': 'stream_end',
                                 'set': False,
                                 'step': False,
                                 'type': 'pos'},
                  'stream_length': {'doc': '(end - start)',
                                    'get': True,
                                    'max': float_('inf'),
                                    'min': 0.0,
                                    'name': 'stream_length',
                                    'set': False,
                                    'step': False,
                                    'type': 'pos'},
                  'stream_pos': {'doc': 'position in stream',
                                 'get': True,
                                 'max': float_('inf'),
                                 'min': 0.0,
                                 'name': 'stream_pos',
                                 'set': True,
                                 'step': False,
                                 'type': 'pos'},
                  'stream_start': {'doc': 'start pos in stream',
                                   'get': True,
                                   'max': float_('inf'),
                                   'min': 0.0,
                                   'name': 'stream_start',
                                   'set': False,
                                   'step': False,
                                   'type': 'pos'},
                  'sub': {'doc': 'select subtitle stream',
                          'get': True,
                          'max': float_('inf'),
                          'min': -1.0,
                          'name': 'sub',
                          'set': True,
                          'step': True,
                          'type': 'int'},
                  'sub_alignment': {'doc': 'subtitle alignment',
                                    'get': True,
                                    'max': 2.0,
                                    'min': 0.0,
                                    'name': 'sub_alignment',
                                    'set': True,
                                    'step': True,
                                    'type': 'int'},
                  'sub_delay': {'doc': '',
                                'get': True,
                                'max': float_('inf'),
                                'min': float_('-inf'),
                                'name': 'sub_delay',
                                'set': True,
                                'step': True,
                                'type': 'float'},
                  'sub_demux': {'doc': 'select subs from demux',
                                'get': True,
                                'max': float_('inf'),
                                'min': -1.0,
                                'name': 'sub_demux',
                                'set': True,
                                'step': True,
                                'type': 'int'},
                  'sub_file': {'doc': 'select file subtitles',
                               'get': True,
                               'max': float_('inf'),
                               'min': -1.0,
                               'name': 'sub_file',
                               'set': True,
                               'step': True,
                               'type': 'int'},
                  'sub_forced_only': {'doc': '',
                                      'get': True,
                                      'max': 1.0,
                                      'min': 0.0,
                                      'name': 'sub_forced_only',
                                      'set': True,
                                      'step': True,
                                      'type': 'flag'},
                  'sub_pos': {'doc': 'subtitle position',
                              'get': True,
                              'max': 100.0,
                              'min': 0.0,
                              'name': 'sub_pos',
                              'set': True,
                              'step': True,
                              'type': 'int'},
                  'sub_scale': {'doc': 'subtitles font size',
                                'get': True,
                                'max': 100.0,
                                'min': 0.0,
                                'name': 'sub_scale',
                                'set': True,
                                'step': True,
                                'type': 'float'},
                  'sub_source': {'doc': 'select subtitle source',
                                 'get': True,
                                 'max': 2.0,
                                 'min': -1.0,
                                 'name': 'sub_source',
                                 'set': True,
                                 'step': True,
                                 'type': 'int'},
                  'sub_visibility': {'doc': 'show/hide subtitles',
                                     'get': True,
                                     'max': 1.0,
                                     'min': 0.0,
                                     'name': 'sub_visibility',
                                     'set': True,
                                     'step': True,
                                     'type': 'flag'},
                  'sub_vob': {'doc': 'select vobsubs',
                              'get': True,
                              'max': float_('inf'),
                              'min': -1.0,
                              'name': 'sub_vob',
                              'set': True,
                              'step': True,
                              'type': 'int'},
                  'switch_angle': {'doc': 'select DVD angle',
                                   'get': True,
                                   'max': 255.0,
                                   'min': -2.0,
                                   'name': 'switch_angle',
                                   'set': True,
                                   'step': True,
                                   'type': 'int'},
                  'switch_audio': {'doc': 'select audio stream',
                                   'get': True,
                                   'max': 255.0,
                                   'min': -2.0,
                                   'name': 'switch_audio',
                                   'set': True,
                                   'step': True,
                                   'type': 'int'},
                  'switch_program': {'doc': '(see TAB default keybind)',
                                     'get': True,
                                     'max': 65535.0,
                                     'min': -1.0,
                                     'name': 'switch_program',
                                     'set': True,
                                     'step': True,
                                     'type': 'int'},
                  'switch_title': {'doc': 'select DVD title',
                                   'get': True,
                                   'max': 255.0,
                                   'min': -2.0,
                                   'name': 'switch_title',
                                   'set': True,
                                   'step': True,
                                   'type': 'int'},
                  'switch_video': {'doc': 'select video stream',
                                   'get': True,
                                   'max': 255.0,
                                   'min': -2.0,
                                   'name': 'switch_video',
                                   'set': True,
                                   'step': True,
                                   'type': 'int'},
                  'teletext_format': {'doc': '0 - opaque, 1 - transparent, ' \
                                             '2 - opaque inverted, 3 - transp. inv.',
                                      'get': True,
                                      'max': 3.0,
                                      'min': 0.0,
                                      'name': 'teletext_format',
                                      'set': True,
                                      'step': True,
                                      'type': 'int'},
                  'teletext_half_page': {'doc': '0 - off, 1 - top half, ' \
                                                '2- bottom half',
                                         'get': True,
                                         'max': 2.0,
                                         'min': 0.0,
                                         'name': 'teletext_half_page',
                                         'set': True,
                                         'step': True,
                                         'type': 'int'},
                  'teletext_mode': {'doc': '0 - off, 1 - on',
                                    'get': True,
                                    'max': 1.0,
                                    'min': 0.0,
                                    'name': 'teletext_mode',
                                    'set': True,
                                    'step': True,
                                    'type': 'flag'},
                  'teletext_page': {'doc': '',
                                    'get': True,
                                    'max': 799.0,
                                    'min': 0.0,
                                    'name': 'teletext_page',
                                    'set': True,
                                    'step': True,
                                    'type': 'int'},
                  'teletext_subpage': {'doc': '',
                                       'get': True,
                                       'max': 64.0,
                                       'min': 0.0,
                                       'name': 'teletext_subpage',
                                       'set': True,
                                       'step': True,
                                       'type': 'int'},
                  'time_pos': {'doc': 'position in seconds',
                               'get': True,
                               'max': float_('inf'),
                               'min': 0.0,
                               'name': 'time_pos',
                               'set': True,
                               'step': True,
                               'type': 'time'},
                  'tv_brightness': {'doc': '',
                                    'get': True,
                                    'max': 100.0,
                                    'min': -100.0,
                                    'name': 'tv_brightness',
                                    'set': True,
                                    'step': True,
                                    'type': 'int'},
                  'tv_contrast': {'doc': '',
                                  'get': True,
                                  'max': 100.0,
                                  'min': -100.0,
                                  'name': 'tv_contrast',
                                  'set': True,
                                  'step': True,
                                  'type': 'int'},
                  'tv_hue': {'doc': '',
                             'get': True,
                             'max': 100.0,
                             'min': -100.0,
                             'name': 'tv_hue',
                             'set': True,
                             'step': True,
                             'type': 'int'},
                  'tv_saturation': {'doc': '',
                                    'get': True,
                                    'max': 100.0,
                                    'min': -100.0,
                                    'name': 'tv_saturation',
                                    'set': True,
                                    'step': True,
                                    'type': 'int'},
                  'video_bitrate': {'doc': '',
                                    'get': True,
                                    'max': float_('inf'),
                                    'min': float_('-inf'),
                                    'name': 'video_bitrate',
                                    'set': False,
                                    'step': False,
                                    'type': 'int'},
                  'video_codec': {'doc': '',
                                  'get': True,
                                  'max': float_('inf'),
                                  'min': float_('-inf'),
                                  'name': 'video_codec',
                                  'set': False,
                                  'step': False,
                                  'type': 'string'},
                  'video_format': {'doc': '',
                                   'get': True,
                                   'max': float_('inf'),
                                   'min': float_('-inf'),
                                   'name': 'video_format',
                                   'set': False,
                                   'step': False,
                                   'type': 'int'},
                  'volume': {'doc': 'change volume',
                             'get': True,
                             'max': 100.0,
                             'min': 0.0,
                             'name': 'volume',
                             'set': True,
                             'step': True,
                             'type': 'float'},
                  'vsync': {'doc': '',
                            'get': True,
                            'max': 1.0,
                            'min': 0.0,
                            'name': 'vsync',
                            'set': True,
                            'step': True,
                            'type': 'flag'},
                  'width': {'doc': '"display" width',
                            'get': True,
                            'max': float_('inf'),
                            'min': float_('-inf'),
                            'name': 'width',
                            'set': False,
                            'step': False,
                            'type': 'int'}
                  }

    def __new__(cls, *args, **kwargs):
        # creating property setters and getters
        def property_getter(property):
            # for compatibility with method name
            if property == "paused":
                property = "pause"

            def fget(self):
                return self.get_property(property)

            return fget

        def property_setter(property):

            def fset(self, value):
                return self.set_property(property, value)

            return fset

        # defining the properties
        for mprop, prop_dict in cls.PROPERTIES.items():
            pdoc, pname = prop_dict['doc'], prop_dict['name']
            fget = property_getter(mprop)  # mprop != unicode
            # (in ascii range that's ok)
            fset = None
            if prop_dict['set']:
                fset = property_setter(mprop)
            prop = property(fget=fget, fset=fset, doc=pdoc)
            setattr(cls, pname, prop)

        return super(MplayerCtrl, cls).__new__(cls)

    def __init__(self, mplayer_path="mplayer", media_file=None,
                 mplayer_args=None, keep_pause=False, debug=False, *args,
                 **kwargs):
        ''' *args are arguments for the mplayer
        process. Just use it, if you know what you're doing.
        media_file can be a URL, a file (path), stream, everything
        the mplayer is able to play to.
        Mplayer_args must be a list or None.
        The arguments in mplayer_args are passed to the mplayer process.
        You should never add -msglevel and -wid to args..'''
        self._stdout_queue = Queue()
        self.mplayer_path = mplayer_path
        self.keep_pause = keep_pause

        self.playing = False
        self.debug = debug
        self.args = []
        self._process = None
        self._stdout = None
        self._stderr = None
        self._stdin = None

        self.ee.on("mplayer_media_started", self.on_media_started)
        self.ee.on("mplayer_media_finished", self.on_media_finished)
        self.ee.on("mplayer_process_started", self.on_process_started)
        self.ee.on("mplayer_process_stopped", self.on_process_stopped)
        self.ee.on("mplayer_stderr", self.on_stderr)
        self.ee.on("mplayer_stdout", self.on_stdout)

        self.start(media_file=media_file, mplayer_args=mplayer_args)

    def _start_process(self, media_file, mplayer_args):
        if not mplayer_args is None:
            args = [self.mplayer_path, '-msglevel', 'all=4']
            args.extend(mplayer_args)
        else:
            args = [self.mplayer_path, '-slave',
                    '-noconsolecontrols', '-idle',
                    '-msglevel', 'all=4']
        # required args
        for tup in [('-vo', self.VO_DRIVER), ('-ao', self.AO_DRIVER),
                    ('-slave', False),
                    ('-idle', False)]:
            if not tup[0] in args:
                args.extend(tup)

        if not '-input' in args:
            args.extend(
                ('-input', 'conf=/dev/null', '-input', 'nodefault-bindings'))
        # -
        if not media_file is None:
            args.append(media_file)

        if self._process is None:
            args = [str(arg).encode(sys.getfilesystemencoding())
                    for arg in filter(None, args)]
            self.args = args
            try:
                if self.debug:
                    LOG.debug("args: " + str(args))
                self._process = Popen(args, stdin=PIPE, stdout=PIPE,
                                      stderr=PIPE, universal_newlines=True,
                                      startupinfo=self.STARTUPINFO)
            except Exception as e:
                LOG.error(e)
                raise BuildProcessError(str(e))
            self._stdin = self._process.stdin
            self._stdout = self._process.stdout
            self._stderr = self._process.stderr
            mse = MplayerStdoutEvents(self, self._stdout, self._stdout_queue)
            mse.start()
            MplayerStderrEvents(self, self._stderr, mse).start()

    def start(self, media_file=None, mplayer_args=None):
        '''Builds a new process, if the old process got killed by Quit().
        Returns True if the process is created successfully,otherwise False'''
        if self._process is None:
            self._start_process(media_file, mplayer_args)
        return self.process_alive

    # own events
    def on_media_started(self, evt):
        self.playing = True
        if evt.get('data') is None:
            LOG.info("media started")
        else:
            LOG.info("media started: " + str(evt['data']))

    def on_media_finished(self, evt):
        self.playing = False
        LOG.info("media finished")

    def on_process_started(self, evt):
        LOG.info("process started")

    def on_process_stopped(self, evt):
        LOG.info("process finished")
        self.playing = False

    def on_stderr(self, evt):
        LOG.error(str(evt))

    def on_stdout(self, evt):
        if self.debug:
            LOG.debug(str(evt))

    def _run_cmd(self, cmd, *args):
        if not self.process_alive:
            raise NoMplayerRunning('You have first to start the mplayer,'
                                   'use Start()')
        args = u' '.join(str(i).replace(u' ', u'\\ ')
                         for i in args if not i is None)
        args.replace(u'\\', u'\\\\')  # escape escaped backslashes :D
        if self.debug:
            LOG.debug('%r, %r' % (cmd, args), 'running command')

        if self.keep_pause:
            stostdin = u'pausing_keep %s %s\n\n' % (cmd, args)
        else:
            stostdin = u'%s %s\n\n' % (cmd, args)

        self._stdin.write(stostdin)
        self._stdin.flush()

    def _get_from_queue(self):
        if self.playing:
            ret = self._stdout_queue.get(True, 0.5)
            if self.debug:
                LOG.debug('get_from_queue: ' + ret)
            parsed_ret = _parse_stdout(ret)
            self._stdout_queue.task_done()
            if parsed_ret[0] == 'ANS_ERROR':
                raise AnsError(parsed_ret[1])
            return parsed_ret[1]

    @property
    def process_alive(self):
        '''Returns True if the process is still alive otherwise False'''
        if self._process is not None:
            return self._process.poll() is None
        else:
            return False

    def alt_src_step(self, value):
        '''(ASX playlist only)
        When more than one source is available it selects
        the next/previous one.'''
        self._run_cmd(u'alt_src_step', value)

    def audio_delay(self, value, abs=None):
        '''Set/adjust the audio delay.
        If [abs] is not given or is zero, adjust the delay by <value> seconds.
        If [abs] is nonzero, set the delay to <value> seconds.'''
        self._run_cmd(u'audio_delay', value, abs)

    def brightness(self, value, abs=None):
        '''Set/adjust video brightness.
        If [abs] is not given or is zero, modifies parameter by <value>.
        If [abs] is non-zero, parameter is set to <value>.
        <value> is in the range [-100, 100].'''
        self._run_cmd(u'brightness', value, abs)

    def contrast(self, value, abs=None):
        '''Set/adjust video contrast.
        If [abs] is not given or is zero, modifies parameter by <value>.
        If [abs] is non-zero, parameter is set to <value>.
        <value> is in the range [-100, 100].'''
        self._run_cmd(u'contrast', value, abs)

    def gamma(self, value, abs=None):
        '''Set/adjust video gamma.
        If [abs] is not given or is zero, modifies parameter by <value>.
        If [abs] is non-zero, parameter is set to <value>.
        <value> is in the range [-100, 100].'''
        self._run_cmd(u'gamma', value, abs)

    def hue(self, value, abs=None):
        '''Set/adjust video hue.
        If [abs] is not given or is zero, modifies parameter by <value>.
        If [abs] is non-zero, parameter is set to <value>.
        <value> is in the range [-100, 100].'''
        self._run_cmd(u'hue', value, abs)

    def saturation(self, value, abs=None):
        '''Set/adjust video saturation.
        If [abs] is not given or is zero, modifies parameter by <value>.
        If [abs] is non-zero, parameter is set to <value>.
        <value> is in the range [-100, 100].'''
        self._run_cmd(u'saturation', value, abs)

    def change_rectangele(self, val1, val2):
        '''Change the position of the rectangle filter rectangle.
            <val1> Must be one of the following:
              * 0 = width
              * 1 = height
              * 2 = x position
              * 3 = y position
            <val2>
              * If <val1> is 0 or 1:
                * Integer amount to add/subtract from the width/height.
                 Positive values add to width/height and negative values
                 subtract from it.
              * If <val1> is 2 or 3:
                * Relative integer amount by which to move the upper left
                 rectangle corner. Positive values move the rectangle
                 right/down and negative values move the rectangle left/up.'''
        self._run_cmd(u'change_rectangle', val1, val2)

    def dvb_set_channel(self, channel_number, card_number):
        '''Set DVB channel'''
        self._run_cmd(u'dvb_set_channel', channel_number, card_number)

    def dvdnav(self, button_name):
        '''Press the given dvdnav button.
            up
            down
            left
            right
            menu
            select
            prev
            mouse'''
        self._run_cmd(u'dvdnav', button_name)

    def edlmark(self):
        '''Write the current position into the EDL file.'''
        self._run_cmd(u'edl_mark')

    def frame_drop(self, value):
        '''Toggle/set frame dropping mode.'''
        self._run_cmd(u'frame_drop', value)

    def get_audio_bitrate(self):
        '''Returns the audio bitrate of the current file.'''
        self._run_cmd(u'get_audio_bitrate')
        return self._get_from_queue()

    def get_audio_codec(self):
        '''Returns the audio codec name of the current file.'''
        self._run_cmd(u'get_audio_codec')
        return self._get_from_queue()

    def get_audio_samples(self):
        '''Returns the audio frequency and number
        of channels of the current file.'''
        self._run_cmd(u'get_audio_samples')
        return self._get_from_queue()

    def get_file_name(self):
        '''Retruns the name of the current file.'''
        self._run_cmd(u'get_file_name')
        return self._get_from_queue()

    def get_meta_album(self):
        '''Returns the "Album" metadata of the current file.'''
        self._run_cmd(u'get_meta_album')
        return self._get_from_queue()

    def get_meta_artist(self):
        '''Returns the "Artist" metadata of the current file.'''
        self._run_cmd(u'get_meta_artist')
        return self._get_from_queue()

    def get_meta_comment(self):
        '''Returns the "Comment" metadata of the current file.'''
        self._run_cmd(u'get_meta_comment')
        return self._get_from_queue()

    def get_meta_genre(self):
        '''Returns the "Genre" metadata of the current file.'''
        self._run_cmd(u'get_meta_genre')
        return self._get_from_queue()

    def get_meta_title(self):
        '''Returns the "Title" metadata of the current file.'''
        self._run_cmd(u'get_meta_title')
        return self._get_from_queue()

    def get_meta_track(self):
        '''Returns the "Track" metadata of the current file.'''
        self._run_cmd(u'get_meta_track')
        return self._get_from_queue()

    def get_meta_year(self):
        '''Returns the "Year" metadata of the current file.'''
        self._run_cmd(u'get_meta_year')
        return self._get_from_queue()

    def get_percent_pos(self):
        '''Returns the current position in the file,
        as integer percentage [0-100].'''
        self._run_cmd(u'get_percent_pos')
        return self._get_from_queue()

    def get_property(self, property):
        '''Returns the current value of a property.
        All possible properties in PROPERTIES
        If property isn't a "get-property", raises AnsError'''
        property = property.lower()
        self._run_cmd(u'get_property', property)
        ret = self._get_from_queue()
        if property == 'metadata':
            # metadata looks like that: key1,value1,key2,value2,key3,value3...
            # let's make a dict out of it!
            key, value = ret.split(',')[::2], ret.split(',')[1::2]
            ret = dict(zip(key, map(_get_type, value)))
        return ret

    def get_sub_visibility(self):
        '''Returns subtitle visibility (1 == on, 0 == off).'''
        self._run_cmd(u'get_sub_visibility')
        return self._get_from_queue()

    def get_time_length(self):
        '''Returns the length of the current file in seconds.'''
        self._run_cmd(u'get_time_length')
        return self._get_from_queue()

    def get_time_pos(self):
        '''Returns the current position in the file in seconds, as float.'''
        self._run_cmd(u'get_time_pos')
        return self._get_from_queue()

    def get_vo_fullscreen(self):
        '''Returns fullscreen status (1 == fullscreened, 0 == windowed).'''
        self._run_cmd(u'get_vo_fullscreen')
        return self._get_from_queue()

    def get_video_bitrate(self):
        '''Returns the video bitrate of the current file.'''
        self._run_cmd(u'get_video_bitrate')
        return self._get_from_queue()

    def get_video_codec(self):
        '''Returns out the video codec name of the current file.'''
        self._run_cmd(u'get_video_codec')
        return self._get_from_queue()

    def get_video_resolution(self):
        '''Returns the video resolution of the current file.'''
        self._run_cmd(u'get_video_resolution')
        return self._get_from_queue()

    def screenshot(self, value):
        '''Take a screenshot. Requires the screenshot filter to be loaded.
            0 Take a single screenshot.
            1 Start/stop taking screenshot of each frame.'''
        self._run_cmd(u'screenshot', value)

    def key_down_event(self, value):
        '''Inject <value> key code event into MPlayer.'''
        self._run_cmd(u'key_down_event', value)

    def loadfile(self, file_url, append=None):
        '''Load the given file/URL, stopping playback of the current file/URL.
        If <append> is nonzero playback continues and the file/URL is
        appended to the current playlist instead.'''
        # check for any redirects
        file = urlopen(Request(file_url, data=None, 
                               headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}))
        http_ffmpeg_file = sub('https', 'ffmpeg://https', file.geturl())
        if self.debug:
            LOG.debug('http_ffmpeg_file: ' + str(http_ffmpeg_file))
        self._run_cmd(u'loadfile', http_ffmpeg_file, append)

    def loadlist(self, file_, append=None):
        '''Load the given playlist file,stopping playback of the current file.
        If <append> is nonzero playback continues and the playlist file is
        appended to the current playlist instead.'''
        self._run_cmd(u'loadlist', file_, append)

    def loop(self, value, abs=None):
        '''Adjust/set how many times the movie should be looped.
        -1 means no loop and 0 forever.'''
        self._run_cmd(u'loop', value, abs)

    def menu(self, command):
        '''Execute an OSD menu command.
            * up     Move cursor up.
            * down   Move cursor down.
            * ok     Accept selection.
            * cancel Cancel selection.
            * hide   Hide the OSD menu.'''
        self._run_cmd(u'menu', command)

    def set_menu(self, menu_name):
        '''Display the menu named <menu_name>.'''
        self._run_cmd(u'set_menu', menu_name)

    def mute(self, value=None):
        '''Toggle sound output muting or set it to [value] when [value] >= 0
        (1 == on, 0 == off).'''
        self._run_cmd(u'mute', value)

    def osd(self, level=None):
        '''Toggle OSD mode or set it to [level] when [level] >= 0.'''
        self._run_cmd(u'osd', level)

    def osd_show_property_text(self, string, duration=None, level=None):
        '''Show an expanded property string on the OSD, see -playing-msg for a
        description of the available expansions.If [duration] is >= 0 the text
        is shown for [duration] ms. [level] sets the minimum OSD level needed
        for the message to be visible (default: 0 - always show).'''
        self._run_cmd(u'osd_show_property_text', string, duration, level)

    def osd_show_text(self, string, duration=None, level=None):
        '''Show <string> on the OSD.'''
        self._run_cmd(u'osd_show_text', string, duration, level)

    def panscan(self, value, abs):
        '''Increase or decrease the pan-and-scan range by <value>,
        1.0 is the maximum.
        Negative values decrease the pan-and-scan range.
        If <abs> is != 0, then the pan-and scan range is interpreted as an
        absolute range.'''
        self._run_cmd(u'panscan', value, abs)

    def pause(self):
        '''Pause/unpause the playback.'''
        self._run_cmd(u'pause')

    def frame_step(self):
        '''Play one frame, then pause again.'''
        self._run_cmd(u'frame_step')

    def pt_step(self, value, force=None):
        '''Go to the next/previous entry in the playtree.
        The sign of <value> tells the direction.  If no entry is available in
        the given direction it will do nothing unless [force] is non-zero.'''
        self._run_cmd(u'pt_step', value, force)

    def pt_up_step(self, value, force=None):
        '''Similar to pt_step but jumps to the next/previous
        entry in the parent list.
        Useful to break out of the inner loop in the playtree.'''
        self._run_cmd(u'pt_up_step', value, force)

    def quit(self):
        '''Sends a quit to the mplayer process, if the mplayer is still alive,
        process will terminated, if that doesn't work process will be killed.
        The panel will not be destroyed!
        Returns True, if the process got terminated successfully,
        otherwise False'''
        if self.process_alive:
            self._run_cmd(u'quit')
            if sys.version_info[:2] > (2, 5):
                self._process.terminate()
                if self.process_alive:
                    self._process.kill()
            self._process, self._stderr, self._stdin, self._stdout = [
                                                                         None] * 4
        return not self.process_alive

    def radio_set_channel(self, channel):
        '''Switch to <channel>. The 'channels'
        radio parameter needs to be set.'''
        self._run_cmd(u'radio_set_channel', channel)

    def radio_set_freq(self, freq):
        '''Set the radio tuner frequency.
            freq in Mhz'''
        self._run_cmd(u'radio_set_freq', freq)

    def radio_step_channel(self, value):
        '''Step forwards (1) or backwards (-1) in channel list.
        Works only when the 'channels' radio parameter was set.'''
        self._run_cmd(u'radio_step_channel', value)

    def radio_step_freq(self, value):
        '''Tune frequency by the <value> (positive - up, negative - down).'''
        self._run_cmd(u'radio_step_freq', value)

    def seek(self, value, type_=None):
        '''Seek to some place in the movie.
            0 is a relative seek of +/- <value> seconds (default).
            1 is a seek to <value> % in the movie.
            2 is a seek to an absolute position of <value> seconds.'''
        self._run_cmd(u'seek', value, type_)

    def seek_chapter(self, value, type_=None):
        '''Seek to the start of a chapter.
            0 is a relative seek of +/- <value> chapters (default).
            1 is a seek to chapter <value>.'''
        self._run_cmd(u'seek_chapter', value, type_)

    def switch_angle(self, value):
        '''Switch to the angle with the ID [value]. Cycle through the
        available angles if [value] is omitted or negative.'''
        self._run_cmd(u'switch_angle', value)

    def set_mouse_pos(self, x, y):
        '''Tells MPlayer the coordinates of the mouse in the window.
        This command doesn't move the mouse!'''
        self._run_cmd(u'set_mouse_pos', x, y)

    # set_property
    def set_property(self, property, value):
        '''Sets a property.
        All possible properties in PROPERTIES
        If property isn't a "set-property", raises AnsError'''
        if property in self.PROPERTIES:
            prop = self.PROPERTIES[property]
            min, max = prop['min'], prop['max']
            ptype = prop['type']
            if prop['set']:
                if ptype == 'flag':
                    value = int(bool(value))
                elif ptype == 'int':
                    value = int(float(value))
                else:
                    value = float(value)
                if not min <= value <= max:
                    raise AnsError('value must be between %.2f and %.2f' %
                                   (min, max))
                self._run_cmd(u'set_property', property, value)
            else:
                raise AnsError('PROPERTY_UNAVAILABLE')
        else:
            raise AnsError('PROPERTY_UNKNOWN')

    def speed_incr(self, value):
        '''Add <value> to the current playback speed.'''
        self._run_cmd(u'speed_incr', value)

    def speed_mult(self, value):
        '''Multiply the current speed by <value>.'''
        self._run_cmd(u'speed_mult', value)

    def speed_set(self, value):
        '''Set the speed to <value>.'''
        self._run_cmd(u'speed_set', value)

    # step_property
    def step_property(self, property, value=None, direction=None):
        '''Change a property by value, or increase by a default if value is
        not given or zero. The direction is reversed if direction is less
        than zero.
        All possible properties in PROPERTIES
        If property isn't a "step-property", raises AnsError'''
        if property in self.PROPERTIES:
            if self.PROPERTIES[property]['step']:
                self._run_cmd(u'step_property', property, value, direction)
            else:
                raise AnsError('PROPERTY_UNAVAILABLE')
        else:
            raise AnsError('PROPERTY_UNKNOWN')

    def stop(self):
        '''Stop playback.'''
        self._run_cmd(u'stop')

    def sub_alignment(self, value=None):
        '''Toggle/set subtitle alignment.
            0 top alignment
            1 center alignment
            2 bottom alignment'''
        self._run_cmd(u'sub_alignment', value)

    def sub_delay(self, value, abs=None):
        '''Adjust the subtitle delay by +/- <value> seconds
        or set it to <value> seconds when [abs] is nonzero.'''
        self._run_cmd(u'sub_delay', value, abs)

    def sub_load(self, subtitle_file):
        '''Loads subtitles from <subtitle_file>.'''
        self._run_cmd(u'sub_load', subtitle_file)

    def sub_log(self):
        '''Logs the current or last displayed subtitle together with filename
        and time information to ~/.mplayer/subtitle_log. Intended purpose
        is to allow convenient marking of bogus subtitles which need to be
        fixed while watching the movie.'''
        self._run_cmd(u'sub_log')

    def sub_pos(self, value, abs=None):
        '''Adjust/set subtitle position.'''
        self._run_cmd(u'sub_pos', value, abs)

    def sub_remove(self, value):
        '''If the [value] argument is present and non-negative,
        removes the subtitle file with index [value].
        If the argument is omitted or negative, removes all subtitle files.'''
        self._run_cmd(u'sub_remove', value)

    def sub_select(self, value):
        '''Display subtitle with index [value]. Turn subtitle display off if
        [value] is -1 or greater than the highest available subtitle index.
        Cycle through the available subtitles if [value] is omitted or less
        than -1. Supported subtitle sources are -sub options on the command
        line, VOBsubs, DVD subtitles, and Ogg and Matroska text streams.
        This command is mainly for cycling all subtitles, if you want to set
        a specific subtitle, use SubFile, SubVob, or SubDemux.'''
        self._run_cmd(u'sub_select', value)

    def sub_source(self, source):
        '''Display first subtitle from [source]. Here [source] is an integer:
        SUB_SOURCE_SUBS   (0) for file subs
        SUB_SOURCE_VOBSUB (1) for VOBsub files
        SUB_SOURCE_DEMUX  (2) for subtitle embedded in the
                                    media file or DVD subs.
        If [source] is -1, will turn off subtitle display.
        If [source] less than -1, will cycle between the first subtitle
        of each currently available sources.'''
        self._run_cmd(u'sub_source', source)

    def sub_file(self, value):
        '''Display subtitle specifid by [value] for file subs. The [value] is
        corresponding to ID_FILE_SUB_ID values reported by '-identify'.
        If [value] is -1, will turn off subtitle display.
        If [value] less than -1, will cycle all file subs.'''
        self._run_cmd(u'sub_file', value)

    def sub_vob(self, value):
        '''Display subtitle specifid by [value] for vobsubs. The [value] is
        corresponding to ID_VOBSUB_ID values reported by '-identify'.
        If [value] is -1, will turn off subtitle display.
        If [value] less than -1, will cycle all vobsubs.'''
        self._run_cmd(u'sub_vob', value)

    def sub_demux(self, value):
        '''Display subtitle specifid by [value] for subtitles from DVD
        or embedded in media file. The [value] is corresponding to
        ID_SUBTITLE_ID values reported by '-identify'. If [value] is -1, will
        turn off subtitle display. If [value] less than -1,
        will cycle all DVD subs or embedded subs.'''
        self._run_cmd(u'sub_demux', value)

    def sub_scale(self, value, abs=None):
        '''Adjust the subtitle size by +/- <value> or set it
        to <value> when [abs] is nonzero.'''
        self._run_cmd(u'sub_scale', value, abs)

    def vobsub_lang(self, *args):
        '''This is a stub linked to SubSelect for backwards compatibility.'''
        self.sub_scale(*args)

    def sub_step(self, value):
        '''Step forward in the subtitle list by <value> steps or
        backwards if <value> is negative.'''
        self._run_cmd(u'sub_step', value)

    def sub_visibility(self, value=None):
        '''Toggle/set subtitle visibility.'''
        self._run_cmd(u'sub_visibility', value)

    def forced_subs_only(self, value=None):
        '''Toggle/set forced subtitles only.'''
        self._run_cmd(u'forced_subs_only', value)

    def switch_audio(self, value=None):
        '''Switch to the audio track with the ID [value]. Cycle through the
        available tracks if [value] is omitted or negative.'''
        self._run_cmd(u'switch_audio', value)

    def switch_ratio(self, value):
        '''Change aspect ratio at runtime. [value] is the new aspect
        ratio expressed as a float (e.g. 1.77778 for 16/9).
        There might be problems with some video filters.'''
        self._run_cmd(u'switch_ratio', value)

    def switch_title(self, value=None):
        '''Switch to the DVD title with the ID [value]. Cycle through the
        available titles if [value] is omitted or negative.'''
        self._run_cmd(u'switch_title', value)

    def switch_vsync(self, value=None):
        '''Toggle vsync (1 == on, 0 == off). If [value] is not provided,
        vsync status is inverted.'''
        self._run_cmd(u'switch_vsync', value)

    def teletext_add_digit(self, value):
        '''Enter/leave teletext page number editing mode and append
        given digit to previously entered one.
        * 0..9 Append apropriate digit. (Enables editing mode if called from
        normal mode, and switches to normal mode when third digit is entered.)
        * Delete last digit from page number. (Backspace emulation, works only
        in page number editing mode.)'''
        self._run_cmd(u'teletext_add_digit', value)

    def teletext_go_link(self, value):
        '''Follow given link on current teletext page.
        value must be 1,2,3,4,5 or 6'''
        self._run_cmd(u'teletext_go_link', value)

    def tv_start_scan(self):
        '''Start automatic TV channel scanning.'''
        self._run_cmd(u'tv_start_scan')

    def tv_step_channel(self, channel):
        '''Select next/previous TV channel.'''
        self._run_cmd(u'tv_step_channel', channel)

    def tv_step_norm(self):
        '''Change TV norm.'''
        self._run_cmd(u'tv_step_norm')

    def tv_step_chanlist(self):
        '''Change channel list.'''
        self._run_cmd(u'tv_step_chanlist')

    def tv_set_channel(self, channel):
        '''Set the current TV channel.'''
        self._run_cmd(u'tv_set_channel', channel)

    def tv_last_channel(self):
        '''Set the current TV channel to the last one.'''
        self._run_cmd(u'tv_last_channel')

    def tv_set_freq(self, freq):
        '''Set the TV tuner frequency.
        freq offset in Mhz'''
        self._run_cmd(u'tv_set_freq', freq)

    def tv_step_freq(self, freq):
        '''Set the TV tuner frequency relative to current value.
        freq offset in Mhz'''
        self._run_cmd(u'tv_step_freq', freq)

    def tv_set_norm(self, norm):
        '''Set the TV tuner norm (PAL, SECAM, NTSC, ...).'''
        self._run_cmd(u'tv_set_norm', norm)

    def tv_set_brightness(self, value, abs=None):
        '''Set TV tuner brightness or adjust it if [abs] is set to 0.
        value from -100 to 100'''
        self._run_cmd(u'tv_set_brightness', value, abs)

    def tv_set_contrast(self, value, abs=None):
        '''Set TV tuner contrast or adjust it if [abs] is set to 0.
        value from -100 to 100'''
        self._run_cmd(u'tv_set_contrast', value, abs)

    def tv_set_hue(self, value, abs=None):
        '''Set TV tuner hue or adjust it if [abs] is set to 0.
        value from -100 to 100'''
        self._run_cmd(u'tv_set_hue', value, abs)

    def tv_set_saturation(self, value, abs=None):
        '''Set TV tuner saturation or adjust it if [abs] is set to 0.
        value from -100 to 100'''
        self._run_cmd(u'tv_set_saturation', value, abs)

    def use_master(self):
        '''Switch volume control between master and PCM.'''
        self._run_cmd(u'use_master')

    def vo_border(self, value=None):
        '''Toggle/set borderless display.'''
        self._run_cmd(u'vo_border', value)

    def vo_fullscreen(self, value=None):
        '''Toggle/set fullscreen mode'''
        self._run_cmd(u'vo_fullscreen', value)

    def vo_ontop(self, value):
        '''Toggle/set stay-on-top.'''
        self._run_cmd(u'vo_ontop', value)

    def vo_rootwin(self, value=None):
        '''Toggle/set playback on the root window.'''
        self._run_cmd(u'vo_rootwin', value)

    def destroy(self):
        self.quit()
        self.ee.remove_listener("mplayer_media_started",
                                self.on_media_started)
        self.ee.remove_listener("mplayer_media_finished",
                                self.on_media_finished)
        self.ee.remove_listener("mplayer_process_started",
                                self.on_process_started)
        self.ee.remove_listener("mplayer_process_stopped",
                                self.on_process_stopped)
        self.ee.remove_listener("mplayer_stderr", self.on_stderr)
        self.ee.remove_listener("mplayer_stdout", self.on_stdout)


def _get_type(val, *types):
    if not types:
        types = (int, float, str)
    for f in types:
        try:
            return f(val)
        except ValueError:
            pass
    return val


def _yes_no_bool(yon):
    yon = yon.lower()
    if yon in ('yes', 'no'):
        return yon == 'yes'
    raise ValueError


def _parse_stdout(line):
    line = line.strip()
    if '=' in line:
        s, val = line.split('=', 1)
        val = val.strip('\'')
        s = s.upper()
        if not s.startswith('ANS_'):
            return (None, None)
        else:
            ret = _get_type(val, int, float, _yes_no_bool, str)
        return s, ret
    return (None, None)
