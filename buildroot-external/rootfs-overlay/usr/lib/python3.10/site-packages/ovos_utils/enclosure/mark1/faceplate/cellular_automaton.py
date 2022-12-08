from ovos_utils.enclosure.mark1.faceplate import FacePlateAnimation
import copy
import random


# Game of Life Base
class GoL(FacePlateAnimation):

    def __init__(self, entropy=0, grid=None, bus=None):
        super().__init__(grid, bus)
        self.entropy = entropy
        if self.is_empty:
            self.randomize()

    def _live_neighbours(self, y, x):
        """Returns the number of live neighbours."""
        count = 0
        if y > 0:
            if self.grid[y - 1][x]:
                count = count + 1
            if x > 0:
                if self.grid[y - 1][x - 1]:
                    count = count + 1
            if self.width > (x + 1):
                if self.grid[y - 1][x + 1]:
                    count = count + 1

        if x > 0:
            if self.grid[y][x - 1]:
                count = count + 1
        if self.width > (x + 1):
            if self.grid[y][x + 1]:
                count = count + 1

        if self.height > (y + 1):
            if self.grid[y + 1][x]:
                count = count + 1
            if x > 0:
                if self.grid[y + 1][x - 1]:
                    count = count + 1
            if self.width > (x + 1):
                if self.grid[y + 1][x + 1]:
                    count = count + 1

        return count

    def animate(self):
        """Game of Life turn"""
        nt = copy.deepcopy(self.grid)
        for y in range(0, self.height):
            for x in range(0, self.width):
                neighbours = self._live_neighbours(y, x)
                if self.grid[y][x] == 0:
                    if neighbours == 3:
                        nt[y][x] = 1
                else:
                    if (neighbours < 2) or (neighbours > 3):
                        nt[y][x] = 0
        if nt == self.grid and self.entropy <= 0:
            self.stop()
        self.grid = nt
        self.randomize(self.entropy)
        if self.is_empty:
            self.stop()


# Langtons Ant base
class _Ant:
    def __init__(self, x, y, direction, height=8, width=32):
        self.x = x
        self.y = y
        assert direction[0] in ["r", "l", "u", "d"]
        self.direction = direction[0]
        self.grid_height = height
        self.grid_width = width
        self.dead = False

    def move_forward(self):
        if self.direction == "r":
            self.x += 1
            if self.x == self.grid_width:
                self.dead = True
        elif self.direction == "d":
            self.y += 1
            if self.y == self.grid_height:
                self.dead = True
        elif self.direction == "l":
            self.x -= 1
            if self.x == -1:
                self.dead = True
        elif self.direction == "u":
            self.y -= 1
            if self.y == -1:
                self.dead = True

    def turn_right(self):
        if self.direction == "r":
            self.direction = "d"
        elif self.direction == "d":
            self.direction = "l"
        elif self.direction == "l":
            self.direction = "u"
        elif self.direction == "u":
            self.direction = "r"

    def turn_left(self):
        if self.direction == "r":
            self.direction = "u"
        elif self.direction == "d":
            self.direction = "r"
        elif self.direction == "l":
            self.direction = "d"
        elif self.direction == "u":
            self.direction = "l"


class _InfiniteAnt(_Ant):
    def move_forward(self):
        if self.direction == "r":
            self.x += 1
            if self.x == self.grid_width:
                self.x = 0
        elif self.direction == "d":
            self.y += 1
            if self.y == self.grid_height:
                self.y = 0
        elif self.direction == "l":
            self.x -= 1
            if self.x == -1:
                self.x = self.grid_width - 1
        elif self.direction == "u":
            self.y -= 1
            if self.y == -1:
                self.y = self.grid_height - 1


class _ReverseAnt(_Ant):
    def turn_left(self):
        super().turn_right()

    def turn_right(self):
        super().turn_left()


class _ReverseInfiniteAnt(_InfiniteAnt):
    def turn_left(self):
        super().turn_right()

    def turn_right(self):
        super().turn_left()


