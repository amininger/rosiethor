#import os
#
#from SoarAgent import SoarAgent, AgentConfig
#from Ai2ThorSimulator import Ai2ThorSimulator
#
#sim = Ai2ThorSimulator()
#sim.load()
#
#agent_config = AgentConfig(os.environ['ROSIE_HOME'] + "/test-agents/ai2thor/agent/rosie.ai2thor.config")
#
#soar_agent = SoarAgent(agent_config, sim)
#soar_agent.connect()
#soar_agent.execute_command("step")
#soar_agent.execute_command("step")
#
#soar_agent.execute_command("p i1 -d 10")
#

import ai2thor.controller

from Tkinter import *
from math import *

DEG_TO_RAD = pi / 180.0

class Application(Frame):
    def exec_command(self, cmd):
        if self.sim:
            e = self.sim.step(dict(action=cmd))

            agent = e.metadata["agent"]
            pos = agent["position"]
            pos = ( pos["x"], pos["y"], pos["z"] )
            rot = agent["rotation"]
            rot = ( rot["x"] * DEG_TO_RAD, rot["y"] * DEG_TO_RAD, rot["z"] * DEG_TO_RAD )
            phi = -agent["cameraHorizon"] * DEG_TO_RAD

            lookat = ( sin(rot[1]) * cos(phi), sin(phi), cos(rot[1]) * cos(phi) )

            objs = []
            for obj in e.metadata["objects"]:
                if obj["visible"]:
                    objs.append(obj["objectId"])
                #obj_pos = obj["position"]
                #obj_pos = ( obj_pos["x"], obj_pos["y"], obj_pos["z"] )

                #to_obj = ( obj_pos[0] - pos[0], obj_pos[1] - pos[1], obj_pos[2] - pos[2] )
                #dot_prod = lookat[0] * to_obj[0] + lookat[1] * to_obj[1] + lookat[2] * to_obj[2]
                #if obj["visible"] and dot_prod > 1:
                #    objs.append("VIS: " + obj["objectId"])
                #elif not obj["visible"] and dot_prod > 0 and dot_prod <= 1:
                #    objs.append("DOT: " + obj["objectId"])

            objs.sort()

            self.text.configure(state="normal")
            self.text.delete(1.0, END)


            self.text.insert(END, "LOOK: " + str(lookat) + "\n")
            for obj in objs:
                self.text.insert(END, obj + "\n")
            self.text.configure(state="disabled")
        else:
            print cmd

    def create_widgets(self):
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.text = Text(self, yscrollcommand=self.scrollbar.set, state="disabled")
        self.text.pack(side=LEFT, fill=BOTH)

    def add_directional_buttons(self):
        turn_left = Button(self, text="(")
        turn_left["command"] = lambda : self.exec_command("RotateLeft")
        self.buttons.append(turn_left)

        forward = Button(self, text="^")
        forward["command"] = lambda : self.exec_command("MoveAhead")
        self.buttons.append(forward)

        turn_right = Button(self, text=")")
        turn_right["command"] = lambda : self.exec_command("RotateRight")
        self.buttons.append(turn_right)

        left = Button(self, text="<")
        left["command"] = lambda : self.exec_command("MoveLeft")
        self.buttons.append(left)

        backward = Button(self, text="v")
        backward["command"] = lambda : self.exec_command("MoveBack")
        self.buttons.append(backward)

        right = Button(self, text=">")
        right["command"] = lambda : self.exec_command("MoveRight")
        self.buttons.append(right)

        for i in range(len(self.buttons)):
            self.buttons[i].grid(row=int(i/3), column=i%3)

    def bind_keys(self):
        self.master.bind("q", lambda e : self.exec_command("RotateLeft"))
        self.master.bind("w", lambda e : self.exec_command("MoveAhead"))
        self.master.bind("e", lambda e : self.exec_command("RotateRight"))
        self.master.bind("a", lambda e : self.exec_command("MoveLeft"))
        self.master.bind("s", lambda e : self.exec_command("MoveBack"))
        self.master.bind("d", lambda e : self.exec_command("MoveRight"))
        self.master.bind("r", lambda e : self.exec_command("LookUp"))
        self.master.bind("f", lambda e : self.exec_command("LookDown"))

    def start_simulator(self):
        self.sim = ai2thor.controller.Controller()
        self.sim.start()
        self.sim.reset('FloorPlan28')
        self.sim.step(dict(action='Initialize', gridSize=0.25)).metadata

    def __init__(self, master=None):
        Frame.__init__(self, master, width=800, height=600)
        self.buttons = []
        self.sim = None
        self.start_simulator()
        self.create_widgets()
        self.bind_keys()
        self.pack()

root = Tk()
app = Application(master=root)
app.mainloop()
