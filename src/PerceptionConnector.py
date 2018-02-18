import sys

from string import digits
from soarutil import *

from WorldObjectManager import WorldObjectManager

class PerceptionConnector(AgentConnector):
    # TODO: Implement eye position?
    def __init__(self, agent, sim):
        super(PerceptionConnector, self).__init__(agent)
        self.output_handler_ids["modify-scene"] = -1
        self.sim = sim
        self.world = WorldObjectManager()

    def on_input_phase(self, input_link):
        self.world.update_objects(self.sim.world)
        svs_commands = ""
        if not self.world.is_added():
            self.world.add_to_wm(input_link, svs_commands)
        else:
            self.world.update_wm(svs_commands)
        if len(svs_commands) > 0:
            self.agent.SendSVSCommands(svs_commands)

    def on_init_soar(self):
        svs_commands = ""
        self.world.remove_from_wm(svs_commands)
        if len(svs_commands) > 0:
            self.agent.SendSVSCommands(svs_commands)

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
                print "!!! PerceptionConnector::process_modify_scene_command[link]\n  No ^source-handle"
            elif dest_handle == None:
                error = True
                print "!!! PerceptionConnector::process_modify_scene_command[link]\n  No ^destination-handle"
            else:
                self.world.link_objects(src_handle, dest_handle)
        else:
            error = True
            print "!!! PerceptionConnector::process_modify_scene_command\n  Bad ^type"

        root_id.CreateStringWME("status", "error" if error else "complete")
