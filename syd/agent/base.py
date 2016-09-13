import aiomas
from functools import partial
from recordclass import recordclass


class AgentMeta(type):
    """metaclass for the Agent based class
    which defines the agent state
    and validates its behaviors"""
    def __new__(cls, name, parents, dct):
        state_vars = dct.get('state_vars', [])
        behaviors = dct.get('behaviors', [])

        dct['State'] = recordclass('{}State'.format(name), state_vars)

        # extract vars required by behaviors
        # can handle partials as well
        all_required_vars = set(sum((
            b.required_vars if not isinstance(b, partial)
            else b.func.required_vars
            for b in behaviors
        ), []))

        missing = [var for var in all_required_vars
                   if var not in state_vars]
        if missing:
            raise MissingVarError('required vars {} are missing in agent `state_vars`'.format(missing))
        return type.__new__(cls, name, parents, dct)


class Agent(aiomas.Agent, metaclass=AgentMeta):
    state_vars = []
    behaviors = []

    def __init__(self, container, state, *args, world_addr=None, **kwargs):
        super().__init__(container)
        self.state = self.State(**state)
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
        return getattr(self.state, var)

    @aiomas.expose
    def get_state(self):
        """get the agent's state"""
        return self.state

    async def decide(self):
        """agent observes and decides.
        the agent should not actually execute any
        updates here (to avoid collisions/ordering issues).
        if this is overridden, you should call `super().decide()`
        to execute attached behaviors"""
        for behavior in self.behaviors:
            behavior(self)

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


def update_var(var, value, state):
    setattr(state, var, value)
    return state


class MissingVarError(Exception):
    pass
