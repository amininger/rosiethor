from pysoarlib import *
import re

from ObjectProperty import ObjectProperty


class WorldObject(object):
    def __init__(self, handle, obj_data):
        self.handle = handle

        self.properties = {}

        self.bbox_pos = [0, 0, 0]
        self.bbox_rot = [0, 0, 0]
        self.bbox_scl = [0.1, 0.1, 0.1]

        self.pos_changed = True
        self.rot_changed = True
        self.scl_changed = True

        self.added = False
        self.obj_id = None

        self.update(obj_data)

    def get_handle(self):
        return self.handle

    def get_perception_id(self):
        return str(self.last_data["objectId"].replace("|", ""))

    def get_last_data(self):
        return self.last_data

    # Pos: The x,y,z world coordinate of the object
    def get_pos(self):
        return tuple(self.bbox_pos)
    def set_pos(self, pos):
        self.bbox_pos = [ pos[0], pos[1], -pos[2] ]
        self.pos_changed = True

    # Rot: The orientation of the world object, in x,y,z axis rotations
    def get_rot(self):
        return tuple(self.bbox_rot)
    def set_rot(self, rot):
        self.bbox_rot = list(rot)
        self.rot_changed = True

    # Scl: The scale of the world object in x,y,z dims, scl=1.0 means width of 1 unit
    def get_scl(self):
        return tuple(self.bbox_scl)
    def set_scl(self, scl):
        self.bbox_scl = list(scl)
        self.scl_changed = True

    def update(self, obj_data):
        if len(self.properties) == 0:
            self.create_properties(obj_data)
        self.last_data = obj_data
        self.update_bbox(obj_data)

        inreach = "inreach" if obj_data["visible"] else "not-inreach"
        self.properties["inreach"].set_value(inreach)

        if self.last_data["openable"]:
            open_value = "open2" if obj_data["isopen"] else "closed2"
            self.properties["door2"].set_value(open_value)

    def update_bbox(self, obj_data):
        pos = obj_data["position"]
        self.set_pos( (float(pos["x"]), float(pos["y"]), float(pos["z"])) )

        rot = obj_data["rotation"]
        self.set_rot( (float(pos["x"]), float(pos["y"]), float(pos["z"])) )

    # Properties
    def create_properties(self, obj_data):
        self.properties["category"] = ObjectProperty("category", "object")

        obj_name = re.match(r"[a-zA-Z]*", self.handle).group(0).lower()
        self.properties["name"] = ObjectProperty("name", obj_name)

        self.properties["inreach"] = ObjectProperty("inreach", "inreach")

        if obj_data["receptacle"]:
            self.properties["receptacle"] = ObjectProperty("receptacle", "receptacle")

        if obj_data["pickupable"]:
            self.properties["grabbable"] = ObjectProperty("grabbable", "grabbable")

        if obj_data["openable"]:
            self.properties["door2"] = ObjectProperty("door2", "closed2")

    ### Methods for managing working memory structures ###

    def is_added(self):
        return self.added

    def add_to_wm(self, parent_id, svs_commands):
        if self.added:
            return

        self.obj_id = parent_id.CreateIdWME("object")
        self.obj_id.CreateStringWME("object-handle", self.handle)

        for prop in self.properties.values():
            prop.add_to_wm(self.obj_id)

        svs_commands.append(SVSCommands.add_box(self.handle, self.bbox_pos, self.bbox_rot, self.bbox_scl))
        svs_commands.append(SVSCommands.add_tag(self.handle, "object-source", "perception"))
        
        self.added = True;

    def update_wm(self, svs_commands):
        if not self.added:
            return

        if self.pos_changed:
            svs_commands.append(SVSCommands.change_pos(self.handle, self.bbox_pos))
            self.pos_changed = False

        if self.rot_changed:
            svs_commands.append(SVSCommands.change_rot(self.handle, self.bbox_rot))
            self.rot_changed = False

        if self.scl_changed:
            svs_commands.append(SVSCommands.change_scl(self.handle, self.bbox_scl))
            self.scl_changed = False

        for prop in self.properties.values():
            prop.update_wm()

    def remove_from_wm(self, svs_commands):
        if not self.added:
            return

        svs_commands.append(SVSCommands.delete(self.handle))
        for prop in self.properties.values():
            prop.remove_from_wm()
        self.obj_id.DestroyWME()
        self.obj_id = None
        self.added = False
