import sys
import traceback

from string import digits
from pysoarlib import *

class CommandSyntaxError(Exception):
    pass

class ActuationConnector(AgentConnector):
    def __init__(self, agent, sim):
        AgentConnector.__init__(self, agent)
        self.register_output_handler("perform-action")
        self.sim = sim

    def on_init_soar(self):
        pass

    def on_input_phase(self, input_link):
        pass

    def on_output_event(self, att_name, root_id):
        if att_name == "perform-action":
            self.process_perform_action(root_id)

    def process_perform_action(self, root_id):
        try:
            action_name = root_id.GetChildString("name")
            if action_name == None:
                raise CommandSyntaxError("No ^name attribute")

            command = None
            if action_name == "turn":
                command = self.process_turn_command(root_id)

            if command == None:
                raise CommandSyntaxError("Unrecognized Action")

            self.sim.exec_command(command)
            root_id.CreateStringWME("status", "success")
        except CommandSyntaxError as e: 
            root_id.CreateStringWME("status", "error")
            root_id.CreateStringWME("error-info", str(e))
        except Exception as e:
            self.print_handler(traceback.format_exc())
            root_id.CreateStringWME("status", "error")
            root_id.CreateStringWME("error-info", "runtime error")

    def process_turn_command(self, root_id):
        direction = root_id.GetChildString("direction")
        if direction == None:
            raise CommandSyntaxError("turn is missing ^direction")
        if direction == "right1":
            return { "action":"RotateRight" }
        if direction == "left1":
            return { "action":"RotateLeft" }
        return CommandSyntaxError("turn given unrecognized direction")


