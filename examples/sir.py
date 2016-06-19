import brood
import random
import networkx as nx


contact_rate = 0.3
transmission_rate = 0.3
recovery_rate = 0.01


class SIRWorld(brood.World):
    def init(self, state, pop_size, prob_friends):
        self.registry = {}
        self.registry_rev = {}
        self.social_network = nx.generators.gnp_random_graph(pop_size, prob_friends)

    @brood.expose
    def register_agent(self, addr):
        """register an agent with the world,
        assigning them an id for the social network"""
        if self.registry:
            next = max(self.registry.values()) + 1
        else:
            next = 0
        self.registry[addr] = next
        self.registry_rev[next] = addr

    @brood.expose
    def friends(self, addr):
        """return friends of an agent"""
        id = self.registry[addr]
        return [self.registry_rev[id_] for id_ in self.social_network.neighbors(id)]


class SIRAgent(brood.Agent):
    state_vars = ['sick'] # 0 = healthy, 1 = sick, 2 = recovered

    async def decide(self):
        # friends don't change, so cache them
        if not hasattr(self, 'friends'):
            self.friends = await self.world.friends(self.addr)

        # only the actions of sick agents matter
        if self.state.sick == 1:
            # check if we recover
            if random.random() < recovery_rate:
                self.submit_var_update('sick', 2)
            else:
                for friend in self.friends:
                    if random.random() < contact_rate and random.random() < transmission_rate:
                        friend_proxy = await self.container.connect(friend)
                        sick = await friend_proxy.get('sick')
                        if sick == 0:
                            await friend_proxy.submit_var_update('sick', 1)


def run(node, pop_size=500, sick_prob=0.2, prob_friends=0.3, n_steps=100):
    sim = brood.Simulation(node)
    world, world_addr = sim.spawn(
        SIRWorld,
        state={},
        pop_size=pop_size,
        prob_friends=prob_friends)

    for i in range(pop_size):
        agent, addr = sim.spawn(
            SIRAgent,
            state={'sick': random.random() < sick_prob},
            world_addr=world_addr)
        brood.run(world.register_agent(addr))

    for report in sim.irun(n_steps, {
        'n_sick': (lambda ss: sum(1 for s in ss if hasattr(s, 'sick') and s.sick == 1), 1),
        'n_recovered': (lambda ss: sum(1 for s in ss if hasattr(s, 'sick') and s.sick == 2), 1)
    }):
        print(report)
