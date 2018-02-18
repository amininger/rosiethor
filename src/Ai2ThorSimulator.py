import ai2thor.controller
import json

class Ai2ThorSimulator:
    def __init__(self):
        self.world = None

    def start(self):
        self.sim = ai2thor.controller.Controller()
        self.sim.start()
        self.sim.reset('FloorPlan28')

        self.world = self.sim.step(dict(action='Initialize', gridSize=0.25)).metadata

    def save(self):
        world_info = json.dumps(self.world)
        with open("world.json", "w") as f:
            f.write(world_info)

    def load(self):
        with open("world.json", "r") as f:
            world_info = f.read()
            self.world = json.loads(world_info)


