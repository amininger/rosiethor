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

    def properties(self):
        name = self.name()

        if name == "fridge": return { "name": "fridge1" } 
        if name == "sink": return { "name": "sink1" } 
        if name == "countertop": return { "name": "counter1" } 
        if name == "cabinet": return { "name": "cupboard1" } 
        if name == "drawer": return { "name": "drawer1" } 
        if name == "tabletop": return { "name": "table1" } 
        if name == "trash": return { "name": "garbage1" } 
        if name == "microwave": return { "name": "microwave1" } 
        if name == "butterknife": return { "shape": "knife1", "subcategory": "utensil1" } 
        if name == "fork": return { "shape": "fork1", "subcategory": "utensil1" } 
        if name == "mug": return { "shape": "mug1", "color": "white1" } 
        if name == "mugfilled": return { "shape": "mug1", "color": "white1" } 
        if name == "sodacan": return { "shape": "soda1", "color": "red1", "subcategory": "liquid1" } 
        if name == "waterbottle": return { "shape": "water1", "color": "blue1", "subcategory": "liquid1" } 
        if name == "milkcarton": return { "shape": "milk1", "color": "white1", "subcategory": "liquid1" } 
        if name == "bowl": return { "shape": "mug1", "color": "blue1" } 
        if name == "bowlfilled": return { "shape": "mug1", "color": "blue1" } 
        if name == "container": return { "shape": "pitcher1", "subcategory": "liquid1" } 
        if name == "containerfull": return { "shape": "pitcher1", "subcategory": "liquid1" } 

        return { "name": name }

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
        name = self.name()
        return bool(self.data["receptacle"]) and name not in [ "tabletop", "countertop" ]

    def is_surface(self):
        name = self.name()
        return bool(self.data["receptacle"]) and name in [ "tabletop", "countertop" ]

    def is_grabbable(self):
        return bool(self.data["pickupable"])

    def reachable_state(self):
        return "reachable1" if self.data["visible"] else "not-reachable1"

    def temperature(self):
        if float(self.data["temperature"]) > 125:
            return "hot1"
        elif float(self.data["temperature"]) > 70:
            return "warm1"
        elif float(self.data["temperature"]) > 50:
            return "room-temp1"
        elif float(self.data["temperature"]) > 30:
            return "cool1"
        return "cold1"

    def open_state(self):
        if not self.data["openable"]:
            return None
        return "open2" if self.data["isopen"] else "closed2"

    def activated_state(self):
        if not self.data["activatable"]:
            return None
        return "on2" if self.data["isactivate"] else "off2"

    def timeleft(self):
        return str(self.data["timeleft"])

    def contained_objects(self):
        return [ str(obj_h) for obj_h in self.data["receptacleObjectIds"] ]

    def container_state(self):
        obj_type = self.data["objectType"]
        if obj_type in [ "Mug", "Bowl", "Container" ]:
            return "empty1"
        if obj_type in [ "MugFilled", "BowlFilled", "ContainerFull" ]:
            return "full1"
        return None
        
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

        if len(self.properties) == 0:
            self.create_properties(unwrapper)

        self.properties["reachable"].set_value(unwrapper.reachable_state())
        self.properties["temperature"].set_value(unwrapper.temperature())
        self.properties["timeleft"].set_value(unwrapper.timeleft())

        if "door2" in self.properties:
            self.properties["door2"].set_value(unwrapper.open_state())

        if "activation1" in self.properties:
            self.properties["activation1"].set_value(unwrapper.activated_state())

        if "container1" in self.properties:
            self.properties["container1"].set_value(unwrapper.container_state())


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

        props = unwrapper.properties()
        for prop_name, prop_val in props.items():
            self.properties[prop_name] = ObjectProperty(prop_name, prop_val)

        self.properties["reachable"] = ObjectProperty("is-reachable1", "reachable1")

        self.properties["temperature"] = ObjectProperty("temperature", unwrapper.temperature())

        self.properties["timeleft"] = ObjectProperty("timeleft", unwrapper.timeleft())

        if unwrapper.is_receptacle():
            self.properties["receptacle"] = ObjectProperty("receptacle", "receptacle")

        if unwrapper.is_surface():
            self.properties["receptacle"] = ObjectProperty("receptacle", "surface")

        if unwrapper.is_grabbable():
            self.properties["grabbable"] = ObjectProperty("is-grabbable1", "grabbable1")

        if unwrapper.open_state() != None:
            self.properties["door2"] = ObjectProperty("door2", "closed2")

        if unwrapper.activated_state() != None:
            self.properties["activation1"] = ObjectProperty("activation1", "off2")

        if unwrapper.container_state() != None:
            self.properties["container1"] = ObjectProperty("container1", "empty1")

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
