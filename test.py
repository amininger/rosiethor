import Python_sml_ClientInterface as sml
from soarutil import *

current_time_ms = lambda: int(round(time.time() * 1000))

def print_event_handler(eventID, self, agent, message):
    print(message)


# Init Agent
kernel = sml.Kernel.CreateKernelInNewThread()
kernel.SetAutoCommit(False)
agent = kernel.CreateAgent("test")
print_event_callback_id = agent.RegisterForPrintEvent(sml.smlEVENT_PRINT, print_event_handler, None)

# Do Stuff

il = agent.GetInputLink()

fruit = il.CreateIdWME("fruit")
fruit.CreateStringWME("apple", "fuji")
fruit.CreateStringWME("apple", "granny-smith")
fruit.CreateStringWME("apple", "honeycrisp")
fruit.CreateStringWME("banana", "chaqita")
fruit.CreateStringWME("cherry", "sour")
fruit.CreateStringWME("cherry", "black")

objs = il.CreateIdWME("objects")
for i in range(4):
    obj = objs.CreateIdWME("object")
    obj.CreateIntWME("id", i+1)
    obj.CreateStringWME("type", "object")
    pos = obj.CreateIdWME("pos")
    pos.CreateFloatWME("x", 2.1 - 0.4*i)
    pos.CreateFloatWME("y", -1.2 + 0.6*i)


agent.Commit()
agent.RunSelf(1)
print(agent.ExecuteCommandLine("p i2 -d 4"))

# Shutdown
agent.UnregisterForPrintEvent(print_event_callback_id)
kernel.DestroyAgent(agent)
kernel.Shutdown()
