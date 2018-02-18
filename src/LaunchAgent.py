import os

from SoarAgent import SoarAgent, AgentConfig
from Ai2ThorSimulator import Ai2ThorSimulator

sim = Ai2ThorSimulator()
sim.load()

agent_config = AgentConfig(os.environ['ROSIE_HOME'] + "/test-agents/ai2thor/agent/rosie.ai2thor.config")

soar_agent = SoarAgent(agent_config, sim)
soar_agent.connect()
soar_agent.execute_command("step")
soar_agent.execute_command("step")

soar_agent.execute_command("p i1 -d 10")

