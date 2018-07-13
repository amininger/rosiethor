import sys

from threading import Thread
import time

import Python_sml_ClientInterface as sml

from pysoarlib import SoarAgent, LanguageConnector

from .PerceptionConnector import PerceptionConnector
from .RobotConnector import RobotConnector

class RosieThorAgent(SoarAgent):
    def __init__(self, sim, config_filename=None, **kwargs):
        SoarAgent.__init__(self, config_filename=config_filename, **kwargs)

        self.connectors["language"] = LanguageConnector(self)
        self.connectors["robot"] = RobotConnector(self, sim)
        self.connectors["perception"] = PerceptionConnector(self, sim)

