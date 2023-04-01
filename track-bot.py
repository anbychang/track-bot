import copy
from heapq import heappop as pop
from heapq import heappush as push

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

GOAL = 36

DIRS = ["UP", "RIGHT", "DOWN", "LEFT"]
INVERSE_DIRS = [2, 3, 0, 1]
ROTATE_90_DIRS = [1, 2, 3, 0]


class Track:  # {{{
    def __init__(self, _id: int, in_dir: int, dx: int, dy: int, out_dir: int):
        self.id = _id
        self.in_dir = in_dir
        self.dx = dx
        self.dy = dy
        self.out_dir = out_dir

    def __str__(self):
        return f"{self.id} {DIRS[self.in_dir]} {self.dx} {self.dy} {DIRS[self.out_dir]}"

    def rotate_90(self) -> object:
        return Track(
            self.id,
            ROTATE_90_DIRS[self.in_dir],
            -self.dy,
            self.dx,
            ROTATE_90_DIRS[self.out_dir],
        )


# }}}


class State:
    def __init__(self, x: int, y: int, out_dir: int, score: int = 0):
        self.out_dir = out_dir
        self.score = score
        self.x = x
        self.y = y

    def __lt__(self, other):
        return self.score < other.score

    def __str__(self):
        return f"{self.x} {self.y} {DIRS[self.out_dir]} {self.score}"


class TrackBot:

    seen_states = {}

    def __init__(self, tracks: list, map_height: int = 9, map_width: int = 36):
        self.map_height = map_height
        self.map_width = map_width
        State.TRACKS = []
        for track in tracks:
            State.TRACKS.append(track)
            for i in range(3):
                State.TRACKS.append(State.TRACKS[-1].rotate_90())

    def expand(self, state) -> list:
        states = []
        for track in State.TRACKS:
            if track.in_dir != INVERSE_DIRS[state.out_dir]:
                continue
            new_state = State(
                state.x + track.dx,
                state.y + track.dy,
                track.out_dir,
                state.x + track.dx,
            )
            if new_state.x < 0:
                continue
            if not (0 <= new_state.y < self.map_height):
                continue
            states.append(new_state)
        return states

    def play(self):
        heap = []

        # deal with the starting board
        # parent_boards = { to_string(board): None}
        # board_score = score(board)
        for y in range(9):
            push(heap, State(-1, y, RIGHT))
        state = pop(heap)

        # move
        while state.score < GOAL:
            for child in self.expand(state):
                print(child)
                if self.seen(child):
                    continue
                push(heap, child)
            state = heap.pop()

    def seen(self, track: object) -> bool:
        return False


bot = TrackBot(
    [
        Track(1, LEFT, 1, 2, LEFT),
        Track(1, LEFT, 1, -2, LEFT),
        Track(2, LEFT, 1, 2, RIGHT),
        Track(3, UP, 0, 3, DOWN),
        Track(4, LEFT, 1, 2, DOWN),
        Track(4, DOWN, 0, -3, LEFT),
        Track(5, RIGHT, -1, 2, DOWN),
        Track(5, DOWN, 0, -3, RIGHT),
    ]
)
bot.play()
