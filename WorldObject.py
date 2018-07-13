from pysoarlib import *
import re

from .ObjectProperty import ObjectProperty

class ObjectDataUnwrapper:
    def __init__(self, data):
        self.data = data

    def id(self):
        return str(self.data["objectId"])

    def name(self):
        return re.match(r"[a-zA-Z]*", self.id()).group(0).lower()

    #def yaw(self):
    #    # Remapped so yaw=0 is down x-axis and yaw=90 is down y-axis
    #    return ((450 - int(self.data["rotation"]["y"])) % 360) * pi / 180.0

    def pos(self):
        # Swap y and z axes
        b = self.data["bounds3D"]
        [x, z, y] = [ (float(b[d+3]) + float(b[d]))/2 for d in range(0, 3) ]
        return [x, y, z]

    def rot(self):
        return ( 0.0, 0.0, 0.0 )

    def scl(self):
        b = self.data["bounds3D"]
        [x, z, y] = [ (float(b[d+3]) - float(b[d])) for d in range(0, 3) ]
        return [x, y, z]

    def is_receptacle(self):
        return bool(self.data["receptacle"])

    def is_grabbable(self):
        return bool(self.data["pickupable"])

    def inreach_state(self):
        return "inreach" if self.data["visible"] else "not-inreach"

    def open_state(self):
        if not self.data["openable"]:
            return None
        return "open2" if self.data["isopen"] else "closed2"

    def contained_objects(self):
        return [ str(obj_h) for obj_h in self.data["receptacleObjectIds"] ]


class WorldObject(object):
    def __init__(self, handle, obj_data=None):
        self.handle = handle
        self.objectId = obj_data["objectId"] if obj_data else None

        self.properties = {}
        self.contains_wmes = {}

        self.bbox_pos = [0, 0, 0]
        self.bbox_rot = [0, 0, 0]
        self.bbox_scl = [0.1, 0.1, 0.1]

        self.pos_changed = True
        self.rot_changed = True
        self.scl_changed = True

        self.obj_id = None

        if obj_data:
            self.update(obj_data)

    def copy(self, new_handle):
        obj = WorldObject(new_handle)
        obj.objectId = self.objectId
        obj.set_pos(list(self.bbox_pos))
        obj.set_rot(list(self.bbox_rot))
        obj.set_scl(list(self.bbox_scl))
        for prop in self.properties:
            obj.properties[prop] = self.properties[prop].copy()
        for obj_h in self.contains_wmes:
            obj.contains_wmes[obj_h] = SoarWME("contains", obj_h)
        return obj

    def get_handle(self):
        return self.handle

    def get_perception_id(self):
        return str(self.objectId)

    # Pos: The x,y,z world coordinate of the object
    def get_pos(self):
        return tuple(self.bbox_pos)
    def set_pos(self, pos):
        self.bbox_pos = [ pos[0], pos[1], pos[2] ]
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
        unwrapper = ObjectDataUnwrapper(obj_data)

        self.objectId = unwrapper.id()
        self.update_bbox(unwrapper)
        self.set_contained_objects(unwrapper.contained_objects())

        if len(self.properties) == 0:
            self.create_properties(unwrapper)

        self.properties["inreach"].set_value(unwrapper.inreach_state())

        if "door2" in self.properties:
            self.properties["door2"].set_value(unwrapper.open_state())


    def set_contained_objects(self, obj_handles):
        for obj_h in obj_handles:
            if obj_h not in self.contains_wmes:
                self.contains_wmes[obj_h] = SoarWME("contains", obj_h)

        to_remove = set()
        for obj_h, wme in self.contains_wmes.items():
            if obj_h not in obj_handles:
                wme.remove_from_wm()
                to_remove.add(obj_h)
        for obj_h in to_remove:
            del self.contains_wmes[obj_h]

    def update_bbox(self, unwrapper):
        self.set_pos(unwrapper.pos())
        self.set_rot(unwrapper.rot())
        self.set_scl(unwrapper.scl())

    # Properties
    def create_properties(self, unwrapper):
        self.properties["category"] = ObjectProperty("category", "object")

        self.properties["name"] = ObjectProperty("name", unwrapper.name())

        self.properties["inreach"] = ObjectProperty("inreach", "inreach")

        if unwrapper.is_receptacle():
            self.properties["receptacle"] = ObjectProperty("receptacle", "receptacle")

        if unwrapper.is_grabbable():
            self.properties["grabbable"] = ObjectProperty("grabbable", "grabbable")

        if unwrapper.open_state() != None:
            self.properties["door2"] = ObjectProperty("door2", "closed2")

    ### Methods for managing working memory structures ###

    def is_added(self):
        return (self.obj_id != None)

    def add_to_wm(self, parent_id, svs_commands):
        if self.is_added():
            return

        self.obj_id = parent_id.CreateIdWME("object")
        self.obj_id.CreateStringWME("object-handle", self.handle)

        for prop in self.properties.values():
            prop.add_to_wm(self.obj_id)

        for wme in self.contains_wmes.values():
            wme.add_to_wm(self.obj_id)

        svs_commands.append(SVSCommands.add_box(self.handle, self.bbox_pos, self.bbox_rot, self.bbox_scl))
        svs_commands.append(SVSCommands.add_tag(self.handle, "object-source", "perception"))

    def update_wm(self, svs_commands):
        if not self.is_added():
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

        for wme in self.contains_wmes.values():
            if wme.added:
                wme.update_wm()
            else:
                wme.add_to_wm(self.obj_id)


    def remove_from_wm(self, svs_commands):
        if not self.is_added():
            return

        svs_commands.append(SVSCommands.delete(self.handle))
        for prop in self.properties.values():
            prop.remove_from_wm()
        for wme in self.contains_wmes.values():
            wme.remove_from_wm()
        self.obj_id.DestroyWME()
        self.obj_id = None
