import aiomas
from functools import partial


def update_var(var, value, state):
    setattr(state, var, value)
    return state


class State():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Agent(aiomas.Agent):
    state_vars = []

    def __init__(self, container, state, *args, world_addr=None, **kwargs):
        super().__init__(container)
        for key in self.state_vars:
            assert key in state
        self.state = State(**state)
        self.world_addr = world_addr
        self._updates = []
        self.init(state, *args, **kwargs)

    def init(self, state, *args, **kwargs):
        """initialization for an agent. you should
        override this method instead of `__init__`."""
        pass

    async def emit(self, name, *args, **kwargs):
        """emit an event from this agent"""
        await self.container.emit(name, self.addr, *args, **kwargs)

    @aiomas.expose
    def get(self, var):
        """get a state variable value"""
        return self.state.__dict__[var]

    @aiomas.expose
    def get_state(self):
        """get the agent's state"""
        return self.state

    async def decide(self):
        """agent observes and decides.
        the agent should not actually execute any
        updates here (to avoid collisions/ordering issues)"""
        pass

    async def setup(self):
        """any setup the agent needs at simulation startup,
        e.g. caching connections, can be done here"""
        if self.world_addr is not None:
            self.container.logger.debug('connecting to world')
            self.world = await self.container.connect(self.world_addr)

    @aiomas.expose
    def submit_update(self, fn):
        """add an update function to the update stack;
        update functions are composed into a single function.
        note this does _not_ execute the update.
        update functions take in an agent's state and return a new state.
        """
        # can't use function composition b/c of potential recursion depth error
        self._updates.append(fn)

    @aiomas.expose
    def submit_var_update(self, var, value):
        """convenience method for updating a single state variable"""
        self.submit_update(partial(update_var, var, value))

    def apply_updates(self):
        """apply all queued updates"""
        state = self.state
        for fn in self._updates:
            state = fn(state)
        self.state = state
        self._updates = []
