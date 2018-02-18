import sys
import vim

from string import digits

from VimWriter import VimWriter


def task_to_string(task_id):
    handle_wme = task_id.FindByAttribute("action-handle", 0)
    arg1_wme = task_id.FindByAttribute("arg1", 0)
    arg2_wme = task_id.FindByAttribute("arg2", 0)

    task = handle_wme.GetValueAsString() + "("
    if arg1_wme != None:
        task += task_arg_to_string(arg1_wme.ConvertToIdentifier())
    if arg2_wme != None:
        if arg1_wme != None:
            task += ", "
        task += task_arg_to_string(arg2_wme.ConvertToIdentifier())
    task += ")"

    return task

def task_arg_to_string(arg_id):
    arg_type = arg_id.FindByAttribute("arg-type", 0).GetValueAsString()
    if arg_type == "object":
        id_wme = arg_id.FindByAttribute("id", 0)
        return obj_arg_to_string(id_wme.ConvertToIdentifier())
    elif arg_type == "predicate":
        handle_str = arg_id.FindByAttribute("handle", 0).GetValueAsString()
        obj2_str = obj_arg_to_string(arg_id.FindByAttribute("2", 0).ConvertToIdentifier())
        return "%s(%s)" % ( handle_str, obj2_str )
    elif arg_type == "waypoint":
        wp_id = arg_id.FindByAttribute("id", 0).ConvertToIdentifier()
        return wp_id.FindByAttribute("handle", 0).GetValueAsString()
    return "?"

def obj_arg_to_string(obj_id):
    pred_order = [ ["size"], ["color"], ["name", "shape", "category"] ]
    preds_id = obj_id.FindByAttribute("predicates", 0).ConvertToIdentifier()
    obj_desc = ""
    for pred_list in pred_order:
        for pred in pred_list:
            pred_wme = preds_id.FindByAttribute(pred, 0)
            if pred_wme != None:
                obj_desc += pred_wme.GetValueAsString() + " "
                break
    if len(obj_desc) > 0:
        obj_desc = obj_desc[:-1]

    return obj_desc.translate(None, digits)

class ActuationConnector:
    def __init__(self, agent):
        self.agent = agent
        self.connected = False
        self.output_handler_ids = { "started-action": -1, "completed-action": -1 }

    def connect(self):
        if self.connected:
            return

        for command_name in self.output_handler_ids:
            self.output_handler_ids[command_name] = self.agent.agent.AddOutputHandler(
                    command_name, ActuationConnector.output_event_handler, self)

        self.connected = True

    def disconnect(self):
        if not self.connected:
            return

        for command_name in self.output_handler_ids:
            self.agent.agent.RemoveOutputHandler(self.output_handler_ids[command_name])
            self.output_handler_ids[command_name] = -1

        self.connected = False

    def on_init_soar(self):
        pass

    def on_input_phase(self, input_link):
        pass

    @staticmethod
    def output_event_handler(self, agent_name, att_name, wme):
        try:
            if wme.IsJustAdded() and wme.IsIdentifier():
                root_id = wme.ConvertToIdentifier()
                self.on_output_event(att_name, root_id)
        except:
            print "ERROR IN OUTPUT EVENT HANDLER"
            print sys.exc_info()

    def on_output_event(self, att_name, root_id):
        if att_name == "started-action":
            self.process_started_action(root_id)
        elif att_name == "completed-action":
            self.process_completed_action(root_id)

    def process_started_action(self, root_id):
        try:
            task_id = root_id.FindByAttribute("execution-operator", 0).ConvertToIdentifier()
            padding = "  " * (int(root_id.FindByAttribute("depth", 0).GetValueAsString()) - 1)
            self.agent.writer.write(padding + ">" + task_to_string(task_id), VimWriter.ACTIONS_WIN)
        except:
            self.agent.writer.write("Error Parsing Started Action", VimWriter.ACTIONS_WIN)
        root_id.CreateStringWME("handled", "true")

    def process_completed_action(self, root_id):
        try:
            task_id = root_id.FindByAttribute("execution-operator", 0).ConvertToIdentifier()
            padding = "  " * (int(root_id.FindByAttribute("depth", 0).GetValueAsString()) - 1)
            self.agent.writer.write(padding + "<" + task_to_string(task_id), VimWriter.ACTIONS_WIN)
        except:
            self.agent.writer.write("Error Parsing Completed Action", VimWriter.ACTIONS_WIN)
        root_id.CreateStringWME("handled", "true")
