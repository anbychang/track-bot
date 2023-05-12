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
        self.n_cells = 0
        self.n_steps = 0
        self.out_dir = RIGHT
        self.passed_supplies = [0] * 3
        self.prev = None
        self.score = -1
        self.used_track_ids = []
        self.x = -1
        self.y = y

    def __lt__(self, other):
        if self.score == other.score:
            return random() < 0.5
        return self.score > other.score  # since heapq always pops the smallest element

    def __str__(self):
        return f"({self.x}, {self.y}) {DIRS[self.out_dir]} score: {self.score}, #steps: {self.n_steps}"

    def add(self, track: object):
        self.last_track = track
        self.n_cells += len(track.steps) + 1
        self.n_steps += 1
        self.out_dir = track.out_dir
        self.x += track.dx
        self.y += track.dy
        self.used_track_ids.append(track.id)

    def last_track_xys(self) -> list:
        for dx, dy in self.last_track.cells:
            yield self.prev.x + dx, self.prev.y + dy

    # }}}


class TrackBot:

    # {{{
    ALL_TRACKS = [
        Track(0, LEFT, [UP], RIGHT),  # 0 means S
        Track(0, LEFT, [DOWN], RIGHT),
        Track(0, RIGHT, [DOWN], LEFT),
        Track(0, RIGHT, [DOWN, DOWN], RIGHT),
        Track(0, RIGHT, [UP], LEFT),
        Track(0, RIGHT, [UP, UP], RIGHT),
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
    ]
    # }}}
    SUPPLY_XS = [8, 17, 26]

    def __init__(self, args: object, play: bool = False):
        self.args = args
        self.init_game_tracks()
        self.init_states(args.random_start)
        if play:
            self.play()

    def draw(self):
        # {{{
        state = self.history[-1]
        print(
            f"{state.n_steps} tracks, {state.n_cells} cells, score: {state.score:.2f}"
        )

        # HIGHLIGHT_NUMBERS = ["⓪ ", "① ", "② ", "③ ", "④ ", "⑤ ", "⑥ ", "⑦ ", "⑧ ", "⑨ "]
        HIGHLIGHT_NUMBERS = "零一二三四五六七八九"
        NUMBERS = "０１２３４５６７８９"
        canvas = [["."] * self.args.map_width for _ in range(self.args.map_height)]
        for state in self.history[1:]:
            for x, y in state.last_track_xys():
                canvas[y][x] = state.last_track.id
        for x in range(self.args.map_width):
            print(f"{NUMBERS[(x+1) % 10]}", end="")
        print()
        for y in range(self.args.map_height):
            for x in range(self.args.map_width):
                if canvas[y][x] == ".":
                    if x in TrackBot.SUPPLY_XS:
                        char = "｜"
                    elif x < 36:
                        char = "．"
                    else:
                        char = "　"
                else:
                    if self.is_supply(x, y) is None:
                        char = NUMBERS[canvas[y][x]]
                    else:
                        char = HIGHLIGHT_NUMBERS[canvas[y][x]]
                    char = f"\033[1;37;{canvas[y][x]+39}m{char}\033[0m"
                print(char, end="")
            print()
        # }}}

    def expand(self, state) -> list:
        # {{{
        for track in self.game_tracks:
            # validate track
            if not Track.is_addable(state.out_dir, track.in_dir):
                continue
            if track.id in state.used_track_ids:
                continue

            # make the new state
            new_state = deepcopy(state)
            new_state.prev = state
            new_state.add(track)
            if self.args.supplies:  # 排名賽
                # clear the `used_track_ids` every 5 tracks
                if new_state.n_steps % 5 == 0:
                    new_state.used_track_ids = new_state.used_track_ids[4:]
                if new_state.n_steps % 5 == 1:
                    new_state.used_track_ids = [new_state.used_track_ids[-1]]
            else:  # 對抗賽
                # maintain the 1 tracks (on) in `used_track_ids` after the first four tracks
                if new_state.n_steps >= 4:
                    new_state.used_track_ids = [new_state.used_track_ids[-1]]
            new_state.score = self.score(new_state)

            # validate the new state
            if new_state.x < 0:
                continue
            if not (0 <= new_state.y < self.args.map_height):
                continue
            yield new_state
        # }}}

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

    def is_supply(self, x: int, y: int) -> int:
        if self.args.supplies is None:
            return
        for i in range(len(TrackBot.SUPPLY_XS)):
            sx, sy = TrackBot.SUPPLY_XS[i], self.args.supplies[i]
            if x == sx and y == sy:
                return i

    def play(self):
        # move
        i_state = 0
        state = pop(self.state_heap)
        while state.x < GOAL:
            i_state += 1
            if i_state == self.args.print_state:
                print(state)
            for child in self.expand(state):
                if i_state == self.args.print_state:
                    print(child.last_track.id, child)
                push(self.state_heap, child)
            state = pop(self.state_heap)

        # back-trace
        self.history = []
        while state:
            self.history.insert(0, state)
            state = state.prev

    def score(self, state: object) -> float:
        # {{{
        if self.args.supplies:
            for x, y in state.last_track_xys():
                i = self.is_supply(x, y)
                if i is not None:
                    state.passed_supplies[i] = 1
            n_passed_supplies = sum(state.passed_supplies)
            for i in range(len(TrackBot.SUPPLY_XS)):
                if state.x > TrackBot.SUPPLY_XS[i] and n_passed_supplies < i + 1:
                    return -1
        return state.x / state.n_steps
        # }}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game_tracks", nargs="+", type=int)
    parser.add_argument("-mh", "--map-height", default=9, type=int)
    parser.add_argument("-mw", "--map-width", default=40, type=int)
    parser.add_argument("-ps", "--print-state", type=int)
    parser.add_argument("-rs", "--random-start", action="store_true")
    parser.add_argument("-s", "--supplies", nargs=len(TrackBot.SUPPLY_XS), type=int)
    args = parser.parse_args()

    bots = [TrackBot(args, play=True) for _ in range(10)]
    bots = sorted(bots, key=lambda bot: bot.history[-1].score, reverse=True)
    for bot in bots[:3]:
        bot.draw()
