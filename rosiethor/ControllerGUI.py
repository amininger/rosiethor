from Tkinter import *

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

        for i in range(len(self.buttons)):
            self.buttons[i].grid(row=int(i/4), column=i%4, sticky=N+S+E+W)

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
        for r in range(2):
            self.rowconfigure(r, weight=1, minsize=50)
        for c in range(4):
            self.columnconfigure(c, weight=1, minsize=50)
        self.sim_robot = sim_robot
        self.buttons = []
        self.create_buttons()
        self.bind_keys()
