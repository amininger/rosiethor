import sys

from threading import Thread
import time

import Python_sml_ClientInterface as sml

#from LanguageConnector import LanguageConnector
#from ActuationConnector import ActuationConnector
from PerceptionConnector import PerceptionConnector

from SoarUtil import SoarWME

current_time_ms = lambda: int(round(time.time() * 1000))

class AgentConfig:
    def __init__(self, config_file):
        # Read config file
        self.props = {}
        try:
            with open(config_file, 'r') as fin:
                for line in fin:
                    args = line.split()
                    if len(args) == 3 and args[1] == '=':
                        self.props[args[0]] = args[2]
        except EnvironmentError:
            pass

        # Set config values
        self.agent_name = self.props.get("agent-name", "rosie")
        self.agent_source = self.props.get("agent-source", None)
        self.smem_source = self.props.get("smem-source", None)

        self.messages_file = self.props.get("messages-file", None)

        self.verbose = self.props.get("verbose", "false") == "true"
        self.watch_level = int(self.props.get("watch-level", "1"))
        self.spawn_debugger = self.props.get("spawn-debugger", "false") == "true"
        self.write_to_stdout = self.props.get("write-to-stdout", "false") == "true"
        self.write_log = self.props.get("enable-log", "false") == "true"

class SoarAgent:
    def __init__(self, config, sim):
        self.config = config

        self.connected = False
        self.is_running = False
        self.queue_stop = False

        self.kernel = sml.Kernel.CreateKernelInNewThread()
        self.kernel.SetAutoCommit(False)

        self.start_time = current_time_ms()
        self.time_id = None
        self.seconds = SoarWME("seconds", 0)
        self.steps = SoarWME("steps", 0)

        self.agent = self.kernel.CreateAgent(self.config.agent_name)
        if self.config.spawn_debugger:
            success = self.agent.SpawnDebugger(self.kernel.GetListenerPort())

        self.run_event_callback_ids = []
        self.print_event_callback_id = -1
        self.init_agent_callback_id = -1

        if self.config.write_log:
            self.log_writer = open("rosie-log.txt", 'w')

        self.source_agent()
        self.agent.ExecuteCommandLine("w " + str(config.watch_level))

        self.connectors = {}
        #self.connectors["language"] = LanguageConnector(self)
        #self.connectors["actuation"] = ActuationConnector(self)
        self.connectors["perception"] = PerceptionConnector(self, sim)

        self.connect()

    def connect(self):
        if self.connected:
            return

        self.run_event_callback_ids.append(self.agent.RegisterForRunEvent(
            sml.smlEVENT_BEFORE_INPUT_PHASE, SoarAgent.run_event_handler, self))
        self.run_event_callback_ids.append(self.agent.RegisterForRunEvent(
            sml.smlEVENT_AFTER_INPUT_PHASE, SoarAgent.run_event_handler, self))
        self.run_event_callback_ids.append(self.agent.RegisterForRunEvent(
            sml.smlEVENT_AFTER_OUTPUT_PHASE, SoarAgent.run_event_handler, self))

        self.print_event_callback_id = self.agent.RegisterForPrintEvent(
                sml.smlEVENT_PRINT, SoarAgent.print_event_handler, self)

        self.init_agent_callback_id = self.kernel.RegisterForAgentEvent(
                sml.smlEVENT_BEFORE_AGENT_REINITIALIZED, SoarAgent.init_agent_handler, self)

        for connector in self.connectors.values():
            connector.connect()

        self.connected = True

    def disconnect(self):
        if not self.connected:
            return

        for callback_id in self.run_event_callback_ids:
            self.agent.UnregisterForRunEvent(callback_id)
        self.run_event_callback_ids = []

        if self.print_event_callback_id != -1:
            self.agent.UnregisterForPrintEvent(self.print_event_callback_id)
            self.print_event_callback_id = -1

        self.kernel.UnregisterForAgentEvent(self.init_agent_callback_id)
        self.init_agent_callback_id = -1

        for connector in self.connectors.values():
            connector.disconnect()

        self.connected = False

    def source_agent(self):
        self.agent.ExecuteCommandLine("smem --set database memory")
        self.agent.ExecuteCommandLine("epmem --set database memory")

        if self.config.smem_source != None:
            print "------------- SOURCING SMEM ---------------" 
            result = self.agent.ExecuteCommandLine("source " + self.config.smem_source)
            if self.config.verbose:
                print result 

        if self.config.agent_source != None:
            print "--------- SOURCING PRODUCTIONS ------------" 
            result = self.agent.ExecuteCommandLine("source " + self.config.agent_source)
            if self.config.verbose:
                print result 
        else:
            print "WARNING! agent-source not set in config file, not sourcing any rules" 


    def start(self):
        if self.is_running:
            return

        self.is_running = True
        thread = Thread(target = SoarAgent.run_thread, args = (self, ))
        thread.start()

    def run_thread(self):
        self.agent.ExecuteCommandLine("run")
        self.is_running = False

    def stop(self):
        self.queue_stop = True

    def kill(self):
        # Wait for running thread to finish
        self.queue_stop = True
        while self.is_running:
            time.sleep(0.01)

        self.disconnect()
        if self.config.write_log:
            self.log_writer.close()

        if self.config.spawn_debugger:
            self.agent.KillDebugger()

        self.kernel.DestroyAgent(self.agent)
        self.agent = None

        self.kernel.Shutdown()

    def execute_command(self, cmd):
        print cmd 
        print self.agent.ExecuteCommandLine(cmd)  + "\n"

    @staticmethod
    def init_agent_handler(eventID, self, info):
        try:
            for connector in self.connectors.values():
                connector.on_init_soar()
            self.seconds.remove_from_wm()
            self.steps.remove_from_wm()
            self.time_id.DestroyWME()
            self.time_id = None
        except:
            print "ERROR IN INIT AGENT" 


    @staticmethod
    def run_event_handler(eventID, self, agent, phase):
       # try:
        if eventID == sml.smlEVENT_BEFORE_INPUT_PHASE:
            if self.queue_stop:
                agent.StopSelf()
                self.queue_stop = False

            # Timing Info
            if self.time_id == None:
                self.start_time = current_time_ms()
                self.time_id = self.agent.GetInputLink().CreateIdWME("time")
                self.seconds.set_value(0)
                self.seconds.add_to_wm(self.time_id)
                self.steps.set_value(0)
                self.steps.add_to_wm(self.time_id)
            else:
                self.seconds.set_value(int((current_time_ms() - self.start_time)/1000))
                self.seconds.update_wm()
                self.steps.set_value(self.steps.val + 1)
                self.steps.update_wm()

            for connector in self.connectors.values():
                connector.on_input_phase(self.agent.GetInputLink())

        elif eventID == sml.smlEVENT_AFTER_INPUT_PHASE or \
                eventID == sml.smlEVENT_AFTER_OUTPUT_PHASE:
            if agent.IsCommitRequired():
                agent.Commit()
       # except:
       #     e = sys.exc_info()
       #     print "ERROR IN RUN HANDLER" 
       #     print str(e[0])
       #     print str(e[1])
       #     print str(e[2])

    @staticmethod
    def print_event_handler(eventID, self, agent, message):
        try:
            print message 
            if self.config.write_log:
                self.log_writer.write(message)
        except:
            print "ERROR IN PRINT HANDLER" 


