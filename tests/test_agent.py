import unittest
from brood.node import Node
from brood.agent import State
from . import SimpleAgent


class AgentTests(unittest.TestCase):
    def setUp(self):
        state = {
            'sup': 10,
            'huh': 5
        }
        self.node = Node.create(('localhost', 5000))
        self.agent = SimpleAgent(self.node, state)

    def tearDown(self):
        self.node.shutdown()

    def test_state(self):
        self.assertTrue(isinstance(self.agent.state, State))
        self.assertEqual(self.agent.get('sup'), 10)

    def test_updates(self):
        def update1(state):
            state.sup *= 2
            return state

        def update2(state):
            state.huh -= 5
            return state

        # copy old state
        state = State(**self.agent.state.__dict__)

        # no updates should be applied yet
        self.agent.submit_update(update1)
        self.agent.submit_update(update2)
        self.assertEquals(self.agent.state, state)

        self.agent.apply_updates()
        self.assertEquals(self.agent.state.sup, 20)
        self.assertEquals(self.agent.state.huh, 0)
