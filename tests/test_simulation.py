import aiomas
import unittest
from brood.node import Node
from brood.simulation import Simulation
from . import SimpleAgent


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.node = Node.create(('localhost', 5000))
        self.sim = Simulation(self.node)
        agent1, _ = self.node.spawn(SimpleAgent, state={'sup':10, 'huh':1})
        agent2, _ = self.node.spawn(SimpleAgent, state={'sup':20, 'huh':2})
        self.agents = [agent1, agent2]

    def tearDown(self):
        self.sim.container.shutdown()

    def test_reports(self):
        n_steps = 4
        reports = self.sim.run(n_steps, reports={
            'sup_sum': (lambda ss: sum(s.sup for s in ss), 2),
            'sup_sum2': (lambda ss: sum(s.sup for s in ss) * 2, 2),
            'sup_max': (lambda ss: max(s.sup for s in ss), 1)
        })
        expected_reports = [
            {'sup_sum2': 60, 'sup_max': 20, 'sup_sum': 30},
            {'sup_max': 20},
            {'sup_sum2': 60, 'sup_max': 20, 'sup_sum': 30},
            {'sup_max': 20}]
        self.assertEquals(reports, expected_reports)

    def test_run(self):
        n_steps = 4
        self.sim.run(n_steps)
        for agent in self.agents:
            count = aiomas.run(agent.counter())
            self.assertEquals(count, n_steps)
