import sys

from threading import Thread
import time

import Python_sml_ClientInterface as sml

from pysoarlib import SoarAgent, LanguageConnector

#from ActuationConnector import ActuationConnector
from PerceptionConnector import PerceptionConnector

class RosieThorAgent(SoarAgent):
    def __init__(self, config_file, sim):
        SoarAgent.__init__(self, config_file)

        self.connectors["language"] = LanguageConnector(self)
        #self.connectors["actuation"] = RosieThorActuationConnector(self)
        self.connectors["perception"] = PerceptionConnector(self, sim)

