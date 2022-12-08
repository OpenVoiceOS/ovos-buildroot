from ovos_utils.enclosure.mark1.faceplate import FacePlateAnimation, BlackScreen
import copy
import random


# Base animations
# These are mostly meant to be subclassed (empty animations)
class HorizontalScroll(FacePlateAnimation):
    def __init__(self, direction="right", grid=None, bus=None):
        super().__init__(grid, bus)
        assert direction.startswith("r") or direction.startswith("l")
        self.direction = direction[0]

    def animate(self):
        if self.direction == "r":
            self.scroll_right()
        else:
            self.scroll_left()
        if self.is_empty:
            self.stop()


class VerticalScroll(FacePlateAnimation):
    def __init__(self, direction="up",
                 grid=None, bus=None):
        super().__init__(grid, bus)
        assert direction.startswith("u") or direction.startswith("d")
        self.direction = direction[0]

    def animate(self):
        if self.direction == "u":
            self.scroll_up()
        else:
            self.scroll_down()
        if self.is_empty:
            self.stop()


class LeftRight(FacePlateAnimation):
    def __init__(self, direction="right", start="left", grid=None, bus=None):
        super().__init__(grid, bus)
        assert direction.startswith("r") or direction.startswith("l")
        self.direction = direction[0]

        # start at right/left side/center
        inverted = not isinstance(self, BlackScreen)
        if start[0] == "l":
            # left side
            for y in range(self.height):
                for x in range(self.width):
                    if not inverted and self.grid[y][x] == 1:
                        pass
                    elif inverted and self.grid[y][x] == 0:
                        pass
        elif start[0] == "r":
            pass # right side
        else:
            pass # center
        print(self.grid[1])

    def animate(self):
        left_collision = False
        right_collision = False
        inverted = not isinstance(self, BlackScreen)
        for y in range(self.height):
            if inverted:
                if self.grid[y][self.width - 1] == 0:
                    right_collision = True
                if self.grid[y][0] == 0:
                    left_collision = True
            else:
                if self.grid[y][self.width - 1] == 1:
                    right_collision = True
                if self.grid[y][0] == 1:
                    left_collision = True
        if left_collision and right_collision:
            return  # No space left to animate
        elif right_collision:
            self.direction = "l"
        elif left_collision:
            self.direction = "r"
        if self.direction == "r":
            self.scroll_right()
        else:
            self.scroll_left()
        if self.is_empty:
            self.stop()


class UpDown(FacePlateAnimation):
    def __init__(self, direction="up", grid=None, bus=None):
        super().__init__(grid, bus)
        assert direction.startswith("u") or direction.startswith("d")
        self.direction = direction[0]

    def animate(self):
        top_collision = False
        bottom_collision = False
        for x in range(self.width):
            if self.grid[0][x] == 1:
                top_collision = True
            if self.grid[self.height - 1][x] == 1:
                bottom_collision = True

        if top_collision and bottom_collision:
            return  # No space left to animate
        elif top_collision:
            self.direction = "d"
        elif bottom_collision:
            self.direction = "u"
        if self.direction == "u":
            self.scroll_up()
        else:
            self.scroll_down()
        if self.is_empty:
            self.stop()


