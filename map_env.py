import sys
from math import *

from tkinter import *

from rosiethor import *

def get_info(sim):
    agent = sim.world["agent"]
    print( agent["position"]["x"], agent["position"]["z"], agent["rotation"]["y"])

class GridMapper:
    def __init__(self, map_name="FloorPlan28", grid_size=0.25):
        self.grid_size = grid_size

        self.sim = Ai2ThorSimulator()
        self.sim.start()

        # Make sure facing same direction
        while int(self.sim.world["agent"]["rotation"]["y"]) != 0:
            self.sim.exec_simple_command("RotateRight")

        cur_node = self.get_cur_node()
        self.visited = set()
        self.explore_node(cur_node, "")

        min_row = min([ node[0] for node in self.visited ])
        max_row = max([ node[0] for node in self.visited ])
        min_col = min([ node[1] for node in self.visited ])
        max_col = max([ node[1] for node in self.visited ])

        grid = [ [ (" " if (row, col) in self.visited else "X") for col in range( min_col-1, max_col+2 ) ] for row in range(min_row-1, max_row+2) ]
        with open(map_name + ".map", 'w') as f:
            f.write("Name: " + map_name + "\n")
            f.write("Grid Size: " + str(grid_size) + "\n")
            f.write("Min Row/Col: " + str(min_row-1) + " " + str(min_col-1) + "\n")
            f.write("Max Row/Col: " + str(max_row-min_row+2) + " " + str(max_col-min_col+2) + "\n")
            for row in grid:
                f.write("".join(row) + "\n")


    def explore_node(self, node, depth):
        self.visited.add(node)
        (row, col) = node
        # Try Moving Ahead
        if ( row+1, col ) not in self.visited:
            self.sim.exec_simple_command("MoveAhead")
            new_node = self.get_cur_node()
            if new_node[0] != row or new_node[1] != col:
                self.explore_node(new_node, depth + "  ")
                self.sim.exec_simple_command("MoveBack")
        # Try Moving Back
        if ( row-1, col ) not in self.visited:
            self.sim.exec_simple_command("MoveBack")
            new_node = self.get_cur_node()
            if new_node[0] != row or new_node[1] != col:
                self.explore_node(new_node, depth + "  ")
                self.sim.exec_simple_command("MoveAhead")
        # Try Moving Left
        if ( row, col-1 ) not in self.visited:
            self.sim.exec_simple_command("MoveLeft")
            new_node = self.get_cur_node()
            if new_node[0] != row or new_node[1] != col:
                self.explore_node(new_node, depth + "  ")
                self.sim.exec_simple_command("MoveRight")
        # Try Moving Right
        if ( row, col+1 ) not in self.visited:
            self.sim.exec_simple_command("MoveRight")
            new_node = self.get_cur_node()
            if new_node[0] != row or new_node[1] != col:
                self.explore_node(new_node, depth + "  ")
                self.sim.exec_simple_command("MoveLeft")

    def get_cur_node(self):
        x = self.sim.world["agent"]["position"]["x"]
        y = self.sim.world["agent"]["position"]["z"]
        row = int(floor((y - self.grid_size/2)/self.grid_size))
        col = int(floor((x - self.grid_size/2)/self.grid_size))
        return (row, col)

    def get_neighbors(self, node):
        (row, col) = node
        n = set()
        n.add( (row+2, col) )
        n.add( (row-3, col) )
        n.add( (row, col+1) )
        n.add( (row-1, col-1) )
        return n

mapper = GridMapper()

