from tkinter import *
import tkinter.font

import sys

from Ai2ThorSimulator import Ai2ThorSimulator
from ControllerGUI import ControllerGUI

sim = Ai2ThorSimulator()
sim.start()

root = Tk()
controller_gui = ControllerGUI(sim, master=root)
root.mainloop()
