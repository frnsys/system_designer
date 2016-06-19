import aiomas
from collections import defaultdict


class Simulation:
    def __init__(self, container):
        """container can either be a Node or a Cluster instance"""
        self.container = container
        self.container.parent = self

    def spawn(self, agent_cls, *args, **kwargs):
        """spawn an agent, returns a proxy"""
        return self.container.spawn(agent_cls, *args, **kwargs)

    async def _step(self):
        await self.container.decide_agents()
        await self.container.update_agents()

    def irun(self, steps, reports=None):
        """run the simulation lazily (as an iterator)"""
        # reports = {name: (fn, mod step)}
        aggs = defaultdict(dict)
        reports = reports or {}
        for name, (fn, mod_step) in reports.items():
            aggs[mod_step][name] = fn

        aiomas.run(self.container.setup_agents())

        for i in range(steps):
            aiomas.run(self._step())

            # TODO any way to make this more efficient?
            report = {}
            states = None
            for mod_step, agg_fns in aggs.items():
                if i % mod_step == 0:
                    for name, fn in agg_fns.items():
                        if states is None:
                            states = self.container.states()
                        report[name] = fn(states)
            yield report

    def run(self, steps, reports=None):
        """run the simulation"""
        return [report for report in self.irun(steps, reports)]
