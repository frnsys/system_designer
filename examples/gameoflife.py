import time
import brood
import random
import numpy as np
from functools import partial


def die(pos, state):
    state.grid[pos] = 0
    return state

def live(pos, state):
    state.grid[pos] = 1
    return state


class GOLAgent(brood.Agent):
    state_vars = ['alive', 'position']

    async def decide(self):
        """
        1. Any live cell with fewer than two live neighbours dies, as if caused by under-population.
        2. Any live cell with two or three live neighbours lives on to the next generation.
        3. Any live cell with more than three live neighbours dies, as if by over-population.
        4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        """
        neighbors = await self.world.neighbors(self.state.position)
        n_living_neighbors = neighbors.sum()
        if self.state.alive and (n_living_neighbors < 2 or n_living_neighbors > 3):
            self.state.alive = False
            await self.world.submit_update(partial(die, self.state.position))
        elif not self.state.alive and n_living_neighbors == 3:
            self.state.alive = True
            await self.world.submit_update(partial(live, self.state.position))


def run(node, width=20, height=20, steps=100, alive_prob=0.3):
    sim = brood.Simulation(node)
    grid = np.zeros((width, height), dtype=bool)
    world, world_addr = sim.spawn(brood.world.GridWorld,
                                  state={'grid': grid},
                                  wraps=False)

    for i in range(width):
        for j in range(height):
            alive = random.random() < alive_prob
            position = (i, j)
            agent, addr = sim.spawn(GOLAgent, state={
                'alive': alive,
                'position': position
            }, world_addr=world_addr)
            brood.run(world.set_position(alive, position))

    socketio = brood.handlers.SocketIO()
    for report in sim.irun(steps, {
        'n_alive': (lambda ss: sum(1 for s in ss if hasattr(s, 'alive') and s.alive), 1)
    }):
        print(report)
        grid = brood.run(world.get('grid'))
        socketio.emit('grid', {'grid':grid.tolist()})
        time.sleep(0.25)
