import ai2thor.controller
import json

from threading import Lock
import traceback

class Ai2ThorSimulator:
    def __init__(self):
        self.sim = None
        self.world = None
        self.changed = False
        self.lock = Lock()

    def start(self):
        self.sim = ai2thor.controller.Controller()
        self.sim.start()
        self.sim.reset('FloorPlan28')

        self.world = self.sim.step(dict(action='Initialize', gridSize=0.25)).metadata
        self.world = self.sim.step(dict(action='Teleport', x=-1.5, y=0.98, z=-3.0)).metadata
        self.world = self.sim.step(dict(action='RotateRight')).metadata
        self.world = self.sim.step(dict(action='RotateRight')).metadata
        self.world = self.sim.step(dict(action='LookDown')).metadata


    def save(self):
        world_info = json.dumps(self.world)
        with open("world.json", "w") as f:
            f.write(world_info)

    def load(self):
        with open("world.json", "r") as f:
            world_info = f.read()
            self.world = json.loads(world_info)

    def exec_simple_command(self, cmd):
        return self.exec_command(dict(action=cmd))

    def exec_command(self, cmd):
        if self.sim:
            #self.lock.acquire()
            self.world = self.sim.step(cmd).metadata
            self.changed = True
            #self.lock.release()

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

