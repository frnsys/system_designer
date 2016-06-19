import time
import brood


class DeepThoughtAgent(brood.Agent):
    state_vars = ['thinking_time', 'friends']

    async def decide(self):
        # simulate communication
        for _ in range(self.state.friends):
            await self.world.get('whatev')
        time.sleep(self.state.thinking_time)


class DeepThoughtWorld(brood.world.World):
    state_vars = ['whatev']


def run(node, n_agents=1000, steps=10, thinking_time=0.01, friends=10):
    sim = brood.Simulation(node)
    world, world_addr = sim.spawn(
        DeepThoughtWorld,
        state={'whatev': 0},
        wraps=False)

    for _ in range(n_agents):
        agent, addr = sim.spawn(DeepThoughtAgent, state={
            'friends': friends,
            'thinking_time': thinking_time
        }, world_addr=world_addr)

    for report in sim.irun(10):
        pass