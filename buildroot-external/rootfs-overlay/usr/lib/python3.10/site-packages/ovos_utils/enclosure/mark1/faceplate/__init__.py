from ovos_utils.enclosure.mark1 import Mark1EnclosureAPI
from ovos_utils import create_loop
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
import random
from time import sleep
import collections
import copy


class FaceplateGrid(collections.MutableSequence):
    encoded = None
    str_grid = None
    pad_char = "."

    def __init__(self, grid=None, bus=None):
        self.bus = bus or get_mycroft_bus()
        self._api = Mark1EnclosureAPI(self.bus)
        self.grid = []
        for x in range(8):
            self.grid.append([])
            for y in range(32):
                self.grid[x].append(0)
        if self.encoded:
            self.grid = self.decode(self.encoded).grid
        elif self.str_grid is not None:
            self.grid = FaceplateGrid(bus=self.bus)\
                .from_string(self.str_grid).grid
        elif grid is not None:
            self.grid = grid

    @property
    def height(self):
        return len(self.grid)

    @property
    def width(self):
        return max([len(r) for r in self.grid])

    def display(self, invert=True, clear=True, x_offset=0, y_offset=0):
        self._api.mouth_display(self.encode(invert),
                                x_offset, y_offset, clear)

    def print(self, draw_padding=True, invert=False):
        print(self.to_string(draw_padding=draw_padding, invert=invert))

    def encode(self, invert=False):
        # to understand how this function works you need to understand how the
        # Mark I arduino proprietary encoding works to display to the faceplate

        # https://mycroft-ai.gitbook.io/docs/skill-development/displaying-information/mark-1-display

        # Each char value str_gridesents a width number starting with B=1
        # then increment 1 for the next. ie C=2
        width_codes = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                       'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a']

        height_codes = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        encode = width_codes[self.width - 1]
        encode += height_codes[self.height - 1]

        # Turn the image pixels into binary values 1's and 0's
        # the Mark I face plate encoding uses binary values to
        # binary_values returns a list of 1's and 0s'. ie ['1', '1', '0', ...]
        binary_values = []
        for i in range(self.width):  # pixels
            for j in range(self.height):  # lines
                pixels = self.grid[j]

                if pixels[i] is None:  # padding
                    pixels[i] = 0

                if pixels[i] != 0:
                    if invert is False:
                        binary_values.append('1')
                    else:
                        binary_values.append('0')
                else:
                    if invert is False:
                        binary_values.append('0')
                    else:
                        binary_values.append('1')
        # these values are used to determine how binary values
        # needs to be grouped together
        number_of_bottom_pixel = 0

        if self.height > 4:
            number_of_top_pixel = 4
            number_of_bottom_pixel = self.height - 4
        else:
            number_of_top_pixel = self.height

        # this loop will group together the individual binary values
        # ie. binary_list = ['1111', '001', '0101', '100']
        binary_list = []
        binary_code = ''
        increment = 0
        alternate = False
        for val in binary_values:
            binary_code += val
            increment += 1
            if increment == number_of_top_pixel and alternate is False:
                # binary code is reversed for encoding
                binary_list.append(binary_code[::-1])
                increment = 0
                binary_code = ''
                alternate = True
            elif increment == number_of_bottom_pixel and alternate is True:
                binary_list.append(binary_code[::-1])
                increment = 0
                binary_code = ''
                alternate = False
        # Code to let the Mark I arduino know where to place the
        # pixels on the faceplate
        pixel_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                       'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        for binary_values in binary_list:
            number = int(binary_values, 2)
            pixel_code = pixel_codes[number]
            encode += pixel_code
        return encode

    def decode(self, encoded, invert=False, pad=True):
        codes = list(encoded)

        # Each char value str_gridesents a width number starting with B=1
        # then increment 1 for the next. ie C=2
        width_codes = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                       'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a']

        height_codes = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        height = height_codes.index(codes[1]) + 1
        width = width_codes.index(codes[0]) + 1

        # Code to let the Mark I arduino know where to place the
        # pixels on the faceplate
        pixel_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                       'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        codes.reverse()
        binary_list = []
        for pixel_code in codes[:-2]:
            number = pixel_codes.index(pixel_code.upper())
            bin_str = str(bin(number))[2:]
            while not len(bin_str) == 4:
                bin_str = "0" + bin_str
            binary_list += [bin_str]

        binary_list.reverse()

        for idx, binary_code in enumerate(binary_list):
            # binary code is reversed for encoding
            binary_list[idx] = binary_code[::-1]

        binary_code = "".join(binary_list)

        # Turn the image pixels into binary values 1's and 0's
        # the Mark I face plate encoding uses binary values to
        # binary_values returns a list of 1's and 0s'. ie ['1', '1', '0', ...]
        grid = []
        # binary_code is a sequence of column by column
        cols = [list(binary_code)[x:x + height] for x in
                range(0, len(list(binary_code)), height)]

        for x in range(height):
            row = []
            for y in range(width):
                bit = int(cols[y][x])
                if invert:
                    if bit:
                        bit = 0
                    else:
                        bit = 1
                row.append(bit)
            grid.append(row)

        #  handle padding
        if pad:
            if width < self.width:
                n = int((self.width - width) / 2)
                if invert:
                    padding = [1] * n
                else:
                    padding = [0] * n
                for idx, row in enumerate(grid):
                    grid[idx] = padding + row + padding
            if height < self.height:
                pass # TODO vertical padding
        self.grid = grid
        return self

    def from_string(self, str_grid):
        rows = [r for r in str_grid.split("\n") if len(r)]
        grid = []
        for r in rows:
            row = []
            for char in list(r):
                if char == " ":
                    row.append(1)
                elif char == FaceplateGrid.pad_char:
                    row.append(None)
                else:
                    row.append(0)
            while len(row) < self.width:
                row.append(None)
            grid.append(row)
        self.grid = grid
        return self

    def to_string(self, draw_padding=False, invert=False):
        str_grid = ""
        for row in self.grid:
            line = ""
            for col in row:
                if col is None and draw_padding:
                    line += self.pad_char
                elif col == 1:
                    if invert:
                        line += "X"
                    else:
                        line += " "
                elif col == 0:
                    if invert:
                        line += " "
                    else:
                        line += "X"
            str_grid += line + "\n"
        return str_grid

    def invert(self):
        for x in range(self.height):
            for y in range(self.width):
                if self.grid[x][y] == 0:
                    self.grid[x][y] = 1
                elif self.grid[x][y] == 1:
                    self.grid[x][y] = 0
        return self

    def clear(self):
        for x in range(self.height):
            for y in range(self.width):
                self.grid[x][y] = 0
        return self

    @property
    def is_empty(self):
        for x in range(self.height):
            for y in range(self.width):
                if self.grid[x][y] == 1:
                    return False
        return True

    def randomize(self, n=200):
        for i in range(n):
            x = random.randint(0, self.height-1)
            y = random.randint(0, self.width-1)
            self.grid[x][y] = int(random.randint(0, 1))
        return self

    def __len__(self):
        # number of pixels
        return self.width * self.height

    def __delitem__(self, index):
        self.grid.__delitem__(index)

    def insert(self, index, value):
        self.grid.insert(index - 1, value)

    def __setitem__(self, index, value):
        self.grid.__setitem__(index, value)

    def __getitem__(self, index):
        return self.grid.__getitem__(index)


