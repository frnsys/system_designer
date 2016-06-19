# Brood

Brood is a multi-agent simulation framework.

**Brood is under heavy development so it is not recommended for use at this moment. APIs and everything else are subject to change.**

It is built on top of [aiomas](https://aiomas.readthedocs.io/en/latest/). At this time Brood requires Python 3.5.

Brood is designed to support large agent-based simulations where the agents themselves are computationally expensive. With simpler models like cellular automata you'll lose most of the framework's benefits (see below for a bit more details).

Brood provides an easy way to emit arbitrary data, e.g. aggregate simulation reports every `n` steps, world grid states, etc, using `socketio`, so you can build arbitrary web visualizations on top:

![Game of Life](assets/gameoflife.gif)

![Schelling](assets/schelling.gif)

## Goals

- Provide a unified interface for single-node and multi-node simulations
- Minimize network communication
    - Efficiently distribute agents across a cluster
    - Load balancing/agent redistribution as communication patterns change
- Support
    - Agent mobility (lightweight, just by moving state)
    - Shared state objects (e.g. the World)
- Support arbitrary visualization and interaction
    - Easily generate reports at arbitrary step intervals
    - Event system and hooks (e.g. `emit` and `register`)
    - Provide a websocket interface for plugging in web front-ends
- Be general/flexible/expressive enough to support many kinds of agent-based models
- Provide out-of-the-box support for common use cases, e.g. GridWorld

## Concepts

- An _agent_ has a list of state variables defined for it. These state variables should encapsulate everything specific about a particular agent.
- A _node_ is a single process managing a population of agents.
- A _cluster_ manages multiple nodes, which may be processes on the same machine or across multiple machines. A cluster shares the interface of a single node, so you can use it as if you were using a single node.
- Agents are updated synchronously in _steps_; that is, agents all act "simultaneously". Doing parallel/distributed updates can get very complicated, so these update steps are broken into two parts:
    - _decide_ - the agent observes itself, other agents, and/or the world (i.e. collects the information it needs) and _submits_ updates for itself or other agents (but does not apply them yet). This should be read-only phase so there are no conflicts.
    - _update_ - the agent applies all queued updates. The possibility of collisions (i.e. conflicting updates) is constrained to this phase.
- The _world_ (aka "environment") is an agent which contains a global state needed by all agents.

## Usage

(not all of this is implemented yet, so this is kind of a design document)

## Examples

Some examples are implemented in the `examples` folder.

To run an example:

    python examples <example name>

The available examples are: `schelling, sir, gameoflife`.

There's also `deepthought` which is just to demonstrate the trade-offs between single and multi-node simulations.

There are web visualizations for `schelling` and `gameoflife`; to view them run:

    brood front 8888 examples

The frontend for the two are located at `/schelling.html` and `/gameoflife.html` respectively. Once you have the frontend loaded you can run the example (e.g. `python examples schelling`) to start sending socketio messages to it.

## Multi-node vs single-node

Running a multi-node simulation is _not necessarily faster_ than running a single-node simulation. The performance gain (or penalty) of a multi-node depends largely on two factors:

- how much computation each individual agent is doing (the more computation, the more appropriate a multi-node simulation)
- how much communication is happening between agents (this adds more overhead in a multi-node simulation)

The communication factor can to some degree be mitigated by distributed agents across nodes such that they are co-located with the agents they communicate the most with.

So an example use for the multi-node case is if you have many agents which "think" a lot and have to query a handful of agents. A less appropriate example is where you have many agents that do some relatively simple computations and have to do a lot of communication with other agents.

---

## Design Spec

- Initialize agent
    - Prior to simulation start
    - While simulation is running (e.g. reproduction/replication)
- Terminate agents (e.g. agent death)
- Initialize world
- Agent interaction
    - requesting and retrieving state information from each other
    - applying updates to each other
- Run distributed or single node
- Move agent from one node to another
- Node monitoring
    - Get number of agents, types of agents, resource usage, etc
- Websocket events for front-end (read, i.e, visualizations, and write, i.e. web interfaces)
- Testing and debugging tools
    - Test network/node failures for distributed applications
    - Distributed log handling (via Redis pub sub? this can also support a more general event system)
- Add new nodes during simulation
- Node fault tolerance/replication

Parallelization/distributed computing: agents are expected to be entirely independent in their execution _with the exception of_ their `decide` method.

---

ownership of attributes that are being updated? e.g.

> Before  an  agent federate can move a tile it must obtain ownership of the tile’s position attribute.  Once the tile has been moved by this agent, the second agent’s move should become invalid, as the tile is no longer at the position at which the agent initially perceived it.  To ensure that attributes are mutually exclusive, we only allow transfer of ownership once per simulation cycle for any given attribute.  A federate will then only relinquish ownership of an attribute if it has not already been updated at the current cycle.

can look to rust's ownership model as well

---

should we use a proper cluster management system, e.g. zookeeper or etcd or consul?
