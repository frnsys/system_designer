import syd
import aiomas
import unittest
from syd.node import Node
from functools import partial
from syd.agent.base import MissingVarError
from . import SimpleAgent


@syd.behavior('cash')
def behavior(agent):
    agent.submit_var_update('cash', 10)


@syd.behavior('cash')
def behavior_with_params(agent, param):
    def update(state):
        state.cash *= param
        return state
    agent.submit_update(update)


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
        self.assertTrue(isinstance(self.agent.state, self.agent.State))
        self.assertEqual(self.agent.get('sup'), 10)

    def test_updates(self):
        def update1(state):
            state.sup *= 2
            return state

        def update2(state):
            state.huh -= 5
            return state

        # copy old state
        state = self.agent.State(**self.agent.state.__dict__)

        # no updates should be applied yet
        self.agent.submit_update(update1)
        self.agent.submit_update(update2)
        self.assertEquals(self.agent.state, state)

        self.agent.apply_updates()
        self.assertEquals(self.agent.state.sup, 20)
        self.assertEquals(self.agent.state.huh, 0)

    def test_behavior_missing_required_vars(self):
        def create_agent_class():
            class NewAgent(syd.Agent):
                state_vars = ['bleh']
                behaviors = [behavior]
            return NewAgent
        self.assertRaises(MissingVarError, create_agent_class)

    def test_behavior_with_required_vars(self):
        try:
            class NewAgent(syd.Agent):
                state_vars = ['cash']
                behaviors = [behavior]
        except MissingVarError:
            self.fail('should not have raised MissingVarError')

    def test_behaviors_called(self):
        class NewAgent(syd.Agent):
            state_vars = ['cash']
            behaviors = [behavior]

        agent = NewAgent(self.node, {'cash': 100})
        self.assertEquals(agent.state.cash, 100)

        aiomas.run(agent.decide())
        agent.apply_updates()
        self.assertEquals(agent.state.cash, 10)

    def test_behaviors_with_param_called(self):
        class NewAgent(syd.Agent):
            state_vars = ['cash']
            behaviors = [partial(behavior_with_params, param=2)]

        agent = NewAgent(self.node, {'cash': 100})
        self.assertEquals(agent.state.cash, 100)

        aiomas.run(agent.decide())
        agent.apply_updates()
        self.assertEquals(agent.state.cash, 200)

    def test_multiple_behaviors_called(self):
        class NewAgent(syd.Agent):
            state_vars = ['cash']
            behaviors = [behavior,
                         partial(behavior_with_params, param=2)]

        agent = NewAgent(self.node, {'cash': 100})
        self.assertEquals(agent.state.cash, 100)

        aiomas.run(agent.decide())
        agent.apply_updates()
        self.assertEquals(agent.state.cash, 20)
