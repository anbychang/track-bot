import argparse
from copy import deepcopy
from heapq import heappop as pop
from heapq import heappush as push
from random import random

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

GOAL = 36

DIRS = ["UP", "RIGHT", "DOWN", "LEFT"]
DX_DIRS = [0, 1, 0, -1]
DY_DIRS = [-1, 0, 1, 0]
INVERSE_DIRS = [2, 3, 0, 1]
ROTATE_90_DIRS = [1, 2, 3, 0]


class Track:
    # {{{
    def __init__(self, _id: int, in_dir: int, steps: list[int], out_dir: int):
        self.dx = DX_DIRS[INVERSE_DIRS[in_dir]]
        self.dy = DY_DIRS[INVERSE_DIRS[in_dir]]
        self.cells = [(self.dx, self.dy)]
        for step in steps:
            self.dx += DX_DIRS[step]
            self.dy += DY_DIRS[step]
            self.cells.append((self.dx, self.dy))
        self.id = _id
        self.in_dir = in_dir
        self.steps = steps
        self.out_dir = out_dir

    def __str__(self):
        return f"{self.id} {DIRS[self.in_dir]} {self.dx} {self.dy} {DIRS[self.out_dir]}"

    def is_addable(prev_out_dir: int, next_in_dir: int) -> bool:
        return prev_out_dir == INVERSE_DIRS[next_in_dir]

    def rotate_90(self) -> object:
        return Track(
            self.id,
            ROTATE_90_DIRS[self.in_dir],
            [ROTATE_90_DIRS[step] for step in self.steps],
            ROTATE_90_DIRS[self.out_dir],
        )

    # }}}


class State:
    # {{{
    def __init__(self, y: int):
        self.last_track = None
        self.n_steps = 0
        self.out_dir = RIGHT
        self.prev = None
        self.score = -1
        self.used_track_ids = []
        self.x = -1
        self.y = y

    def add(self, track: object):
        self.last_track = track
        self.n_steps += 1
        self.out_dir = track.out_dir
        self.x += track.dx
        self.y += track.dy
        self.score = self.x / self.n_steps
        self.used_track_ids.append(track.id)
        if len(self.used_track_ids) > 3:
            self.used_track_ids.pop(0)

    def __lt__(self, other):
        if self.score == other.score:
            return random() < 0.5
        return self.score > other.score  # since heapq always pops the smallest element

    def __str__(self):
        return f"({self.x}, {self.y}) {DIRS[self.out_dir]} score: {self.score}, #steps: {self.n_steps}"

    # }}}


class TrackBot:

    seen_states = {}
    ALL_TRACKS = [
        # {{{
        Track(1, LEFT, [DOWN, DOWN], LEFT),
        Track(1, LEFT, [UP, UP], LEFT),
        Track(2, LEFT, [DOWN, DOWN], RIGHT),
        Track(3, UP, [DOWN, DOWN], DOWN),
        Track(4, LEFT, [DOWN, DOWN], DOWN),
        Track(4, DOWN, [UP, UP], LEFT),
        Track(5, RIGHT, [DOWN, DOWN], DOWN),
        Track(5, DOWN, [UP, UP], RIGHT),
        Track(6, UP, [DOWN], DOWN),
        Track(7, RIGHT, [DOWN], DOWN),
        Track(7, DOWN, [UP], RIGHT),
        Track(8, LEFT, [DOWN], DOWN),
        Track(8, DOWN, [UP], LEFT),
        Track(9, LEFT, [DOWN], LEFT),
        Track(9, LEFT, [UP], LEFT),
        # }}}
    ]

    def __init__(self, args: object):
        self.args = args
        self.init_game_tracks()
        self.init_states(args.random_start)

    def init_game_tracks(self):
        # {{{
        self.game_tracks = []
        for track in TrackBot.ALL_TRACKS:
            if track.id not in self.args.game_tracks:
                continue
            self.game_tracks.append(track)
            for i in range(3):  # rotate the track 90 degrees 3 times
                self.game_tracks.append(self.game_tracks[-1].rotate_90())
        # }}}

    def init_states(self, random: bool = True):
        # {{{
        self.state_heap = []
        if random:
            for y in range(9):
                push(self.state_heap, State(y))
        else:
            push(self.state_heap, State(4))
        # }}}

    def expand(self, state) -> list:
        # {{{
        for track in self.game_tracks:
            if not Track.is_addable(state.out_dir, track.in_dir):
                continue
            if track.id in state.used_track_ids:
                continue
            new_state = deepcopy(state)
            new_state.prev = state
            new_state.add(track)
            if new_state.x < 0:
                continue
            if not (0 <= new_state.y < self.args.map_height):
                continue
            yield new_state
        # }}}

    def play(self):

        # move
        i_state = 0
        state = pop(self.state_heap)
        while state.x < GOAL:
            i_state += 1
            if i_state == self.args.print_state:
                print(state)
            for child in self.expand(state):
                if self.seen(child):
                    continue
                if i_state == self.args.print_state:
                    print(child.last_track.id, child)
                push(self.state_heap, child)
            state = pop(self.state_heap)

        # back-trace
        print(state.n_steps, state.score)
        states = []
        while state:
            states.insert(0, state)
            state = state.prev

        # draw
        self.map = [["."] * self.args.map_width for _ in range(self.args.map_height)]
        for state in states[1:]:
            for cell in state.last_track.cells:
                x = state.prev.x + cell[0]
                y = state.prev.y + cell[1]
                self.map[y][x] = state.last_track.id
        for y in range(self.args.map_height):
            for x in range(self.args.map_width):
                if self.map[y][x] == ".":
                    print(".", end="")
                else:
                    print(
                        f"\033[1;37;{self.map[y][x]+39}m{self.map[y][x]}\033[0m", end=""
                    )
            print()

    def seen(self, track: object) -> bool:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game_tracks", nargs="+", type=int)
    parser.add_argument("-mh", "--map-height", default=9, type=int)
    parser.add_argument("-mw", "--map-width", default=40, type=int)
    parser.add_argument("-ps", "--print-state", type=int)
    parser.add_argument("-rs", "--random-start", action="store_true")
    args = parser.parse_args()
    bot = TrackBot(args)
    bot.play()