class FacePlateAnimation(FaceplateGrid):

    def __init__(self, grid=None, bus=None):
        super().__init__(grid, bus)
        self.finished = False

    def animate(self):
        pass

    def __iter__(self):
        while not self.finished:
            self.animate()
            yield self

    def start(self):
        self.finished = False

    def stop(self):
        self.finished = True

    def run(self, delay=0.5, callback=None, daemonic=False):
        self.start()

        if delay < 0.4:
            # writer bugs out if sending messages too rapidly
            delay = 0.4

        def step(callback=callback):
            try:
                if not self.finished:
                    self.animate()
                    if callback:
                        callback(self)
            except Exception as e:
                LOG.error(e)

        if daemonic:
            create_loop(step, delay)
        else:
            while not self.finished:
                step()
                sleep(delay)
        self.stop()

    def scroll_down(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                self.grid[y][x] = old[y - 1][x]

    def scroll_up(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                if y == self.height - 1:
                    self.grid[y][x] = old[0][x]
                else:
                    self.grid[y][x] = old[y + 1][x]

    def scroll_right(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                self.grid[y][x] = old[y][x - 1]

    def scroll_left(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                if x == self.width -1:
                    self.grid[y][x] = old[y][0]
                else:
                    self.grid[y][x] = old[y][x + 1]

    def move_down(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                if y - 1 < 0:
                    self.grid[y][x] = 0
                else:
                    self.grid[y][x] = old[y - 1][x]

    def move_up(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                if y == self.height - 1:
                    self.grid[y][x] = 0
                else:
                    self.grid[y][x] = old[y + 1][x]

    def move_right(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                self.grid[y][x] = old[y][x - 1]

    def move_left(self):
        old = copy.deepcopy(self.grid)
        for x in range(self.width):
            for y in range(self.height):
                if x == self.width - 1:
                    self.grid[y][x] = 0
                else:
                    self.grid[y][x] = old[y][x + 1]


class BlackScreen(FaceplateGrid):
    # Basically a util class to handle
    # inverting on __init__
    str_grid = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invert()
