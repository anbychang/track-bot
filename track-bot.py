import argparse
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


class Track:  # {{{
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

    def rotate_90(self) -> object:
        return Track(
            self.id,
            ROTATE_90_DIRS[self.in_dir],
            [ROTATE_90_DIRS[step] for step in self.steps],
            ROTATE_90_DIRS[self.out_dir],
        )

    # }}}


TRACKS = [
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


class State:
    def __init__(
        self,
        x: int = None,
        y: int = None,
        out_dir: int = None,
        score: int = -1,
        prev: object = None,
        last_track: object = None,
        n_steps: int = 0,
    ):
        self.last_track = last_track
        self.prev = prev
        if prev and last_track:
            self.n_steps = self.prev.n_steps + 1
            self.out_dir = last_track.out_dir
            self.score = (prev.x + last_track.dx) / self.n_steps
            self.x = prev.x + last_track.dx
            self.y = prev.y + last_track.dy
            self.used_track_ids = self.prev.used_track_ids[:]
            self.used_track_ids.append(last_track.id)
            if len(self.used_track_ids) > 3:
                self.used_track_ids.pop(0)
        else:
            self.n_steps = n_steps
            self.out_dir = out_dir
            self.score = score
            self.used_track_ids = []
            self.x = x
            self.y = y

    def __lt__(self, other):
        if self.score == other.score:
            return random() < 0.5
        return self.score > other.score  # since heapq always pops the smallest element

    def __str__(self):
        return f"({self.x}, {self.y}) {DIRS[self.out_dir]} score: {self.score}, #steps: {self.n_steps}"


class TrackBot:

    seen_states = {}

    def __init__(self, track_ids: list[int], map_height: int = 9, map_width: int = 40):
        self.map_height = map_height
        self.map_width = map_width
        self.random = random
        self.tracks = []
        for track in TRACKS:
            if track.id not in track_ids:
                continue
            self.tracks.append(track)
            for i in range(3):
                self.tracks.append(self.tracks[-1].rotate_90())

    def expand(self, state) -> list:
        states = []
        for track in self.tracks:
            if track.in_dir != INVERSE_DIRS[state.out_dir]:
                continue
            if track.id in state.used_track_ids:
                continue
            new_state = State(prev=state, last_track=track)
            if new_state.x < 0:
                continue
            if not (0 <= new_state.y < self.map_height):
                continue
            states.append(new_state)
        return states

    def play(self):
        heap = []

        # starting states
        # for y in range(9):
        #     push(heap, State(-1, y, RIGHT))
        push(heap, State(-1, 4, RIGHT))
        state = pop(heap)

        # move
        i = 0
        while state.x < GOAL:
            i += 1
            # if i == 2:
            #     print(state)
            for child in self.expand(state):
                if self.seen(child):
                    continue
                # if i == 2:
                #     print(child.last_track.id, child)
                push(heap, child)
            state = pop(heap)

        # back-trace
        print(state.n_steps, state.score)
        states = []
        while state:
            states.insert(0, state)
            state = state.prev

        # draw
        self.map = [["."] * self.map_width for _ in range(self.map_height)]
        for state in states[1:]:
            for cell in state.last_track.cells:
                x = state.prev.x + cell[0]
                y = state.prev.y + cell[1]
                self.map[y][x] = state.last_track.id
        for y in range(self.map_height):
            for x in range(self.map_width):
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
    parser.add_argument("tracks", nargs="+", type=int)
    args = parser.parse_args()
    bot = TrackBot(args.tracks)
    bot.play()
