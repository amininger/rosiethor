import sys

from string import digits
from pysoarlib import *

from .WorldObjectManager import WorldObjectManager

from threading import Lock

import time
current_time_ms = lambda: int(round(time.time() * 1000))

class PerceptionConnector(AgentConnector):
    # TODO: Implement eye position?
    def __init__(self, agent, sim):
        AgentConnector.__init__(self, agent)
        self.add_output_command("modify-scene")
        self.objects = WorldObjectManager()
        self.wm_dirty = False
        self.sim = sim
        self.sim.add_world_change_listener(lambda world: self.handle_world_change(world))
        self.lock = Lock()
        self.last_poll_time = current_time_ms()

    def on_input_phase(self, input_link):
        svs_commands = []
        if not self.objects.is_added():
            self.lock.acquire()
            self.objects.add_to_wm(input_link, svs_commands)
            self.lock.release()
        elif self.wm_dirty or self.objects.wm_dirty:
            self.lock.acquire()
            self.objects.update_wm(svs_commands)
            self.wm_dirty = False
            self.lock.release()
        if len(svs_commands) > 0:
            self.agent.agent.SendSVSInput("\n".join(svs_commands))

        cur_time = current_time_ms()
        if cur_time - self.last_poll_time > 500:
            self.sim.exec_simple_command("Poll")
            self.last_poll_time = cur_time
            #mic = next( (o for o in self.sim.world["objects"] if o["objectType"] == "Microwave") )
            #self.print_handler(str(mic))
            ##self.print_handler("Microwave: On=" + str(mic["isactivate"]) + " Time=" + str(mic["timeleft"]))
            #mug = next( (o for o in self.sim.world["objects"] if o["objectType"] == "Mug"), None )
            #if mug:
            #    self.print_handler(str(mug))
            #    #self.print_handler("Mug: Temperature=" + str(mug["temperature"]))


    def handle_world_change(self, world):
        self.lock.acquire()
        self.objects.update(world)
        self.wm_dirty = True
        self.lock.release()

    def on_init_soar(self):
        svs_commands = []
        self.lock.acquire()
        self.objects.remove_from_wm(svs_commands)
        self.lock.release()
        if len(svs_commands) > 0:
            self.agent.agent.SendSVSInput("\n".join(svs_commands))


    def on_output_event(self, command_name, root_id):
        if command_name == "modify-scene":
            self.process_modify_scene_command(root_id)
    
    def process_modify_scene_command(self, root_id):
        error = False
        mod_type = root_id.GetChildString("type")
        if mod_type == "link":
            src_handle = root_id.GetChildString("source-handle")
            dest_handle = root_id.GetChildString("destination-handle")
            if src_handle == None:
                error = True
                self.print_handler("!!! PerceptionConnector::process_modify_scene_command[link]\n  No ^source-handle")
            elif dest_handle == None:
                error = True
                self.print_handler("!!! PerceptionConnector::process_modify_scene_command[link]\n  No ^destination-handle")
            else:
                self.lock.acquire()
                self.objects.link_objects(src_handle, dest_handle)
                self.lock.release()
        else:
            error = True
            self.print_handler("!!! PerceptionConnector::process_modify_scene_command\n  Bad ^type")

        root_id.CreateStringWME("status", "error" if error else "complete")
