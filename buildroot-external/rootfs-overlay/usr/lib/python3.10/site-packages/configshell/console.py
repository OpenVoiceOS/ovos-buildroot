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

from fcntl import ioctl
import re
import six
import struct
import sys
from termios import TIOCGWINSZ, TCSADRAIN, tcsetattr, tcgetattr
import textwrap
import tty

from .prefs import Prefs

class Console(object):
    '''
    Implements various utility methods providing a console UI support toolkit,
    most notably an epytext-to-console text renderer using ANSI escape
    sequences. It uses the Borg pattern to share state between instances.
    '''
    _max_width = 132
    _escape = '\033['
    _ansi_format = _escape + '%dm%s'
    _ansi_reset = _escape + '0m'
    _re_ansi_seq = re.compile('(\033\[..?m)')

    _ansi_styles = {'bold':      1,
                    'underline': 4,
                    'blink':     5,
                    'reverse':   7,
                    'concealed': 8}

    colors = ['black', 'red', 'green', 'yellow',
              'blue', 'magenta', 'cyan', 'white']

    _ansi_fgcolors = dict(zip(colors, range(30, 38)))
    _ansi_bgcolors = dict(zip(colors, range(40, 48)))

    __borg_state = {}

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        '''
        Initializes a Console instance.
        @param stdin: The console standard input.
        @type stdin: file object
        @param stdout: The console standard output.
        @type stdout: file object
        '''
        self.__dict__ = self.__borg_state
        self._stdout = stdout
        self._stdin = stdin
        self._stderr = stderr
        self.prefs = Prefs()

    # Public methods

    def escape(self, sequence, reply_terminator=None):
        '''
        Sends an escape sequence to the console, and reads the reply terminated
        by reply_terminator. If reply_terminator is not specified, the reply
        will not be read.
        @type sequence: str
        @param reply_terminator: The expected end-of-reply marker.
        @type reply_terminator: str
        '''
        attributes = tcgetattr(self._stdin)
        tty.setraw(self._stdin)
        try:
            self.raw_write(self._escape + sequence)
            if reply_terminator is not None:
                reply = ''
                while reply[-len(reply_terminator):] != reply_terminator:
                    reply += self._stdin.read(1)
        finally:
            tcsetattr(self._stdin, TCSADRAIN, attributes)
        if reply_terminator is not None:
            reply = reply[:-len(reply_terminator)]
            reply = reply.replace(self._escape, '').split(';')
            return reply

    def get_width(self):
        '''
        Returns the console width, or maximum width if we are not a terminal
        device.
        '''
        try:
            winsize = struct.pack("HHHH", 0, 0, 0, 0)
            winsize = ioctl(self._stdout.fileno(), TIOCGWINSZ, winsize)
            width = struct.unpack("HHHH", winsize)[1]
        except IOError:
            width = self._max_width
        else:
            if width > self._max_width:
                width = self._max_width

        return width

    def get_cursor_xy(self):
        '''
        Get the current text cursor x, y coordinates.
        '''
        coords = [int(coord) for coord in self.escape("6n", "R")]
        coords.reverse()
        return coords

    def set_cursor_xy(self, xpos, ypos):
        '''
        Set the cursor x, y coordinates.
        @param xpos: The x coordinate of the cursor.
        @type xpos: int
        @param ypos: The y coordinate of the cursor.
        @type ypos: int
        '''
        self.escape("%d;%dH" % (ypos, xpos))

    def raw_write(self, text, output=sys.stdout):
        '''
        Raw console printing function.
        @param text: The text to print.
        @type text: str
        '''
        output.write(text)
        output.flush()

    def display(self, text, no_lf=False, error=False):
        '''
        Display a text with a default style.
        @param text: Text to display
        @type text: str
        @param no_lf: Do not display a line feed.
        @type no_lf: bool
        '''
        text = self.render_text(text)

        if error:
            output = self._stderr
        else:
            output = self._stdout

        self.raw_write(text, output=output)
        if not no_lf:
            self.raw_write('\n', output=output)

    def epy_write(self, text):
        '''
        Renders and print and epytext-formatted text on the console.
        '''
        text = self.dedent(text)
        # We need to remove the last line feed, but there might be
        # escape characters after it...
        clean_text = ''
        for index in range(1, len(text)):
            if text[-index] == '\n':
                clean_text = text[:-index]
                if index != 1:
                    clean_text += text[-index+1:]
                break
        else:
            clean_text = text
        self.raw_write(clean_text, output=self._stdout)

    def indent(self, text, margin=2):
        '''
        Indents text by margin space.
        @param text: The text to be indented.
        @type text: str
        '''
        output = ''
        for line in text.split('\n'):
            output += margin * ' ' + line + '\n'
        return output

    def dedent(self, text):
        '''
        A convenience function to easily write multiline text blocks that
        will be later assembled in to a unique epytext string.
        It removes heading newline chars and common indentation.
        '''
        for i in range(len(text)):
            if text[i] != '\n':
                break
        text = text[i:]
        text = textwrap.dedent(text)
        text = '\n' * i + text

        return text

    def render_text(self, text, fgcolor=None, bgcolor=None, styles=None,
                    open_end=False, todefault=False):
        '''
        Renders some text with ANSI console colors and attributes.
        @param fgcolor: ANSI color to use for text:
            black, red, green, yellow, blue, magenta. cyan. white
        @type fgcolor: str
        @param bgcolor: ANSI color to use for background:
            black, red, green, yellow, blue, magenta. cyan. white
        @type bgcolor: str
        @param styles: List of ANSI styles to use:
            bold, underline, blink, reverse, concealed
        @type styles: list of str
        @param open_end: Do not reset text style at the end ot the output.
        @type open_end: bool
        @param todefault: Instead of resetting style at the end of the
        output, reset to default color. Only if not open_end.
        @type todefault: bool
        '''
        if self.prefs['color_mode'] and self._stdout.isatty():
            if fgcolor is None:
                if self.prefs['color_default']:
                    fgcolor = self.prefs['color_default']
            if fgcolor is not None:
                text = self._ansi_format % (self._ansi_fgcolors[fgcolor], text)
            if bgcolor is not None:
                text = self._ansi_format % (self._ansi_bgcolors[bgcolor], text)
            if styles is not None:
                for style in styles:
                    text = self._ansi_format % (self._ansi_styles[style], text)
            if not open_end:
                text += self._ansi_reset
                if todefault and fgcolor is not None:
                    if self.prefs['color_default']:
                        text += self._ansi_format \
                                % (self._ansi_fgcolors[
                                    self.prefs['color_default']], '')
        return text

    def wordwrap(self, text, indent=0, startindex=0, splitchars=''):
        '''
        Word-wrap the given string.  I.e., add newlines to the string such
        that any lines that are longer than terminal width or max_width
        are broken into shorter lines (at the first whitespace sequence that
        occurs before the limit. If the given string contains newlines, they
        will not be removed.  Any lines that begin with whitespace will not
        be wordwrapped.

        This version takes into account ANSI escape characters:
            - stop escape sequence styling at the end of a split line
            - start it again on the next line if needed after the indent
            - do not account for the length of the escape sequences when
              wrapping

        @param indent: If specified, then indent each line by this number
            of spaces.
        @type indent: int
        @param startindex: If specified, then assume that the first line
            is already preceded by startindex characters.
        @type startindex: int
        @param splitchars: A list of non-whitespace characters which can
            be used to split a line.  (E.g., use '/\\' to allow path names
            to be split over multiple lines.)
        @rtype: str
        '''
        right = self.get_width()
        if splitchars:
            chunks = re.split(r'( +|\n|[^ \n%s]*[%s])' %
                              (re.escape(splitchars), re.escape(splitchars)),
                              text.expandtabs())
        else:
            chunks = re.split(r'( +|\n)', text.expandtabs())
        result = [' '*(indent-startindex)]
        charindex = max(indent, startindex)
        current_style = ''
        for chunknum, chunk in enumerate(chunks):
            chunk_groups = re.split(self._re_ansi_seq, chunk)
            chunk_text = ''
            next_style = current_style

            for group in chunk_groups:
                if re.match(self._re_ansi_seq, group) is None:
                    chunk_text += group
                else:
                    next_style += group

            chunk_len = len(chunk_text)
            if (charindex + chunk_len > right and charindex > 0) \
               or chunk == '\n':
                result[-1] = result[-1].rstrip()
                result.append(self.render_text(
                    '\n' + ' '*indent + current_style, open_end=True))
                charindex = indent
                if chunk[:1] not in ('\n', ' '):
                    result.append(chunk)
                    charindex += chunk_len
            else:
                result.append(chunk)
                charindex += chunk_len

            current_style = next_style.split(self._ansi_reset)[-1]

        return ''.join(result).rstrip()+'\n'
