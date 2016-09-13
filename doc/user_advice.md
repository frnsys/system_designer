## Multi-node vs single-node

Running a multi-node simulation is _not necessarily faster_ than running a single-node simulation. The performance gain (or penalty) of a multi-node depends largely on two factors:

- how much computation each individual agent is doing (the more computation, the more appropriate a multi-node simulation)
- how much communication is happening between agents (this adds more overhead in a multi-node simulation)

The communication factor can to some degree be mitigated by distributed agents across nodes such that they are co-located with the agents they communicate the most with.

So an example use for the multi-node case is if you have many agents which "think" a lot and have to query a handful of agents. A less appropriate example is where you have many agents that do some relatively simple computations and have to do a lot of communication with other agents.
