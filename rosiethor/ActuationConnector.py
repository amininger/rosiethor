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
            elif action_name == "drive-forward":
                command = self.process_drive_forward_command(root_id)
            elif action_name == "look":
                command = self.process_look_command(root_id)
            elif action_name == "pick-up":
                command = self.process_pickup_command(root_id)
            elif action_name == "put-down":
                command = self.process_putdown_command(root_id)
            elif action_name == "open":
                command = self.process_open_command(root_id)
            elif action_name == "close":
                command = self.process_close_command(root_id)
            else:
                raise CommandSyntaxError("Unrecognized Action " + action_name)

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
        raise CommandSyntaxError("turn given unrecognized direction")

    def process_drive_forward_command(self, root_id):
        return { "action": "MoveAhead" }

    def process_look_command(self, root_id):
        direction = root_id.GetChildString("direction")
        if direction == None:
            raise CommandSyntaxError("look is missing ^direction")
        if direction == "up1":
            return { "action":"LookUp" }
        if direction == "down1":
            return { "action":"LookDown" }
        raise CommandSyntaxError("look given unrecognized direction")

    def process_pickup_command(root_id):
        obj_handle = root_id.GetChildString("object")
        if obj_handle == None:
            raise CommandSyntaxError("pick-up is missing ^object")

        world_obj = self.agent.connectors["perception"].world.get_object(obj_handle)
        if world_obj == None:
            raise CommandSyntaxError("pick-up given unrecognized object " + obj_handle)

        return { "action": "PickupObject", 
                "objectId": world_obj.get_perception_id() }

    def process_putdown_command(root_id):
        obj_handle = root_id.GetChildString("object")
        if obj_handle == None:
            raise CommandSyntaxError("put-down is missing ^object")

        world_obj = self.agent.connectors["perception"].world.get_object(obj_handle)
        if world_obj == None:
            raise CommandSyntaxError("put-down given unrecognized object " + obj_handle)

        rec_handle = root_id.GetChildString("receptacle")
        if rec_handle == None:
            raise CommandSyntaxError("put-down is missing ^receptacle")

        world_rec = self.agent.connectors["perception"].world.get_object(rec_handle)
        if world_rec == None:
            raise CommandSyntaxError("put-down given unrecognized receptacle " + rec_handle)

        return { "action": "PutObject", 
                "objectId": world_obj.get_perception_id(), 
                "receptacleObjectId": world_rec.get_perception_id() }

    def process_open_command(root_id):
        obj_handle = root_id.GetChildString("object")
        if obj_handle == None:
            raise CommandSyntaxError("open is missing ^object")

        world_obj = self.agent.connectors["perception"].world.get_object(obj_handle)
        if world_obj == None:
            raise CommandSyntaxError("open given unrecognized object " + obj_handle)

        return { "action": "OpenObject", 
                "objectId": world_obj.get_perception_id() }

    def process_close_command(root_id):
        obj_handle = root_id.GetChildString("object")
        if obj_handle == None:
            raise CommandSyntaxError("close is missing ^object")

        world_obj = self.agent.connectors["perception"].world.get_object(obj_handle)
        if world_obj == None:
            raise CommandSyntaxError("close given unrecognized object " + obj_handle)

        return { "action": "CloseObject", 
                "objectId": world_obj.get_perception_id() }
