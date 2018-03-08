from soarutil import *


class WorldObject(object):
    def __init__(self, handle, obj_data):
        self.handle = handle

        self.obj_id = None
        self.open_wme = None
        self.closed_wme = None
        self.added = False

        self.bbox_pos = [0, 0, 0]
        self.bbox_rot = [0, 0, 0]
        self.bbox_scl = [0.1, 0.1, 0.1]

        self.pos_changed = True
        self.rot_changed = True
        self.scl_changed = True

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
        self.last_data = obj_data
        self.update_bbox(obj_data)

    def update_bbox(self, obj_data):
        pos = obj_data["position"]
        self.set_pos( (float(pos["x"]), float(pos["y"]), float(pos["z"])) )

        rot = obj_data["rotation"]
        self.set_rot( (float(pos["x"]), float(pos["y"]), float(pos["z"])) )

    ### Methods for managing working memory structures ###

    def is_added(self):
        return self.added

    def add_to_wm(self, parent_id, svs_commands):
        if self.added:
            return

        self.obj_id = parent_id.CreateIdWME("object")
        self.obj_id.CreateStringWME("object-handle", self.handle)
        props_id = self.obj_id.CreateIdWME("properties")

        prop_id = props_id.CreateIdWME("property")
        prop_id.CreateStringWME("property-handle", "category")
        prop_id.CreateStringWME("type", "visual")
        prop_id.CreateIdWME("values").CreateFloatWME("object", 1.0)

        prop_id = props_id.CreateIdWME("property")
        prop_id.CreateStringWME("property-handle", "name")
        prop_id.CreateStringWME("type", "visual")
        prop_id.CreateIdWME("values").CreateFloatWME(self.handle.replace("-", "+").split("+")[0].lower(), 1.0)

        if self.last_data["receptacle"]:
            prop_id = props_id.CreateIdWME("property")
            prop_id.CreateStringWME("property-handle", "receptacle")
            prop_id.CreateStringWME("type", "visual")
            prop_id.CreateIdWME("values").CreateFloatWME("receptacle", 1.0)

        if self.last_data["pickupable"]:
            prop_id = props_id.CreateIdWME("property")
            prop_id.CreateStringWME("property-handle", "grabbable")
            prop_id.CreateStringWME("type", "visual")
            prop_id.CreateIdWME("values").CreateFloatWME("grabbable", 1.0)

        if self.last_data["openable"]:
            prop_id = props_id.CreateIdWME("property")
            prop_id.CreateStringWME("property-handle", "door2")
            prop_id.CreateStringWME("type", "visual")
            vals_id = prop_id.CreateIdWME("values")

            self.open_wme = SoarWME("open2", 0.0)
            self.closed_wme = SoarWME("closed2", 0.0)
            if self.last_data["isopen"]:
                self.open_wme.set_value(1.0)
            else:
                self.closed_wme.set_value(1.0)
            self.open_wme.add_to_wm(vals_id)
            self.closed_wme.add_to_wm(vals_id)

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

        if self.last_data["openable"]:
            if self.last_data["isopen"]:
                self.open_wme.set_value(1.0)
                self.closed_wme.set_value(0.0)
            else:
                self.open_wme.set_value(0.0)
                self.closed_wme.set_value(1.0)
            self.open_wme.update_wm()
            self.closed_wme.update_wm()

    def remove_from_wm(self, svs_commands):
        if not self.added:
            return

        svs_commands.append(SVSCommands.delete(self.handle))
        self.obj_id.DestroyWME()
        self.obj_id = None
        self.open_wme = None
        self.closed_wme = None
        self.added = False
