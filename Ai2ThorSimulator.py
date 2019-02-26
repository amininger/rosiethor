import ai2thor.controller
import json

from threading import Lock, Thread
import traceback

from rosiethor.NavigationHelper import NavigationHelper
from rosiethor.MapUtil import MapUtil

from math import *

import time

INTERMEDIATE_ACTION_DELAY = 0.2

class Ai2ThorSimulator:
    def __init__(self):
        self.sim = None
        self.world = None
        self.listeners = set()
        self.lock = Lock()

    def start(self, scene_name="testing"):
        self.scene_name = scene_name

        self.sim = ai2thor.controller.Controller()
        self.sim.local_executable_path = "/home/aaron/sf/research/rosie-project/ai2thor/unity/ai2thor.x86_64"
        self.sim.start(player_screen_width=300, player_screen_height=300)

        self.nav = NavigationHelper(self.scene_name)

        self.shutdown = False
        #self.poll_thread = Thread(target = Ai2ThorSimulator.__poll_thread, args = (self, ) )
        #self.poll_thread.start()

        self.set_scene(scene_name)
        self.exec_command(dict(action='Teleport', x=-1.25, y=0.98, z=-2.0))
        self.exec_simple_command('RotateRight')
        self.exec_simple_command('LookDown')

    def stop(self):
        pass
        #self.shutdown = True
        #time.sleep(1.0)

    # Will get an updated world state every 500 ms
    def __poll_thread(self):
        while not self.shutdown:
            self.exec_simple_command("Poll")
            time.sleep(0.5)

    def set_scene(self, scene_name):
        self.lock.acquire()
        self.sim.reset(scene_name)
        self.world = self.sim.step(dict(action='Initialize', gridSize=0.25, screenWidth=800, screenHeight=600)).metadata
        self.lock.release()

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
            self.lock.acquire()
            self.world = self.sim.step(cmd).metadata
            for listener in self.listeners:
                listener(self.world)
            self.save()
            self.lock.release()

    def get_norm_dir_to_obj(self, obj):
        camPos = MapUtil.convert_pos(self.world["cameraPosition"])
        obj_xyzrpy = MapUtil.get_obj_xyzrpy(obj)
        dPos = [ obj_xyzrpy[d] - camPos[d] for d in range(3) ]
        dPosMag = sqrt(sum([ dPos[d] * dPos[d] for d in range(3) ]))
        return [ dPos[d] / dPosMag for d in range(3) ]


    def lookat_obj(self, obj_id):
        obj = next( (o for o in self.world["objects"] if o["objectId"] == obj_id), None)
        if not obj:
            print("ERROR: Ai2ThorSimulator::lookat_obj - " + obj_id + " doesn't exist")
            return False

        # Step 1: Rotate to face object
        while True:
            dPosNorm = self.get_norm_dir_to_obj(obj)
            rel_yaw = atan2(dPosNorm[1], dPosNorm[0]) - MapUtil.get_obj_yaw(self.world["agent"])
            if rel_yaw < 0:
                rel_yaw += 2 * pi

            time.sleep(INTERMEDIATE_ACTION_DELAY)
            
            if rel_yaw > pi * 0.25 and rel_yaw <= pi * 1.25:
                self.exec_simple_command("RotateLeft")
            elif rel_yaw > pi * 1.25 and rel_yaw < pi * 1.75:
                self.exec_simple_command("RotateRight")
            else:
                break

        # Step 2: Look up/down
        viewHorizon = round(self.world["agent"]["cameraHorizon"])
        while True:
            # Normalized direction vector to the object
            dPosNorm = self.get_norm_dir_to_obj(obj)

            # angle of camera rotation above/below straight forward
            viewAngle = self.world["agent"]["cameraHorizon"]
            viewAngle = (-viewAngle / 180 * pi)

            # The up vector for the robot (relative to viewing direction)
            robotYaw = MapUtil.get_obj_yaw(self.world["agent"])
            up = [ cos(robotYaw) * -sin(viewAngle), sin(robotYaw) * -sin(viewAngle), cos(viewAngle) ]

            dot = sum([ up[d] * dPosNorm[d] for d in range(3) ])

            time.sleep(INTERMEDIATE_ACTION_DELAY)
            if dot > sin(pi/10):
                self.exec_simple_command("LookUp")
            elif dot < sin(-pi/10):
                self.exec_simple_command("LookDown")

            newViewHorizon = round(self.world["agent"]["cameraHorizon"])
            if newViewHorizon == viewHorizon:
                break
            viewHorizon = newViewHorizon

        return True


    def approach_obj(self, obj_id):
        print("Approach: " + obj_id)
        obj = next( (o for o in self.world["objects"] if o["objectId"] == obj_id), None)
        if not obj:
            print("ERROR: Ai2ThorSimulator::approach_obj - " + obj_id + " doesn't exist")
            return False

        robot_xyzrpy = MapUtil.get_obj_xyzrpy(self.world["agent"])
        path = self.nav.find_path_to_obj(robot_xyzrpy, obj)

        if path == None:
            return False

        for step in path:
            time.sleep(INTERMEDIATE_ACTION_DELAY)
            if step == 'F':
                self.exec_simple_command("MoveAhead")
            elif step == 'R':
                self.exec_simple_command("RotateRight")
            elif step == 'L':
                self.exec_simple_command("RotateLeft")

        return self.lookat_obj(obj_id)


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


