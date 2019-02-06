import sys
from math import *

from tkinter import *

from rosiethor import *

class GridMapper:
    def __init__(self, map_name="simple_kitchen", grid_size=0.25):
        self.grid_size = grid_size

        self.sim = Ai2ThorSimulator()
        self.sim.start()

        # Make sure facing 0 direction (+x axis)
        while MapUtil.get_obj_dir(self.sim.world["agent"]) != 0:
            self.sim.exec_simple_command("RotateRight")

        cur_coord = MapUtil.get_obj_coord(self.sim.world["agent"], self.grid_size)
        self.visited = set()
        self.explore_coord(cur_coord, "")

        min_row = min([ coord[0] for coord in self.visited ])
        max_row = max([ coord[0] for coord in self.visited ])
        min_col = min([ coord[1] for coord in self.visited ])
        max_col = max([ coord[1] for coord in self.visited ])

        grid = [ [ (" " if (row, col) in self.visited else "X") for col in range( min_col-1, max_col+2 ) ] for row in range(min_row-1, max_row+2) ]
        with open(map_name + ".map", 'w') as f:
            f.write("Name: " + map_name + "\n")
            f.write("Grid Size: " + str(grid_size) + "\n")
            f.write("Grid Dims: " + str(max_row-min_row+3) + " " + str(max_col-min_col+3) + "\n")
            f.write("Min Row/Col: " + str(min_row-1) + " " + str(min_col-1) + "\n")
            for row in reversed(grid):
                f.write("".join(row) + "\n")

    def explore_coord(self, coord, depth):
        print(MapUtil.get_obj_xyzrpy(self.sim.world["agent"]))
        self.visited.add(coord)
        (row, col) = coord

        # Try Moving Ahead
        if ( row, col+1 ) not in self.visited:
            self.sim.exec_simple_command("MoveAhead")
            new_coord = MapUtil.get_obj_coord(self.sim.world["agent"], self.grid_size)
            if new_coord[0] != row or new_coord[1] != col:
                self.explore_coord(new_coord, depth + "  ")
                self.sim.exec_simple_command("MoveBack")
        # Try Moving Back
        if ( row, col-1 ) not in self.visited:
            self.sim.exec_simple_command("MoveBack")
            new_coord = MapUtil.get_obj_coord(self.sim.world["agent"], self.grid_size)
            if new_coord[0] != row or new_coord[1] != col:
                self.explore_coord(new_coord, depth + "  ")
                self.sim.exec_simple_command("MoveAhead")
        # Try Moving Left
        if ( row+1, col ) not in self.visited:
            self.sim.exec_simple_command("MoveLeft")
            new_coord = MapUtil.get_obj_coord(self.sim.world["agent"], self.grid_size)
            if new_coord[0] != row or new_coord[1] != col:
                self.explore_coord(new_coord, depth + "  ")
                self.sim.exec_simple_command("MoveRight")
        # Try Moving Right
        if ( row-1, col ) not in self.visited:
            self.sim.exec_simple_command("MoveRight")
            new_coord = MapUtil.get_obj_coord(self.sim.world["agent"], self.grid_size)
            if new_coord[0] != row or new_coord[1] != col:
                self.explore_coord(new_coord, depth + "  ")
                self.sim.exec_simple_command("MoveLeft")

mapper = GridMapper(map_name="testing")

