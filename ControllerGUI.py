from __future__ import print_function

from tkinter import *

class ControllerGUI(Toplevel):
    def create_buttons(self):
        turn_left = Button(self, text="L")
        turn_left["command"] = lambda : self.sim_robot.exec_simple_command("RotateLeft")
        self.buttons.append(turn_left)

        forward = Button(self, text="/\\")
        forward["command"] = lambda : self.sim_robot.exec_simple_command("MoveAhead")
        self.buttons.append(forward)

        turn_right = Button(self, text="R")
        turn_right["command"] = lambda : self.sim_robot.exec_simple_command("RotateRight")
        self.buttons.append(turn_right)

        look_up = Button(self, text="U")
        look_up["command"] = lambda : self.sim_robot.exec_simple_command("LookUp")
        self.buttons.append(look_up)

        left = Button(self, text="<")
        left["command"] = lambda : self.sim_robot.exec_simple_command("MoveLeft")
        self.buttons.append(left)

        backward = Button(self, text="\\/")
        backward["command"] = lambda : self.sim_robot.exec_simple_command("MoveBack")
        self.buttons.append(backward)

        right = Button(self, text=">")
        right["command"] = lambda : self.sim_robot.exec_simple_command("MoveRight")
        self.buttons.append(right)

        look_down = Button(self, text="D")
        look_down["command"] = lambda : self.sim_robot.exec_simple_command("LookDown")
        self.buttons.append(look_down)

        open_door = Button(self, text="Open")
        open_door["command"] = lambda : self.open_command()
        self.buttons.append(open_door)

        close_door = Button(self, text="Close")
        close_door["command"] = lambda : self.close_command()
        self.buttons.append(close_door)

        grab = Button(self, text="Grab")
        grab["command"] = lambda : self.grab_command()
        self.buttons.append(grab)

        put = Button(self, text="Put")
        put["command"] = lambda : self.put_command()
        self.buttons.append(put)

        for i in range(len(self.buttons)):
            self.buttons[i].grid(row=int(i/4), column=i%4, sticky=N+S+E+W)

    def create_menu(self):
        self.menu_label_var = StringVar()
        self.menu_label = Label(self, textvariable=self.menu_label_var)
        self.menu_label.grid(row=3, columnspan=4, sticky=W+E)

        self.menu_buttons = []

    def show_menu(self, name, options):
        if len(options) == 0:
            return
        self.menu_label_var.set(name)
        for opt in options:
            self.menu_buttons.append(Button(self, text=opt, command=lambda opt=opt: self.on_menu_select(opt, name)))
        for r, btn in enumerate(self.menu_buttons):
            btn.grid(row=4+r, columnspan=4, sticky=W+E)

    def hide_menu(self):
        for btn in self.menu_buttons:
            btn.destroy()
        self.menu_buttons = []

    def on_menu_select(self, opt, cmd_name):
        self.hide_menu()
        self.handle_command(cmd_name, opt)

    def handle_command(self, cmd_name, obj_id):
        if cmd_name == "OPEN":
            self.sim_robot.exec_command(dict(action="OpenObject", objectId=obj_id))
        elif cmd_name == "CLOSE":
            self.sim_robot.exec_command(dict(action="CloseObject", objectId=obj_id))
        elif cmd_name == "GRAB":
            self.sim_robot.exec_command(dict(action="PickupObject", objectId=obj_id))
        elif cmd_name == "PUT":
            held_id = str(self.sim_robot.world["inventoryObjects"][0]["objectId"])
            self.sim_robot.exec_command(dict(action="PutObject", objectId=held_id, receptacleObjectId=obj_id))

    def open_command(self):
        obj_ids = [ str(obj["objectId"]) for obj in self.sim_robot.world["objects"] 
                if (obj["visible"] and obj["openable"] and not obj["isopen"]) ]
        self.show_menu("OPEN", obj_ids)

    def close_command(self):
        obj_ids = [ str(obj["objectId"]) for obj in self.sim_robot.world["objects"] 
                if (obj["visible"] and obj["openable"] and obj["isopen"]) ]
        self.show_menu("CLOSE", obj_ids)

    def grab_command(self):
        if len(self.sim_robot.world["inventoryObjects"]) > 0:
            return
        obj_ids = [ str(obj["objectId"]) for obj in self.sim_robot.world["objects"] 
                if (obj["visible"] and obj["pickupable"]) ]
        self.show_menu("GRAB", obj_ids)

    def put_command(self):
        if len(self.sim_robot.world["inventoryObjects"]) == 0:
            return
        obj_ids = [ str(obj["objectId"]) for obj in self.sim_robot.world["objects"] 
                if (obj["visible"] and obj["receptacle"] and len(obj["receptacleObjectIds"]) < int(obj["receptacleCount"])) ]
        self.show_menu("PUT", obj_ids)

    def bind_keys(self):
        self.bind("q", lambda e : self.sim_robot.exec_simple_command("RotateLeft"))
        self.bind("w", lambda e : self.sim_robot.exec_simple_command("MoveAhead"))
        self.bind("e", lambda e : self.sim_robot.exec_simple_command("RotateRight"))
        self.bind("a", lambda e : self.sim_robot.exec_simple_command("MoveLeft"))
        self.bind("s", lambda e : self.sim_robot.exec_simple_command("MoveBack"))
        self.bind("d", lambda e : self.sim_robot.exec_simple_command("MoveRight"))
        self.bind("r", lambda e : self.sim_robot.exec_simple_command("LookUp"))
        self.bind("f", lambda e : self.sim_robot.exec_simple_command("LookDown"))

    def __init__(self, sim_robot, master=None):
        Toplevel.__init__(self, master)
        for r in range(3):
            self.rowconfigure(r, weight=2, minsize=50)
        self.rowconfigure(3, weight=1, minsize=30)
        for c in range(4):
            self.columnconfigure(c, weight=1, minsize=50)
        self.sim_robot = sim_robot
        self.buttons = []
        self.create_buttons()
        self.create_menu()
        self.bind_keys()
