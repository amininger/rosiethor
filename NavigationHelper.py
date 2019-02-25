from math import *
import heapq

from .MapUtil import MapUtil

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

    def __str__(self):
        return str(self.get_coord())

class NavigationHelper:
    def __init__(self, map_name="testing"):
        try:
            with open("/home/aaron/sf/research/rosie-project/rosiethor/" + map_name + ".map", 'r') as f:
                name = get_next_param(f)
                self.grid_size = float(get_next_param(f))

                dims = get_next_param(f).split(" ")
                self.rows = int(dims[0])
                self.cols = int(dims[1])

                corner = get_next_param(f).split(" ")
                self.min_row = int(corner[0])
                self.min_col = int(corner[1])

                self.grid = list(reversed([ [ c for c in f.readline()[:-1] ] for row in range(self.rows) ]))
        except:
            self.rows = 0
            self.cols = 0
            self.grid = []

    def is_clear(self, row, col):
        if row < 0 or row >= self.rows:
            return False

        if col < 0 or col >= self.cols:
            return False

        return (self.grid[row][col] == ' ')

    def get_path_actions(self, path):
        if not path:
            return None
        actions = []
        for i in range(len(path)-1):
            step = path[i]
            next_step = path[i+1]
            if step.r != next_step.r or step.c != next_step.c:
                actions.append('F')
            elif (step.d + 1) % 4 == next_step.d:
                actions.append('L')
            elif (step.d - 1) % 4 == next_step.d:
                actions.append('R')
            else:
                print("UNEXPECTED PATH STEP: " + str(step) + " " + str(next_step))
        return actions

    def get_local_coord(self, xyzrpy):
        coord = MapUtil.pos_to_coord(xyzrpy)
        return [ coord[0] - self.min_row, coord[1] - self.min_col ]


    def find_path_to_pos(self, xyzrpy, goal_pos):
        start_coord = self.get_local_coord(xyzrpy)
        start_dir = MapUtil.yaw_to_dir(xyzrpy[5])
        start_node = Node(start_coord[0], start_coord[1], start_dir)

        goal_coord = self.get_local_coord(goal_pos)
        goal_coords = set([ (goal_coord[0], goal_coord[1], i) for i in range(4) ])

        path = self.astar_path_search(start_node, goal_coords)
        return self.get_path_actions(path)

    def find_path_to_obj(self, xyzrpy, goal_obj):
        start_coord = self.get_local_coord(xyzrpy)
        start_dir = MapUtil.yaw_to_dir(xyzrpy[5])
        start_node = Node(start_coord[0], start_coord[1], start_dir)

        goal_coords = self.calc_goal_coords_for_obj(goal_obj)
        print(goal_coords)
        path = self.astar_path_search(start_node, goal_coords)
        return self.get_path_actions(path)

    def astar_path_search(self, start_node, goal_coords):
        if len(goal_coords) == 0:
            return None

        self.opened = []
        self.closed = set()
        heapq.heapify(self.opened)
        heapq.heappush(self.opened, (0, 0, start_node))

        last_node = None

        avg_row = sum([ coord[0] for coord in goal_coords ])/len(goal_coords)
        avg_col = sum([ coord[1] for coord in goal_coords ])/len(goal_coords)

        while len(self.opened):
            f, f2, node = heapq.heappop(self.opened)
            if node.get_coord() in self.closed:
                continue
            self.closed.add(node.get_coord())

            if node.get_coord() in goal_coords:
                last_node = node
                break
            dirs = [ (0, 1), (1, 0), (0, -1), (-1, 0) ]
            neighbors = [ 
                    Node(node.r + dirs[node.d][0], node.c + dirs[node.d][1], node.d),
                    Node(node.r, node.c, (node.d+1)%4),
                    Node(node.r, node.c, (node.d-1)%4)]
            for next_node in neighbors:
                if self.is_clear(next_node.r, next_node.c) and \
                    next_node.get_coord() not in self.closed:
                    next_node.g = node.g + 1
                    next_node.h = int(abs(next_node.r - avg_row) + abs(next_node.c - avg_col)) 
                    next_node.f = next_node.g + next_node.h
                    next_node.parent = node
                    heapq.heappush(self.opened, (next_node.f, next_node.h, next_node))

        if not last_node:
            return None

        path = []
        node = last_node
        while node:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    # Defines which sides of the object we can try and reach (defaults to all 4 sides)
    object_sides = { 'Fridge': [0] }

    def calc_goal_coords_for_obj(self, obj):
        goal_coords = set()
        [x, y, z, dx, dy, dz]  = MapUtil.get_obj_bbox(obj)
        sides = NavigationHelper.object_sides.get(obj["objectType"], [0, 1, 2, 3])
        deltas = [ (0, 1), (1, 0), (0, -1), (-1, 0) ]
        for side in sides:
            side_dir = (side + MapUtil.get_obj_dir(obj)) % 4
            # Find the endpoints of the side we are considering
            if side_dir == 0:   endpoints = [ [x + dx/2, y - dy/2], [x + dx/2, y + dy/2] ]
            elif side_dir == 1: endpoints = [ [x - dx/2, y + dy/2], [x + dx/2, y + dy/2] ]
            elif side_dir == 2: endpoints = [ [x - dx/2, y - dy/2], [x - dx/2, y + dy/2] ]
            else:               endpoints = [ [x - dx/2, y - dy/2], [x + dx/2, y - dy/2] ]
            # Convert the side into a set of coordinates, then move back 1 direction
            coords = self.calc_region_coords(endpoints[0], endpoints[1])
            for c in coords:
                adjusted_coord = [ c[0] + deltas[side_dir][0], c[1] + deltas[side_dir][1] ]
                if not self.is_clear(adjusted_coord[0], adjusted_coord[1]):
                    # If blocked at distance 1, try distance 2
                    adjusted_coord = [ c[0] + 2*deltas[side_dir][0], c[1] + 2*deltas[side_dir][1] ]
                if not self.is_clear(adjusted_coord[0], adjusted_coord[1]):
                    # If blocked at distance 2, try distance 3
                    adjusted_coord = [ c[0] + 3*deltas[side_dir][0], c[1] + 3*deltas[side_dir][1] ]
                if self.is_clear(adjusted_coord[0], adjusted_coord[1]):
                    goal_coords.add( (adjusted_coord[0], adjusted_coord[1], (side_dir + 2) % 4) )
        return goal_coords

    def calc_region_coords(self, min_pos, max_pos):
        min_coord = self.get_local_coord(min_pos)
        max_coord = self.get_local_coord(max_pos)
        print(str(min_coord[1]) + " -> " + str(max_coord[1]))
        coords = set()
        for r in range(min_coord[0], max_coord[0]+1):
            for c in range(min_coord[1], max_coord[1]+1):
                coords.add( (r, c) )
        return coords

    # Given a desired coord, find an open square that is as close as possible
    def calc_goals(self, coord):
        goals = set()
        # Same square
        if self.is_clear(coord[0], coord[1]):
            for d in range(4):
                goals.add( (coord[0], coord[1], d) )
            return goals

        # offsets = (delta_row, delta_col, orientation to face coord)
        offsets = [ (0, 1, 2), (1, 0, 3), (0, -1, 0), (-1, 0, 1) ]

        # Distance 1 away
        for offset in offsets:
            if self.is_clear( coord[0] + offset[0], coord[1] + offset[1] ):
                goals.add( (coord[0] + offset[0], coord[1] + offset[1], offset[2]) )
        if len(goals) > 0:
            return goals

        # Distance 2 away
        for offset in offsets:
            if self.is_clear( coord[0] + 2*offset[0], coord[1] + 2*offset[1] ):
                goals.add( (coord[0] + 2*offset[0], coord[1] + 2*offset[1], offset[2]) )
        if len(goals) > 0:
            return goals

        # Diagonal 
        for i in range(4):
            offset = offsets[i]
            next_offset = offsets[(i+1)%4]
            row = coord[0] + offset[0] + next_offset[0]
            col = coord[1] + offset[1] + next_offset[1]
            if self.is_clear(row, col):
                goals.add( (row, col, offset[2]) )
                goals.add( (row, col, next_offset[2]) )
        return goals

nav = NavigationHelper()

