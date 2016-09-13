import re
import aiomas
import asyncio
import paramiko
from .serializers import get_np_serializer
from ..distributors import RoundRobin


# hacky...
N_NODES_RE = re.compile('starting (\d+)')


class NodeException(Exception):
    pass


class Cluster:
    """a Cluster is an abstraction over multiple Nodes;
    it provides an identical interface to a Node so you can
    use them interchangeably"""

    def __init__(self, port, hosts, distributor=RoundRobin, venv=None):
        """create a new cluster listening on `port`, managing `hosts`"""
        self.hosts = sum((self._start_node(host, user, start_port, venv)
                         for host, user, start_port in hosts), [])
        self._container = aiomas.Container.create(('localhost', port),
                                                  codec=aiomas.codecs.MsgPackBlosc,
                                                  extra_serializers=[get_np_serializer])
        self._container.has_manager = True
        self._managers = aiomas.run(self._connect_to_managers(self.hosts))
        self._distributor = distributor(self._managers)

    def _start_node(self, host, user, start_port, venv):
        """start a node on a remote host"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user)

        cmd = 'syd nodes {} --daemonize'.format(start_port)
        if venv is not None:
            cmd = 'source {}/bin/activate; {}'.format(venv, cmd)
        stdin, stdout, stderr = client.exec_command(cmd)

        # assume command failed if stderr is not empty
        if stderr.read():
            raise NodeException('Unable to execute `syd nodes` on host "{}". Is it configured?'.format(host))

        # get number of nodes created (hacky)
        output = stdout.read().decode('utf-8')
        print(output)
        n_nodes = int(N_NODES_RE.search(output).group(1))
        client.close()
        return ['tcp://{}:{}'.format(host, start_port + i)
                for i in range(n_nodes)]

    async def _connect_to_managers(self, hosts, timeout=10):
        """connect to all node managers"""
        _managers = []
        for host in hosts:
            # worker manager is at {host}/0
            manager = await self._container.connect('{}/0'.format(host), timeout=timeout)
            _managers.append(manager)
        return _managers

    def shutdown(self):
        """shutdown the cluster"""
        tasks = [asyncio.ensure_future(manager.stop())
                 for manager in self._managers]
        aiomas.run(asyncio.gather(*tasks))
        self._container.shutdown()

    def states(self):
        """iterate over all agent states across the cluster"""
        tasks = [asyncio.ensure_future(manager.states())
                 for manager in self._managers]

        for states in aiomas.run(asyncio.gather(*tasks)):
            yield from states

    def spawn(self, agent_cls, *args, **kwargs):
        """spawn an agent on the cluster"""
        manager = self._distributor.next(self._managers)
        qual_name = '{}:{}'.format(agent_cls.__module__, agent_cls.__name__)
        return aiomas.run(manager.spawn(qual_name, *args, **kwargs))

    async def decide_agents(self, *args, **kwargs):
        """call `decide` on all agents across the cluster"""
        tasks = [asyncio.ensure_future(
                    manager.decide_agents(*args, **kwargs))
                 for manager in self._managers]
        await asyncio.gather(*tasks)

    async def update_agents(self, *args, **kwargs):
        """call `update` on all agents across the cluster"""
        tasks = [asyncio.ensure_future(
                    manager.update_agents(*args, **kwargs))
                 for manager in self._managers]
        await asyncio.gather(*tasks)

    async def setup_agents(self, *args, **kwargs):
        """call `setup` on all agents across the cluster"""
        tasks = [asyncio.ensure_future(
                    manager.setup_agents(*args, **kwargs))
                 for manager in self._managers]
        await asyncio.gather(*tasks)
