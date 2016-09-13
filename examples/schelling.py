import syd
import time
import random
import numpy as np
from itertools import product
from functools import partial


class SchellingAgent(syd.Agent):
    state_vars = ['type', 'position', 'satisfaction', 'threshold']

    async def decide(self):
        neighbors = await self.world.neighbors(self.state.position)
        n_same = np.where(neighbors == self.state.type)[0].size
        satisfaction = n_same/neighbors.size
        self.submit_var_update('satisfaction', satisfaction)
        if satisfaction < 1 - self.state.threshold:
            await self.world.queue_random_move(self.state.position, self.state.type, self.addr)


class SchellingWorld(syd.world.GridWorld):
    state_vars = ['grid', 'vacancies']

    async def decide(self):
        self.submit_update(self.update_vacancies)

    @syd.expose
    async def queue_random_move(self, position, agent_type, agent_addr):
        if self.state.vacancies:
            new_pos = self.state.vacancies.pop(random.randrange(len(self.state.vacancies)))
            self.submit_update(partial(self.move_agent, position, new_pos, agent_type))
            agent_proxy = await self.container.connect(agent_addr)
            await agent_proxy.submit_var_update('position', new_pos)

    def move_agent(self, position, new_pos, value, state):
        x, y = position
        nx, ny = new_pos
        state.grid[x, y] = 0
        state.grid[nx, ny] = value
        return state

    def update_vacancies(self, state):
        state.vacancies = list(self.vacancies(empty_val=0))
        return state


class SchellingVoxelWorld(syd.world.VoxelWorld, SchellingWorld):
    def move_agent(self, position, new_pos, value, state):
        x, y, z = position
        nx, ny, nz = new_pos
        state.grid[x, y, z] = 0
        state.grid[nx, ny, nz] = value
        return state


def run(node, n_agents=5000, n_types=3, width=80, height=80, depth=None, n_steps=400, threshold=0.6, wraps=False):
    if depth is None:
        assert n_agents < width * height
        grid = np.zeros((width, height))
        positions = list(product(range(width), range(height)))
        world_cls = SchellingWorld
    else:
        assert n_agents < width * height * depth
        grid = np.zeros((width, height, depth))
        positions = list(product(range(width), range(height), range(depth)))
        world_cls = SchellingVoxelWorld

    # value of 0 is reserved for empty positions
    types = [i+1 for i in range(n_types)]

    sim = syd.Simulation(node)
    world, world_addr = sim.spawn(
        world_cls,
        state={'grid': grid, 'vacancies': []},
        wraps=wraps)

    socketio = syd.handlers.SocketIO()
    for _ in range(n_agents):
        position = positions.pop(random.randrange(len(positions)))
        type = random.choice(types)
        agent, addr = sim.spawn(SchellingAgent, state={
            'type': type,
            'position': position,
            'satisfaction': 0.,
            'threshold': threshold
        }, world_addr=world_addr)
        syd.run(world.set_position(type, position))

    for report in sim.irun(n_steps, {
        'total_satisfaction': (lambda ss: sum(s.satisfaction for s in ss if hasattr(s, 'satisfaction')), 1)
    }):
        print('mean satisfaction:', report['total_satisfaction']/n_agents)
        grid = syd.run(world.get('grid'))
        socketio.emit('grid', {'grid':grid.tolist()})
        time.sleep(0.2)