class LangtonsAnt(FacePlateAnimation):
    def __init__(self, ants=1, continuous=True, gen_reverse=False,
                 grid=None, bus=None):
        super().__init__(grid=grid, bus=bus)
        self.ants = []
        # if continuous loops around the board
        #   height + 1 -> 0
        #   width + 1 -> 0
        # else ant is removed
        self.continuous = continuous
        if isinstance(ants, int):
            # spawn N ants
            assert 0 <= ants < 256
            for i in range(ants):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                direction = random.choice(["u", "d", "l", "r"])
                reverse = False
                if gen_reverse:
                    reverse = random.choice([True, False])
                ant = self.ant_factory(x, y, direction, reverse)
                self.ants.append(ant)
        elif isinstance(ants, list):
            # Ant objects
            self.ants = ants
            for ant in self.ants:
                assert isinstance(ant, _Ant)
        else:
            raise ValueError

    def ant_factory(self, x, y, direction, reverse=False):
        # reverse ants exit black squares to the opposite direction
        if self.continuous:
            # loops around the board instead of dying
            if reverse:
                return _ReverseInfiniteAnt(x, y, direction)
            return _InfiniteAnt(x, y, direction)
        if reverse:
            return _ReverseAnt(x, y, direction)
        return _Ant(x, y, direction)

    def move_ants(self):
        # copy grid, multiple ants might want to flip same square
        # end result is the same so this is not a problem as long as it does
        # not change during iteration
        old_grid = copy.deepcopy(self.grid)

        for idx, ant in enumerate(self.ants):
            if self.ants[idx].dead:
                continue
            if old_grid[ant.y][ant.x] == 1:
                # black
                self.ants[idx].turn_left()
            else:
                # white
                self.ants[idx].turn_right()
            # flip color
            self.grid[ant.y][ant.x] = not old_grid[ant.y][ant.x]
            # update ant position
            self.ants[idx].move_forward()

    def animate(self):
        self.move_ants()
        # Stop condition -> all ants moved out of the board
        dead_ants = [ant for ant in self.ants if ant.dead]
        if len(dead_ants) == len(self.ants):
            self.stop()


# Game of Life Animations
class SpaceInvader(GoL):
    # This basically half "pulsar"
    str_grid = """
XXXXXXXXXXXX  XXX  XXXXXXXXXXXXX
XXXXXXXXXX X X X X X XXXXXXXXXXX
XXXXXXXX   XX  X  XX   XXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXX  XXX  XXXXXXXXXXXXX
XXXXXXXXXXXX XXXXX XXXXXXXXXXXXX
XXXXXXXXXXXX XXXXX XXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
"""


# Langton's Ant animations

# Single Ant
class LangtonsLineDisplacer(LangtonsAnt):
    # see pattern here
    # https://youtu.be/w6XQQhCgq5c?t=84

    def __init__(self, x=None, y=None, continuous=True, bus=None):
        super().__init__(0, continuous, bus=bus)
        x = x if x is not None else random.randint(0, self.width - 1)
        y = y if y is not None else random.randint(0, self.height - 1)
        ant = self.ant_factory(x, y - 1, "u")
        self.ants.append(ant)
        # create initial line
        for i in range(0, self.width):
            self.grid[y][i] = 1


# 2 Ants
class LangtonsAntsOscillator(LangtonsAnt):
    # see pattern here
    # https://youtu.be/w6XQQhCgq5c?t=103

    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x1 = x2 = x if x is not None else self.width // 2
        y1 = y if y is not None else self.height // 2
        y2 = y1 - 1
        dir1 = "d"
        dir2 = "u"
        ant1 = self.ant_factory(x1, y1, dir1)
        ant2 = self.ant_factory(x2, y2, dir2)
        self.ants += [ant1, ant2]


class LangtonsAntsOscillator2(LangtonsAnt):
    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x1 = x2 = x if x is not None else self.width // 2
        y1 = y if y is not None else self.height // 2
        y2 = y1 - 1
        dir1 = dir2 = "u"
        ant1 = self.ant_factory(x1, y1, dir1)
        ant2 = self.ant_factory(x2, y2, dir2)
        self.ants += [ant1, ant2]


class LangtonsAntsOscillator3(LangtonsAnt):
    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x1 = x2 = x if x is not None else self.width // 2
        y1 = y if y is not None else self.height // 2
        y2 = y1 - 1
        dir1 = "l"
        dir2 = "r"
        ant1 = self.ant_factory(x1, y1, dir1)
        ant2 = self.ant_factory(x2, y2, dir2)
        self.ants += [ant1, ant2]


class LangtonsAntsOscillator4(LangtonsAnt):
    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x1 = x2 = x if x is not None else self.width // 2
        y1 = y if y is not None else self.height // 2
        y2 = y1 - 1
        dir1 = dir2 = "l"
        ant1 = self.ant_factory(x1, y1, dir1)
        ant2 = self.ant_factory(x2, y2, dir2)
        self.ants += [ant1, ant2]


class LangtonsAntsOscillator5(LangtonsAnt):
    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x1 = x2 = x if x is not None else self.width // 2
        y1 = y if y is not None else self.height // 2
        y2 = y1 - 1
        dir1 = "u"
        dir2 = "d"
        ant1 = self.ant_factory(x1, y1, dir1)
        ant2 = self.ant_factory(x2, y2, dir2)
        self.ants += [ant1, ant2]


