import ai2thor.controller
import json

from threading import Lock
import traceback

from .NavigationHelper import NavigationHelper
from .MapUtil import MapUtil

import time

class Ai2ThorSimulator:
    def __init__(self):
        self.sim = None
        self.world = None
        self.lock = Lock()
        self.listeners = set()
        self.nav = NavigationHelper("testing")

    def start(self):
        self.sim = ai2thor.controller.Controller()
        self.sim.local_executable_path = "/home/aaron/sf/research/rosie-project/ai2thor/unity/ai2thor.x86_64"
        self.sim.start()
        self.sim.reset('testing')

        self.world = self.sim.step(dict(action='Initialize', gridSize=0.25, screenWidth=800, screenHeight=600)).metadata
        self.world = self.sim.step(dict(action='Teleport', x=-1.25, y=0.98, z=-2.0)).metadata
        self.world = self.sim.step(dict(action='RotateRight')).metadata
        #self.world = self.sim.step(dict(action='RotateRight')).metadata
        #self.world = self.sim.step(dict(action='LookDown')).metadata

        self.save()


    def set_scene(self, scene_name):
        self.sim.reset(scene_name)
        self.world = self.sim.step(dict(action='Initialize', gridSize=0.25, screenWidth=800, screenHeight=600)).metadata

    def save(self):
        world_info = json.dumps(self.world)
        with open("world.json", "w") as f:
            f.write(world_info)

    def load(self):
        with open("world.json", "r") as f:
            world_info = f.read()
            self.world = json.loads(world_info)

    def add_world_change_listener(self, listener):
        self.listeners.add(listener)

    def exec_simple_command(self, cmd):
        self.exec_command(dict(action=cmd))

    def exec_command(self, cmd):
        if self.sim:
            #self.lock.acquire()
            self.world = self.sim.step(cmd).metadata
            for listener in self.listeners:
                listener(self.world)
            #self.lock.release()

    def approach_obj(self, obj_id):
        if not self.sim:
            return False

        print("Approach: " + obj_id)
        obj = next( (o for o in self.world["objects"] if o["objectId"] == obj_id), None)
        if not obj:
            print("ERROR: Ai2ThorSimulator::approach_obj - " + obj_id + " doesn't exist")
            return False

        robot_xyzrpy = MapUtil.get_obj_xyzrpy(self.world["agent"])
        path = self.nav.find_path_to_obj(robot_xyzrpy, obj)

        if not path:
            return False

        for step in path:
            time.sleep(0.2)
            if step == 'F':
                self.exec_simple_command("MoveAhead")
            elif step == 'R':
                self.exec_simple_command("RotateRight")
            elif step == 'L':
                self.exec_simple_command("RotateLeft")
        return True


#
#            rot = agent["rotation"]
#            rot = ( rot["x"] * DEG_TO_RAD, rot["y"] * DEG_TO_RAD, rot["z"] * DEG_TO_RAD )
#            phi = -agent["cameraHorizon"] * DEG_TO_RAD
#
#            lookat = ( sin(rot[1]) * cos(phi), sin(phi), cos(rot[1]) * cos(phi) )
#
#            objs = []
#            for obj in e.metadata["objects"]:
#                if obj["visible"]:
#                    objs.append(obj["objectId"])
#                #obj_pos = obj["position"]
#                #obj_pos = ( obj_pos["x"], obj_pos["y"], obj_pos["z"] )
#
#                #to_obj = ( obj_pos[0] - pos[0], obj_pos[1] - pos[1], obj_pos[2] - pos[2] )
#                #dot_prod = lookat[0] * to_obj[0] + lookat[1] * to_obj[1] + lookat[2] * to_obj[2]
#                #if obj["visible"] and dot_prod > 1:
#                #    objs.append("VIS: " + obj["objectId"])
#                #elif not obj["visible"] and dot_prod > 0 and dot_prod <= 1:
#                #    objs.append("DOT: " + obj["objectId"])
#
#            objs.sort()
#
#            self.text.configure(state="normal")
#            self.text.delete(1.0, END)
#
#
#            self.text.insert(END, "LOOK: " + str(lookat) + "\n")
#            for obj in objs:
#                self.text.insert(END, obj + "\n")
#            self.text.configure(state="disabled")
#        else:
#            print cmd


