import aiomas
import asyncio
import logging
import operator
import itertools
from .proxy import LocalProxy

logger = logging.getLogger(__name__)


class Node(aiomas.Container):
    """a node manages a population of agents"""
    def __init__(self, addr, *args, **kwargs):
        super().__init__(addr, *args, **kwargs)
        self._local_agent_proxies = {}

        # prepare logging for each node
        _, port = addr[:-1].rsplit(':', 1)
        handler = logging.FileHandler('/tmp/sydling_{}.log'.format(port))
        handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        self.logger.debug('node up at {}'.format(addr))


    @classmethod
    async def start(cls, addr, **container_kwargs):
        """starts a node managed by a NodeManager"""
        container_kwargs.update(as_coro=True)
        container = await cls.create(addr, **container_kwargs)
        container.has_manager = True
        try:
            manager = NodeManager(container)
            await manager.stop_received
        except KeyboardInterrupt:
            logger.info('Execution interrupted by user')
        finally:
            await container.shutdown(as_coro=True)

    @property
    def _agents(self):
        """iterator over every agent in the node
        (excluding the manager, if there is one)"""
        if getattr(self, 'has_manager', False):
            manager_url = '{}0'.format(self._base_url)
            yield from (a for a in self.agents.dict.values() if a.addr != manager_url)
        else:
            yield from self.agents.dict.values()

    def states(self):
        """iterator over every agent's state in the node"""
        return [agent.state for agent in self._agents]

    def spawn(self, agent_cls, *args, **kwargs):
        """spawn an agent in this node"""
        agent = agent_cls(self, *args, **kwargs)
        return LocalProxy(agent), agent.addr

    async def update_agents(self, *args, **kwargs):
        """call the 'apply_update' method on all agents"""
        for agent in self._agents:
            agent.apply_updates(*args, **kwargs)

    async def decide_agents(self, *args, **kwargs):
        """call the 'decide' method on all agents"""
        self.logger.debug('DECIDING AGENTS')
        for agent in self._agents:
            await agent.decide(*args, **kwargs)

    async def setup_agents(self, *args, **kwargs):
        """call the 'setup' method on all agents"""
        self.logger.debug('setting up agents!')
        for agent in self._agents:
            await agent.setup(*args, **kwargs)

    async def connect(self, url, timeout=0):
        """connect to an agent. checks if
        the requested agent is local to the container
        before communicating over the network"""
        base_url, id = url.rsplit('/', 1)

        # local
        if base_url == self._base_url[:-1]:
            if id not in self._local_agent_proxies:
                agent = self.agents.dict[id]
                self._local_agent_proxies[id] = LocalProxy(agent)
            return self._local_agent_proxies[id]

        # remote
        else:
            return await super().connect(url, timeout)

    # TODO this is provisional: doesn't seem to improve performance much?
    async def bulk_get(self, agent_addrs, var):
        addresses = [a.rsplit('/', 1) for a in agent_addrs]
        results = []
        tasks = []
        for base_url, ids_ in itertools.groupby(addresses, operator.itemgetter(0)):
            ids = (id for _, id in ids_)
            if base_url == self._base_url[:-1]:
                results.extend(self.bulk_get_local(ids, var))
            else:
                manager_url = '{}/0'.format(base_url)
                tasks.append(self.bulk_get_remote(manager_url, ids, var))

        # clean this up
        return results + list(itertools.chain.from_iterable(await asyncio.gather(*tasks)))
    def bulk_get_local(self, ids, var):
        return [self.agents.dict[id].get(var) for id in ids]
    async def bulk_get_remote(self, manager_url, ids, var):
        manager = await self.connect(manager_url)
        return await manager.bulk_get(ids, var)


class NodeManager(aiomas.subproc.Manager):
    """a special agent that manages a node"""

    @aiomas.expose
    def states(self):
        """iterator over every agent state in the node"""
        return self.container.states()

    @aiomas.expose
    def update_agents(self, *args, **kwargs):
        """call the 'update' method on all agents"""
        self.container.update_agents(*args, **kwargs)

    @aiomas.expose
    async def decide_agents(self, *args, **kwargs):
        """call the 'decide' method on all agents"""
        self.container.logger.debug('manager DECIDING AGENTS')
        await self.container.decide_agents(*args, **kwargs)

    @aiomas.expose
    async def setup_agents(self, *args, **kwargs):
        """call the 'setup' method on all agents"""
        self.container.logger.debug('setting up agents! in manager')
        await self.container.setup_agents(*args, **kwargs)

    @aiomas.expose
    def bulk_get(self, ids, var):
        return self.container.bulk_get_local(ids, var)