class LangtonsAntTrail(LangtonsAnt):
    # see pattern here
    # https://youtu.be/w6XQQhCgq5c?t=159

    def __init__(self, x=None, y=None, bus=None):
        super().__init__(0, bus=bus)
        x = x if x is not None else random.randint(0, self.width - 1)
        y = y if y is not None else random.randint(0, self.height - 1)
        dir1 = "u"
        dir2 = "d"
        ant1 = self.ant_factory(x, y - 1, dir1)
        ant2 = self.ant_factory(x, y, dir2, reverse=True)
        self.ants += [ant1, ant2]


class LangtonsAntDotTransporter(LangtonsAnt):
    # https://youtu.be/w6XQQhCgq5c?t=171

    def __init__(self, x=None, y=None,  bus=None):
        super().__init__(0, bus=bus)
        x = x if x is not None else random.randint(0, self.width - 1)
        y = y if y is not None else random.randint(0, self.height - 1)
        dir1 = dir2 = "u"
        ant1 = self.ant_factory(x, y, dir1)
        ant2 = self.ant_factory(x + 1, y, dir2, reverse=True)
        self.ants += [ant1, ant2]
        # initial grid
        if y + 1 == self.height:
            self.grid[0][x + 1] = 1 # bellow anti-ant
        else:
            self.grid[y + 1][x + 1] = 1  # bellow anti-ant
        self.grid[y - 1][x] = 1  # above ant


# 1D / elementar automata

class ElementarAutomata(FacePlateAnimation):
    def __init__(self, direction="u", idx=0, seed=None, grid=None, bus=None):
        super().__init__(grid, bus)
        assert direction[0] in ["u", "d", "l", "r"]
        self.direction = direction[0]
        self.row = idx
        self.initial_state(seed)

    def initial_state(self, seed=None):
        if seed is not None:
            line = seed
        else:
            line = [0 for i in range(self.width)]
        self.grid[self.row] = line

    def rule(self):
        # process the line
        raise NotImplementedError

    def animate(self):
        old = copy.deepcopy(self.grid)
        new_line = self.rule()
        if self.direction == "u":
            self.move_up()
        elif self.direction == "d":
            self.move_down()
        elif self.direction == "l":
            self.move_left()
        elif self.direction == "r":
            self.move_right()
        self.grid[self.row] = new_line
        if old == self.grid:
            self.stop()


class SierpinskiTriangle(ElementarAutomata):
    def __init__(self, direction="u", seed=None, bus=None):
        assert direction[0] in ["u", "d"]
        if direction[0] == "u":
            idx = -1
        else:
            idx = 0
        super().__init__(direction, idx, seed=seed, bus=bus)

    def initial_state(self, seed=None):
        if seed is not None:
            line = seed
        else:
            line = [0 for i in range(self.width)]
            idx = self.width // 2
            line[idx] = 1
        self.grid[self.row] = line

    def rule(self):
        new_line = copy.deepcopy(self.grid[self.row])
        # handle middle
        for i in range(1, self.width - 1):
            left = self.grid[self.row][i - 1]
            right = self.grid[self.row][i + 1]
            if left and right:
                new_line[i] = 0
            elif left or right:
                new_line[i] = 1
            else:
                new_line[i] = 0

        # handle edges
        #if self.grid[0][1] == 1:
        #    new_line[0] = 1
        #else:
        #    new_line[0] = 0
        #if self.grid[0][-2] == 1:
        #    new_line[-1] = 1
        #else:
        #    new_line[-1] = 0
        return new_line


class Rule110(ElementarAutomata):
    def __init__(self, direction="u", seed=None, bus=None):
        assert direction[0] in ["u", "d"]
        if direction[0] == "u":
            idx = -1
        else:
            idx = 0
        super().__init__(direction, idx, seed=seed, bus=bus)

    def initial_state(self, seed=None):
        if seed is not None:
            line = seed
        else:
            line = [0 for i in range(self.width)]
            idx = self.width - 1
            line[idx] = 1
        self.grid[self.row] = line

    def rule(self):
        new_line = copy.deepcopy(self.grid[self.row])
        # handle middle
        for i in range(1, self.width - 1):
            left = self.grid[self.row][i - 1]
            mid = self.grid[self.row][i]
            right = self.grid[self.row][i + 1]
            if str(left) + str(mid) + str(right) in \
                    ["110", "101", "011", "010", "001"]:
                new_line[i] = 1
            else:
                new_line[i] = 0

        # handle edges
        if self.grid[0][1] == 1:
            new_line[0] = 1
        else:
            new_line[0] = 0
        if self.grid[0][-2] == 1:
            new_line[-1] = 1
        else:
            new_line[-1] = 0
        return new_line


if __name__ == "__main__":
    from time import sleep
    from ovos_utils.messagebus import get_mycroft_bus
    from time import sleep

    bus = get_mycroft_bus("192.168.1.70")

    a = Rule110(bus=bus)
    a.print()

    for grid in a:
        grid.print()
        grid.display(invert=False)
        sleep(0.5)