from heapq import heappop as pop
from heapq import heappush as push

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIRS = ['UP', 'RIGHT', 'DOWN', 'LEFT']

class State():

    def __init__(self, x: int, y: int, out_dir: int, score: int = 0):
        self.out_dir = out_dir
        self.score = score
        self.x = x
        self.y = y

    def __lt__(self, other):
        return self.score < other.score

    def __str__(self):
        return f'{self.x} {self.y} {DIRS[self.out_dir]} {self.score}'


class Track():

    def __init__(self, in_dir: int, dx: int, dy: int, out_dir: int):
        self.in_dir = in_dir
        self.dx = dx
        self.dy = dy
        self.out_dir = out_dir


class TrackBot():

    def __init__(self, tracks: list, map_height: int = 9, map_width: int = 36):
        self.map_height = map_height
        self.map_width = map_width
        self.tracks = tracks

    def play(self):
        heap = []

        # deal with the starting board
        # parent_boards = { to_string(board): None}
        # board_score = score(board)
        for y in range(9):
            push(heap, State(-1, y, RIGHT))
        state = pop(heap)
        print(state)
        return

        # move
        while score < GOAL:
            for child in self.expand(state):
                if self.seen(child):
                    continue
                heap.push([child.score(), child])
            score, state = heap.pop()


bot = TrackBot([
    Track(LEFT, 1, 2, LEFT), # 1
    Track(LEFT, 1, 2, RIGHT), # 2
    Track(UP, 0, 3, DOWN), # 3
    Track(LEFT, 1, 2, DOWN), # 4
    Track(RIGHT, -1, 2, DOWN) # 5
])
bot.play()