class CollisionBox(FacePlateAnimation):
    def __init__(self,
                 horizontal_direction=None,
                 vertical_direction=None,
                 grid=None, bus=None):
        super().__init__(grid, bus)
        assert horizontal_direction is None or \
               horizontal_direction.startswith("r") or \
               horizontal_direction.startswith("l")
        assert vertical_direction is None or \
               vertical_direction.startswith("u") or \
               vertical_direction.startswith("d")
        self.vertical_direction = vertical_direction[0] if \
            vertical_direction else None
        self.horizontal_direction = horizontal_direction[0] if \
            horizontal_direction else None

    def animate(self):
        left_collision = False
        right_collision = False
        top_collision = False
        bottom_collision = False
        for y in range(self.height):
            if self.grid[y][self.width - 1] == 1:
                right_collision = True
            if self.grid[y][0] == 1:
                left_collision = True
        for x in range(self.width):
            if self.grid[0][x] == 1:
                top_collision = True
            if self.grid[self.height - 1][x] == 1:
                bottom_collision = True

        if top_collision and bottom_collision:
            self.vertical_direction = None
        elif top_collision:
            self.vertical_direction = "d"
        elif bottom_collision:
            self.vertical_direction = "u"

        if left_collision and right_collision:
            self.horizontal_direction = None
        elif right_collision:
            self.horizontal_direction = "l"
        elif left_collision:
            self.horizontal_direction = "r"

        if self.vertical_direction is None:
            pass
        elif self.vertical_direction == "u":
            self.scroll_up()
        elif self.vertical_direction == "d":
            self.scroll_down()

        if self.horizontal_direction is None:
            pass
        elif self.horizontal_direction == "r":
            self.scroll_right()
        elif self.horizontal_direction == "l":
            self.scroll_left()

        if self.is_empty:
            self.stop()


# Ready to use animations
class SquareWave(HorizontalScroll):
    def __init__(self, direction="r", frequency=3,
                 amplitude=4, grid=None, bus=None):
        super().__init__(direction, grid, bus)
        # frequency must be > 1
        # frequency is in number of pixels
        assert 0 < frequency
        # amplitude must be 2, 4 or 6. else it renders badly
        # amplitude is in number of pixels
        assert 0 < amplitude < self.height
        assert divmod(amplitude, 2)[1] == 0

        self.freq = frequency
        self.amplitude = self.height - amplitude

        self._initial_grid()
        self.invert()

    def _initial_grid(self):
        # draws the initial state
        count = 0
        top = True
        a = self.amplitude // 2 - 1
        for x in range(self.width):
            if top:
                self.grid[a + 1][x] = 1
            else:
                self.grid[-a - 1][x] = 1

            for y in range(self.height):
                if count == 0:
                    self.grid[y][x] = 1
                if y <= a:
                    self.grid[y][x] = 0
                elif y >= self.height - a:
                    self.grid[y][x] = 0
            count += 1
            if count == self.freq + 1:
                count = 0
                top = not top


class StrayDot(CollisionBox):
    def __init__(self,
                 start_x=None,
                 start_y=None,
                 horizontal_direction=None,
                 vertical_direction=None,
                 grid=None, bus=None):
        horizontal_direction = horizontal_direction or \
                               random.choice(["l", "r"])
        vertical_direction = vertical_direction or \
                             random.choice(["u", "d"])
        super().__init__(horizontal_direction, vertical_direction,
                         grid, bus)
        start_x = start_x or random.randint(0, self.width - 1)
        start_y = start_y or random.randint(0, self.height - 1)
        self.grid[start_y][start_x] = 1


