from math import *
import heapq

from Ai2ThorSimulator import Ai2ThorSimulator

def get_next_param(f):
    return f.readline().split(":")[1].strip()

class Node:
    def __init__(self, r, c, d):
        self.r = r
        self.c = c
        self.d = d
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def get_coord(self):
        return (self.r, self.c, self.d)

    def __lt__(self, other):
        if self.r != other.r: return self.r < other.r
        if self.c != other.c: return self.c < other.c
        if self.d != other.d: return self.d < other.d
        return False

class NavigationHelper:
    def __init__(self, map_name="test_map"):
        with open(map_name + ".map", 'r') as f:
            name = get_next_param(f)
            self.grid_size = float(get_next_param(f))

            dims = get_next_param(f).split(" ")
            self.rows = int(dims[0])
            self.cols = int(dims[1])

            corner = get_next_param(f).split(" ")
            self.min_row = int(corner[0])
            self.min_col = int(corner[1])

            self.grid = list(reversed([ [ c for c in f.readline()[:-1] ] for row in range(self.rows) ]))

    def calc_coord(self, pos):
        row = int(floor((pos[1] - self.grid_size/2)/self.grid_size)) - self.min_row
        col = int(floor((pos[0] - self.grid_size/2)/self.grid_size)) - self.min_col
        return (row, col)

    def is_clear(self, coord):
        row, col = coord
        if row < 0 or row >= self.rows:
            return False

        if col < 0 or col >= self.cols:
            return False

        return (self.grid[row][col] == ' ')

    def find_path(self, start_coord, start_rot, goal_coord):
        start_node = Node(start_coord[0], start_coord[1], start_rot)
        goals = self.calc_goals(goal_coord)

        self.opened = []
        self.closed = set()
        heapq.heapify(self.opened)
        heapq.heappush(self.opened, (0, 0, start_node))

        while len(self.opened):
            f, f2, node = heapq.heappop(self.opened)
            if node.get_coord() in self.closed:
                continue
            self.closed.add(node.get_coord())

            if node.get_coord() in goals:
                return node
            dirs = [ (0, 1), (1, 0), (0, -1), (-1, 0) ]
            neighbors = [ 
                    Node(node.r + dirs[node.d][0], node.c + dirs[node.d][1], node.d),
                    Node(node.r, node.c, (node.d+1)%4),
                    Node(node.r, node.c, (node.d-1)%4)]
            for next_node in neighbors:
                if self.is_clear(next_node.get_coord()) and \
                    next_node.get_coord() not in self.closed:
                    next_node.g = node.g + 1
                    next_node.h = int(abs(next_node.r - goal_coord[0]) + abs(next_node.c - goal_coord[1])) 
                    next_node.f = next_node.g + next_node.h
                    next_node.parent = node
                    heapq.heappush(self.opened, (next_node.f, next_node.h, next_node))
        return None
            

    def calc_goals(self, coord):
        goals = set()
        # Same square
        if self.is_clear(coord):
            for d in range(4):
                goals.add( (coord[0], coord[1], d) )
            return goals

        # offsets = (delta_row, delta_col, orientation to face coord)
        offsets = [ (0, 1, 2), (1, 0, 3), (0, -1, 0), (-1, 0, 1) ]

        # Distance 1 away
        for offset in offsets:
            if self.is_clear( (coord[0] + offset[0], coord[1] + offset[1]) ):
                goals.add( (coord[0] + offset[0], coord[1] + offset[1], offset[2]) )
        if len(goals) > 0:
            return goals

        # Distance 2 away
        for offset in offsets:
            if self.is_clear( (coord[0] + 2*offset[0], coord[1] + 2*offset[1]) ):
                goals.add( (coord[0] + 2*offset[0], coord[1] + 2*offset[1], offset[2]) )
        if len(goals) > 0:
            return goals

        # Diagonal 
        for i in range(4):
            offset = offsets[i]
            next_offset = offsets[(i+1)%4]
            row = coord[0] + offset[0] + next_offset[0]
            col = coord[1] + offset[1] + next_offset[1]
            if self.is_clear( (row, col) ):
                goals.add( (row, col, offset[2]) )
                goals.add( (row, col, next_offset[2]) )
        return goals

nav = NavigationHelper()

