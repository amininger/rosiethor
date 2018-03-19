import sys

from string import digits
from pysoarlib import *

from WorldObjectManager import WorldObjectManager

class PerceptionConnector(AgentConnector):
    # TODO: Implement eye position?
    # TODO: Implement robot self
    def __init__(self, agent, sim):
        AgentConnector.__init__(self, agent)
        self.register_output_handler("modify-scene")
        self.sim = sim
        self.world = WorldObjectManager()

    def on_input_phase(self, input_link):
        self.world.update_objects(self.sim.world)
        svs_commands = []
        if not self.world.is_added():
            self.world.add_to_wm(input_link, svs_commands)
        elif self.sim.changed:
            self.world.update_objects(self.sim.world)
            self.sim.changed = False
            self.world.update_wm(svs_commands)
        if len(svs_commands) > 0:
            self.agent.agent.SendSVSInput("\n".join(svs_commands))

    def on_init_soar(self):
        svs_commands = []
        self.world.remove_from_wm(svs_commands)
        if len(svs_commands) > 0:
            self.agent.agent.SendSVSInput("\n".join(svs_commands))

    def on_output_event(self, att_name, root_id):
        if att_name == "modify-scene":
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
                self.world.link_objects(src_handle, dest_handle)
        else:
            error = True
            self.print_handler("!!! PerceptionConnector::process_modify_scene_command\n  Bad ^type")

        root_id.CreateStringWME("status", "error" if error else "complete")