class ParticleBox(FacePlateAnimation):
    def __init__(self, n_particles=5, bus=None):
        super().__init__(bus=bus)
        assert 0 < n_particles < 11
        self.n_particles = n_particles
        self.particles = []

        class Dot:
            def __init__(self, idx, x, y, vx, vy):
                self.x = x
                self.y = y
                self.vx = vx
                self.vy = vy
                self.idx = idx

        for i in range(n_particles):
            vx = random.choice(["l", "r"])
            vy = random.choice(["u", "d"])
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            while self.grid[y][x] == 1:
                # 2 particles can't occupy same space
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
            self.grid[y][x] = 1
            self.particles.append(Dot(i, x, y, vx, vy))

    def render_particles(self):
        self.clear()
        for p in self.particles:
            self.grid[p.y][p.x] = 1

    def get_particle(self, x, y):
        for p in self.particles:
            if p.x == x and p.y == y:
                return p

    def process_collisions(self):
        # new particles after this turn
        new_particles = copy.deepcopy(self.particles)

        # NOTE this is not a physics simulation!
        # while it is behaving like an elastic collision
        # if there is a 3+ particle collision results will be incorrect
        # as long as only 2 particles collide it looks accurate
        # max number of particles limited to 10 to minimize chance of this
        # happening
        for p in self.particles:
            idx = p.idx

            # horizontal movement
            if p.vx is None:
                # not moving horizontally
                if p.x != 0:
                    # check for collisions from left p2 -> p1
                    p2 = self.get_particle(p.x - 1, p.y)
                    if p2 and p2.vx == "r":
                        # collision p2 -> p1
                        if p.x == self.width - 1:
                            new_particles[idx].vx = None
                        else:
                            new_particles[idx].vx = "r"
                            new_particles[idx].x += 1
                if p.x != self.width - 1:
                    # check for collisions from right p1 <- p2
                    p2 = self.get_particle(p.x + 1, p.y)
                    if p2 and p2.vx == "l":
                        # collision p1 <- p2
                        if p.x == 0:
                            new_particles[idx].vx = None
                        else:
                            new_particles[idx].vx = "l"
                            new_particles[idx].x -= 1
            # moving right
            elif p.vx == "r":
                p2 = self.get_particle(p.x + 1, p.y)
                if p.x == self.width - 1:
                    # border collision p1 -> |
                    new_particles[idx].vx = "l"
                    new_particles[idx].x -= 1
                elif p2:
                    # particle collision p1 -> p2
                    if p2.vx is None:
                        # p2 moves, p1 stops
                        new_particles[idx].vx = None
                    elif p2.vx == "r":
                        # moving together
                        new_particles[idx].x += 1
                    elif p2 and p2.vx == "l":
                        if p.x == 0:
                            new_particles[idx].vx = None
                        else:
                            # both change direction
                            new_particles[idx].vx = "l"
                            new_particles[idx].x -= 1
                else:
                    # move right
                    new_particles[idx].x += 1
            # moving left
            elif p.vx == "l":
                p2 = self.get_particle(p.x - 1, p.y)
                if p.x == 0:
                    # border collision | <- p1
                    new_particles[idx].vx = "r"
                    new_particles[idx].x += 1
                elif p2:
                    # particle collision  p2 <- p1

                    if p2.vx is None:
                        # p2 moves, p1 stops
                        new_particles[idx].vx = None
                    elif p2.vx == "l":
                        # moving together, no collision
                        new_particles[idx].x -= 1
                    elif p2.vx == "r":
                        if p.x == self.width - 1:
                            new_particles[idx].vx = None
                        else:
                            # both change direction
                            new_particles[idx].vx = "r"
                            new_particles[idx].x += 1
                else:
                    # move left
                    new_particles[idx].x -= 1

            # vertical movement
            if p.vy is None:
                # not moving vertically
                if p.y != 0:
                    # check for collisions from top p2 -> p1
                    p2 = self.get_particle(p.x, p.y - 1)
                    if p2 and p2.vy == "d":
                        if p.y == self.height - 1:
                            new_particles[idx].vy = None
                        else:
                            # collision p2 -> p1
                            new_particles[idx].vy = "d"
                            new_particles[idx].y += 1
                if p.y != self.height - 1:
                    # check for collisions from bottom p1 <- p2
                    p2 = self.get_particle(p.x, p.y + 1)
                    if p2 and p2.vy == "u":
                        # collision p1 <- p2
                        if p.y == 0:  # on top
                            new_particles[idx].vy = None
                        else:
                            new_particles[idx].vy = "u"
                            new_particles[idx].y -= 1
            # moving down
            elif p.vy == "d":
                p2 = self.get_particle(p.x, p.y + 1)
                if p.y == self.height - 1:
                    # border collision p1 -> |
                    new_particles[idx].vy = "u"
                    new_particles[idx].y -= 1
                elif p2:
                    # particle collision p1 -> p2

                    if p2.vy is None:
                        # p2 moves, p1 stops
                        new_particles[idx].vy = None
                    elif p2.vy == "d":
                        # moving together
                        new_particles[idx].y += 1
                    elif p2.vy == "u":
                        if p.y == 0:
                            new_particles[
                                idx].vy = None  # wall absorbed momentum
                        else:
                            # both change direction
                            new_particles[idx].vy = "u"
                            new_particles[idx].y -= 1
                else:
                    # move down
                    new_particles[idx].y += 1
            # moving up
            elif p.vy == "u":

                p2 = self.get_particle(p.x, p.y - 1)
                if p.y == 0:
                    # border collision | <- p1
                    new_particles[idx].vy = "d"
                    new_particles[idx].y += 1
                elif p2:
                    # particle collision  p2 <- p1
                    if p2.vy is None:
                        # p2 moves, p1 stops
                        new_particles[idx].vy = None
                    elif p2.vy == "u":
                        # moving together, no collision
                        new_particles[idx].y -= 1
                    elif p2.vy == "d":
                        # both change direction
                        if p.y == self.height - 1:
                            new_particles[idx].vy = None
                        else:
                            new_particles[idx].vy = "d"
                            new_particles[idx].y += 1
                else:
                    # move left
                    new_particles[idx].y -= 1

        # update processed particles
        self.particles = new_particles

    def animate(self):
        self.process_collisions()
        self.render_particles()


