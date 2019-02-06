from math import *

class MapUtil:
    def get_obj_xyzrpy(obj):
        pos = obj["position"]
        yaw = ((450 - int(obj["rotation"]["y"])) % 360) * pi / 180.0
        return [ pos["x"], pos["z"], pos["y"], 0.0, 0.0, yaw ]

    def get_obj_yaw(obj):
        return ((450 - int(obj["rotation"]["y"])) % 360) * pi / 180.0

    def get_obj_dir(obj):
        return ((5 - int(round(obj["rotation"]["y"]/90))) % 4)

    def yaw_to_dir(yaw):
        return int(round(yaw / (pi/2)))

    def pos_to_coord(pos, grid_size=0.25):
        row = floor((pos[1] + grid_size/2)/grid_size)
        col = floor((pos[0] + grid_size/2)/grid_size)
        return (row, col)

    def get_obj_coord(obj, grid_size=0.25):
        x = obj["position"]["x"]
        y = obj["position"]["z"]
        row = floor((y + grid_size/2)/grid_size)
        col = floor((x + grid_size/2)/grid_size)
        return (row, col)

    def get_obj_bbox(obj):
        b = obj["bounds3D"]
        print(b)
        [dx, dz, dy] = [ (float(b[d+3]) - float(b[d])) for d in range(0, 3) ]
        return [ b[0] + dx/2, b[2] + dy/2, b[1] + dz/2, dx, dy, dz ]








