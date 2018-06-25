from pysoarlib import *
from math import *

VIEW_DIST = 3.8
VIEW_ANGLE = 1.5708 * 0.8
VIEW_HEIGHT = 2.0


class Robot():
    def __init__(self, obj_manager):
        self.obj_manager = obj_manager

        self.self_id = None
        self.arm_id = None
        self.pose_id = None
        self.pose_wmes = []
        for dim in [ "x", "y", "z", "r", "p", "y"]:
            self.pose_wmes.append(SoarWME(dim, 0.0))

        self.held_object = SoarWME("holding-object", "none")
        self.moving_state = SoarWME("moving-status", "stopped")

        self.pose = [0.0] * 6
        self.update_pose = False
        self.dims = [.5, .5, 1.0]

        self.added = False

    def update(self, world_info):
        if len(world_info["inventoryObjects"]) > 0:
            held_obj = world_info["inventoryObjects"][0]["objectId"]
            self.held_object.set_value(self.obj_manager.get_soar_handle(held_obj))
        else:
            self.held_object.set_value("none")

        pos = world_info["agent"]["position"]
        rot = world_info["agent"]["rotation"]
        pose = [ pos["x"], pos["y"], pos["z"], rot["x"], rot["y"], rot["z"] ]

        for i in range(6):
            if abs(pose[i] - self.pose[i]) > 0:
                self.update_pose = True
                self.pose = pose
                break


    def get_pose(self):
        return list(self.pose)

    # Creates a triangular view region of height VIEW_DIST
    # and angle VIEW_ANGLE and a height of 2m
    #def get_view_region_verts(self):
    #    verts = ""
    #    dx = VIEW_DIST/2
    #    dy = VIEW_DIST * sin(VIEW_ANGLE/2)
    #    dz = VIEW_HEIGHT/2
    #    # Top triangle
    #    # FIX: FORMAT
    #    verts += String.format("%f %f %f ", -dx, 0.0, dz)
    #    verts += String.format("%f %f %f ", dx, -dy, dz)
    #    verts += String.format("%f %f %f ", dx, dy, dz)
    #    # Bottom triangle
    #    verts += String.format("%f %f %f ", -dx, 0.0, -dz)
    #    verts += String.format("%f %f %f ", dx, -dy, -dz)
    #    verts += String.format("%f %f %f", dx, dy, -dz)

    #    return verts

    def add_to_wm(self, parent_id, svs_commands):
        if self.added:
            return

        self.self_id = parent_id.CreateIdWME("self");
        self.moving_state.add_to_wm(self.self_id)

        self.pose_id = self.self_id.CreateIdWME("pose")
        for wme in self.pose_wmes:
            wme.add_to_wm(self.pose_id)

        self.arm_id = self.self_id.CreateIdWME("arm")
        self.arm_id.CreateStringWME("moving-status", "wait")
        self.held_object.add_to_wm(self.arm_id)
        
        # TODO: Fix SVS 
        #svsCommands.append(String.format("add robot world p %s r %s\n", 
        #        SVSCommands.posToStr(pos), SVSCommands.rotToStr(rot)));
        #svsCommands.append(String.format("add robot_pos robot\n"));
        #svsCommands.append(String.format("add robot_body robot v %s p .2 0 0 s %s\n", 
        #        SVSCommands.bboxVertices(), SVSCommands.scaleToStr(dims)));
        #svsCommands.append(String.format("add robot_view robot v %s p %f %f %f\n", 
        #        getViewRegionVertices(), VIEW_DIST/2 + .5, 0.0, VIEW_HEIGHT/2 - dims[2]/2));

        self.added = True
        self.update_pose = False

    def update_wm(self, svs_commands):
        if not self.added:
            return

        self.moving_state.update_wm()
        self.held_object.update_wm()

        if self.update_pose:
            for i in range(6):
                self.pose_wmes[i].set_value(self.pose[i])
                self.pose_wmes[i].update_wm()
            self.update_pose = False

    def remove_from_wm(self, svs_commands):
        if not self.added:
            return

        self.held_object.remove_from_wm()
        self.arm_id = None

        for wme in self.pose_wmes:
            wme.remove_from_wm()
        self.pose_id = None

        self.moving_state.remove_from_wm()
        self.self_id.DestroyWME()
        self.self_id = None

        #svsCommands.append(String.format("delete robot\n"));
        self.added = False
