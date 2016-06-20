import time
import brood
import random
import networkx as nx


contact_rate = 0.3
transmission_rate = 0.3
recovery_rate = 0.01


class SIRWorld(brood.World):
    def init(self, state, social_network):
        self.registry = {}
        self.social_network = social_network

    @brood.expose
    def register_agent(self, id, addr):
        """map agent ids to addresses"""
        self.registry[id] = addr

    @brood.expose
    def friends(self, id):
        """return friends of an agent"""
        return [self.registry[id_] for id_ in self.social_network.neighbors(id)]


class SIRAgent(brood.Agent):
    state_vars = ['id', 'sick'] # 0 = healthy, 1 = sick, 2 = recovered

    async def decide(self):
        # friends don't change, so cache them
        if not hasattr(self, 'friends'):
            self.friends = await self.world.friends(self.state.id)

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


def color_for_status(status):
    if status == 0:
        return '#0066ff'
    elif status == 1:
        return '#ff0000'
    elif status == 2:
        return '#FFFD8A'



def run(node, pop_size=150, sick_prob=0.1, prob_friends=0.02, n_steps=100):
    sim = brood.Simulation(node)
    social_network = nx.generators.gnp_random_graph(pop_size, prob_friends)

    world, world_addr = sim.spawn(
        SIRWorld,
        state={},
        social_network=social_network)

    # prep graph for sigma.js
    graph_data = {'nodes': []}
    for id in range(pop_size):
        sick = int(random.random() < sick_prob)
        agent, addr = sim.spawn(
            SIRAgent,
            state={'id': id, 'sick': sick},
            world_addr=world_addr)
        graph_data['nodes'].append({
            'id': id,
            'size': 1,
            'color': color_for_status(sick),
            'x': random.random(),
            'y': random.random()
        })
        brood.run(world.register_agent(id, addr))

    socketio = brood.handlers.SocketIO()

    graph_data['edges'] = [{
        'id': 'e{}'.format(i),
        'source': f,
        'target': t,
        'size': 1,
        'color': '#222222'}
        for i, (f, t) in enumerate(social_network.edges())]
    socketio.emit('setup', graph_data)

    for report in sim.irun(n_steps, {
        'n_sick': (lambda ss: sum(1 for s in ss if hasattr(s, 'sick') and s.sick == 1), 1),
        'n_recovered': (lambda ss: sum(1 for s in ss if hasattr(s, 'sick') and s.sick == 2), 1),
        'colors': (lambda ss: {s.id : color_for_status(s.sick) for s in ss if hasattr(s, 'sick')}, 1)
    }):
        socketio.emit('update', report['colors'])
        del report['colors']
        print(report)
        time.sleep(0.1)
