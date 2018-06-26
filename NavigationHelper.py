from math import *

from Ai2ThorSimulator import Ai2ThorSimulator

class NavigationHelper:
    def __init__(self, map_name="FloorPlan28", grid_size=0.25):
        self.grid_size = grid_size

        with open(map_name + ".map", 'r') as f:
            corner = f.readline().split(" ")
            self.min_row = int(corner[0])
            self.min_col = int(corner[1])

            dims = f.readline().split(" ")
            self.rows = int(dims[0])
            self.cols = int(dims[1])

            self.grid = [ [ c for c in f.readline()[:-1] ] for row in range(self.rows+1) ]

        self.sim = Ai2ThorSimulator()
        self.sim.start()

        print(self.get_grid_square(self.sim.world["agent"]))

    def get_grid_square(self, obj):
        z = obj["position"]["z"]
        print(int(floor(z/self.grid_size)))
        row = int(floor(z/self.grid_size)) - self.min_row
        x = obj["position"]["x"]
        print(int(floor(x/self.grid_size)))
        col = int(floor(x/self.grid_size)) - self.min_col
        return (row, col)

#nav = NavigationHelper()

#
#
#class GridMapper:
#    def __init__(self, map_name="FloorPlan28", grid_size=0.25):
#        self.grid_size = grid_size
#
#        self.sim = Ai2ThorSimulator()
#        self.sim.start()
#
#        cur_node = self.get_cur_node()
#        self.visited = set()
#        self.explore_node(cur_node, "")
#
#        min_row = min([ node[0] for node in self.visited ])
#        max_row = max([ node[0] for node in self.visited ])
#        min_col = min([ node[1] for node in self.visited ])
#        max_col = max([ node[1] for node in self.visited ])
#
#        grid = [ [ (" " if (row, col) in self.visited else "X") for col in range( min_col-1, max_col+2 ) ] for row in range(min_row-1, max_row+2) ]
#        with open(map_name + ".map", 'w') as f:
#            f.write(str(min_row-1) + " " + str(min_col-1) + "\n")
#            f.write(str(max_row-min_row+2) + " " + str(max_col-min_col+2) + "\n")
#            for row in grid:
#                f.write("".join(row) + "\n")
#
#
#    def explore_node(self, node, depth):
#        self.visited.add(node)
#        (row, col) = node
#        # Try Moving Ahead
#        if ( row-1, col ) not in self.visited:
#            self.sim.exec_simple_command("MoveAhead")
#            new_node = self.get_cur_node()
#            if new_node[0] != row or new_node[1] != col:
#                self.explore_node(new_node, depth + "  ")
#                self.sim.exec_simple_command("MoveBack")
#        # Try Moving Back
#        if ( row+1, col ) not in self.visited:
#            self.sim.exec_simple_command("MoveBack")
#            new_node = self.get_cur_node()
#            if new_node[0] != row or new_node[1] != col:
#                self.explore_node(new_node, depth + "  ")
#                self.sim.exec_simple_command("MoveAhead")
#        # Try Moving Left
#        if ( row, col+1 ) not in self.visited:
#            self.sim.exec_simple_command("MoveLeft")
#            new_node = self.get_cur_node()
#            if new_node[0] != row or new_node[1] != col:
#                self.explore_node(new_node, depth + "  ")
#                self.sim.exec_simple_command("MoveRight")
#        # Try Moving Right
#        if ( row, col-1 ) not in self.visited:
#            self.sim.exec_simple_command("MoveRight")
#            new_node = self.get_cur_node()
#            if new_node[0] != row or new_node[1] != col:
#                self.explore_node(new_node, depth + "  ")
#                self.sim.exec_simple_command("MoveLeft")
#
#    def get_cur_node(self):
#        z = self.sim.world["agent"]["position"]["z"]
#        row = int(floor(z/self.grid_size))
#        x = self.sim.world["agent"]["position"]["x"]
#        col = int(floor(x/self.grid_size))
#        return (row, col)
#
#    def get_neighbors(self, node):
#        (row, col) = node
#        n = set()
#        n.add( (row+2, col) )
#        n.add( (row-3, col) )
#        n.add( (row, col+1) )
#        n.add( (row-1, col-1) )
#        return n
#
#mapper = GridMapper()
#
#
#
#
#
