supporting distributed simulations introduces a lot of design challenges. here are some notes on those.

features:

- adding new nodes during simulation
    - appropriately re-distributing to new nodes
- taking down nodes during simulation
    - appropriately re-distributing from old nodes
- node fault tolerance/replication
    - (optional) snapshotting of agent states, associated with node addresses, every n steps, to redis (or some similar distributed key-value store)
- node monitoring
    - get number of agents, types of agents, resource usage, etc
- moving agent(s) across nodes (single or in bulk)
- support running a single simulation across multiple nodes or multiple simulations across multiple nodes
- agents can communicate to agents on other nodes
- load balancing (i.e. agent redistribution) as communication patterns change

principles:

- moving from single to multi-node simulations should require no changes to their code other than the changing of a configuration option
- multi-node simulations should be robust against node failure
- agent distribution across nodes should minimize inter-node communication
- in general, any inter-node activity should be minimized

open questions:

- how do deal with collisions? perhaps it's enough to have, for each state variable, "add" and "subtract" operators that specify how updates are combined? need to think through this more
- should we use a proper cluster management system, e.g. zookeeper or etcd or consul?

ownership of attributes that are being updated? e.g.

> Before  an  agent federate can move a tile it must obtain ownership of the tile’s position attribute.  Once the tile has been moved by this agent, the second agent’s move should become invalid, as the tile is no longer at the position at which the agent initially perceived it.  To ensure that attributes are mutually exclusive, we only allow transfer of ownership once per simulation cycle for any given attribute.  A federate will then only relinquish ownership of an attribute if it has not already been updated at the current cycle.

can look to rust's ownership model as well
