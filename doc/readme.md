Development roadmap is spread throughout the [`spec`](spec) docs

---

# Audience

- people with little or no exposure to systems thinking and modeling
    - this includes people with no technical background!
- people familiar with systems thinking and modeling but looking for easier tools

# Goals

- accessible
    - easy setup
        - for more technically-inclined folks, a self-hosted/local option that's `pip` installable
        - for less technically-inclined folks, offer a hosted option with a web interface?
    - "training wheels"
        - include simple, _modifiable/forkable_ examples with detailed explanations/documentations
        - workshops and other educational programming demoing the framework's capacities
        - include common agent behaviors
        - include example frontends/visualizations

---

# Out-of-the-Box

Some things should be supported out-of-the-box to handle common use-cases and for demoing the framework:

- common agent behaviors
- common worlds (e.g. GridWorld)

---

## Concepts

- An _agent_ has a list of state variables defined for it. These state variables should encapsulate everything specific about a particular agent.
- A _node_ is a single process managing a population of agents.
- A _cluster_ manages multiple nodes, which may be processes on the same machine or across multiple machines. A cluster shares the interface of a single node, so you can use it as if you were using a single node.
- Agents are updated synchronously in _steps_; that is, agents all act "simultaneously". Doing parallel/distributed updates can get very complicated, so these update steps are broken into two parts:
    - _decide_ - the agent observes itself, other agents, and/or the world (i.e. collects the information it needs) and _submits_ updates for itself or other agents (but does not apply them yet). This should be read-only phase so there are no conflicts.
    - _update_ - the agent applies all queued updates. The possibility of collisions (i.e. conflicting updates) is constrained to this phase.
- The _world_ (aka "environment") is an agent which contains a global/shared state needed by all agents.

## Design

Models/simulations are composed of a graph of components. Components might be populations of agents, they might be number generators, etc...

---

## Usage notes

### Multi-node vs single-node

Running a multi-node simulation is _not necessarily faster_ than running a single-node simulation. The performance gain (or penalty) of a multi-node depends largely on two factors:

- how much computation each individual agent is doing (the more computation, the more appropriate a multi-node simulation)
- how much communication is happening between agents (this adds more overhead in a multi-node simulation)

The communication factor can to some degree be mitigated by distributed agents across nodes such that they are co-located with the agents they communicate the most with.

So an example use for the multi-node case is if you have many agents which "think" a lot and have to query a handful of agents. A less appropriate example is where you have many agents that do some relatively simple computations and have to do a lot of communication with other agents.
