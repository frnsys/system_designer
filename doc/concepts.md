## Concepts

- An _agent_ has a list of state variables defined for it. These state variables should encapsulate everything specific about a particular agent.
- A _node_ is a single process managing a population of agents.
- A _cluster_ manages multiple nodes, which may be processes on the same machine or across multiple machines. A cluster shares the interface of a single node, so you can use it as if you were using a single node.
- Agents are updated synchronously in _steps_; that is, agents all act "simultaneously". Doing parallel/distributed updates can get very complicated, so these update steps are broken into two parts:
    - _decide_ - the agent observes itself, other agents, and/or the world (i.e. collects the information it needs) and _submits_ updates for itself or other agents (but does not apply them yet). This should be read-only phase so there are no conflicts.
    - _update_ - the agent applies all queued updates. The possibility of collisions (i.e. conflicting updates) is constrained to this phase.
- The _world_ (aka "environment") is an agent which contains a global/shared state needed by all agents.