class FallingDots(FacePlateAnimation):
    def __init__(self, n=10, bus=None):
        super().__init__(bus=bus)
        self._create = True
        assert 0 < n < 32
        self.n = n

    @property
    def n_dots(self):
        n = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    n += 1
        return n

    def animate(self):
        self.move_down()
        if self._create:
            if random.choice([True, False]):
                self._create = False
                x = random.randint(0, self.width - 1)
                self.grid[0][x] = 1
        if self.n_dots < self.n:
            self._create = True


class StraightParticleShooter(FacePlateAnimation):
    def __init__(self, period=None, bus=None):
        super().__init__(bus=bus)
        self.direction = "d"
        self.period = period
        self.counter = 0
        # draw shooter
        self.grid[0][0] = 1
        self.grid[1][0] = 1
        self.grid[1][1] = 1
        self.grid[2][0] = 1

    def line_down(self):
        old = copy.deepcopy(self.grid)
        for y in range(self.height):
            self.grid[y][0] = old[y - 1][0]
            self.grid[y][1] = old[y - 1][1]

    def line_up(self):
        old = copy.deepcopy(self.grid)
        for y in range(self.height):
            if y == self.height - 1:
                self.grid[y][0] = old[0][0]
                self.grid[y][1] = old[0][1]
            else:
                self.grid[y][0] = old[y + 1][0]
                self.grid[y][1] = old[y + 1][1]

    def scroll_particles(self):
        old = copy.deepcopy(self.grid)
        for x in range(2, self.width):
            for y in range(self.height):
                if old[y][x] == 1:
                    self.grid[y][x] = 0
                    if x < self.width - 1:
                        self.grid[y][x + 1] = 1

    @property
    def num_particles(self):
        n = 0
        for x in range(2, self.width):
            for y in range(self.height):
                if self.grid[y][x] == 1:
                    n += 1
        return n

    @property
    def line(self):
        for y in range(self.height):
            if self.grid[y][0] == 1:
                return y
        return 0

    def animate(self):
        # collision detection
        top_collision = False
        bottom_collision = False
        if self.grid[0][0] == 1:
            top_collision = True
        elif self.grid[self.height - 1][0] == 1:
            bottom_collision = True
        if top_collision:
            self.direction = "d"
        elif bottom_collision:
            self.direction = "u"

        # bounce the "emitter" up and down
        if self.direction == "u":
            self.line_up()
        else:
            self.line_down()

        # create particles
        period = self.period or random.randint(0, 20)
        if self.num_particles < 1 or self.counter >= period:
            self.grid[self.line + 1][2] = 1
            self.counter = 0

        # animate particles
        self.scroll_particles()
        self.counter += 1



if __name__ == "__main__":
    from ovos_utils.messagebus import get_mycroft_bus
    from time import sleep

    bus = get_mycroft_bus("192.168.1.70")

    for faceplate in ParticleBox(bus=bus):
        faceplate.display(invert=False)
        sleep(0.5)