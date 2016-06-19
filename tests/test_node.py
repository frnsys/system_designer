import aiomas
import unittest
from unittest import mock
from brood.node import Node
from brood.node.proxy import LocalProxy
from . import SimpleAgent, mock_coro


class NodeTests(unittest.TestCase):
    def setUp(self):
        self.node = Node.create(('localhost', 5000))
        agent1, _ = self.node.spawn(SimpleAgent, state={'sup':10, 'huh':1})
        agent2, _ = self.node.spawn(SimpleAgent, state={'sup':20, 'huh':2})
        self.agents = [agent1, agent2]

    def tearDown(self):
        self.node.shutdown()

    def test_agent_iterator(self):
        agents = set(self.node._agents) # order may be inconsistent
        # these agents are _not_ proxies because they are used locally
        self.assertEquals(agents, set([a.obj for a in self.agents]))

    @mock.patch.object(SimpleAgent, 'decide', new_callable=mock_coro)
    def test_agent_decide(self, mock_method):
        aiomas.run(self.node.decide_agents())
        self.assertEquals(mock_method.call_count, 2)

    @mock.patch.object(SimpleAgent, 'apply_updates')
    def test_agent_update(self, mock_method):
        aiomas.run(self.node.update_agents())
        self.assertEquals(mock_method.call_count, 2)

    def test_local_proxy(self):
        agent = self.agents[0]
        res = aiomas.run(agent.what())
        self.assertTrue(isinstance(agent, LocalProxy))
        self.assertEquals(res, agent.obj.what())

    def test_gets_local_agent(self):
        addr = self.agents[0].addr
        agent_proxy = aiomas.run(self.node.connect(addr))
        self.assertTrue(isinstance(agent_proxy, LocalProxy))

    def test_bulk_get(self):
        results = aiomas.run(self.node.bulk_get([a.addr for a in self.agents], 'sup'))
        self.assertEqual(results, [10, 20])
