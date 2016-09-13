## Notes:

- high-level spec, needs to be prioritized
- more of a wishlist in some parts

---

## Modularity

Simulation components should be constructable in a modular way, such that they take input(s) and have output(s) and can function as black-boxes.

If someone is interested, they can "zoom" into the black-box and see what it's composed of, which may include other black-box modules that can further be zoomed into, etc.

With this kind of module isolation, they can be exported for other models as well.

## Multiscale

Multiscale modeling could be supported, i.e. so that at a certain "distance" away from certain modules (e.g. n levels higher in abstraction or actual spatial distance for spatial models), the details of those models aren't processed but rather a simpler version are run. Related terms are "level-of-detail" (e.g. in video games, when you are far from an object only low-level textures are loaded), "culling", and "coarse-grained modeling".

## Publishing

A system for publishing models, their outputs and logs/traces, input data, along with discussion/conclusions could be interesting.

## Versioning

We should also have a versioning system for models.

## Forking

Modules and models (because of recursive modularity, there's no real distinction between the two) are both forkable, so people can riff and tweak each other.

A diffing system would be nice as well, making it easier to compare two models by identifying their exact differences.

## Interchange Format

Models should be representable by a human and machine readable interchange format.

This way people can easily import, export, and share models.

One distinction is whether or not the exported file is standalone (i.e. all top-level _and_ submodules are recursively described, even ones that have been imported from elsewhere) or not (just has UUID references to imported submodules, which are versioned).

## Module Marketplace

Some place for people to share their modules/models and for others to use would encourage more "social" modeling (in the sense of people modeling collaboratively).

## Arbitrary Frontends

The core of what we provide is a backend for flexibly describing/defining and running agent-based simulations, abstracting away technical concerns. We want to be agnostic about how this backend is accessed and represented - at the very least it will be an SDK, but will also have some way of feeding into custom web interfaces (i.e. via websockets). That way people can build their own visualizations or even UIs on top of it.

## Atomic Behaviors

A core abstraction of the framework is "atomic behaviors", i.e. discrete behaviors which can be hot-swapped on and off of an agent, each representing some aspect of behavior. They can be mixed and matched to define new agents.

Some behaviors may even be _metabehaviors_ which govern the addition, removal and even re-parameterization of other behaviors.

Behaviors themselves may be composed of other sub-behaviors as well.

## Examples

We have to have lots of accessible examples to demo what the framework is capable of and to help people learn how to use it.

This will also help guide development so we have a better sense of what we need to support.

## Extensibility

We are definitely not going to capture all use cases on our own, so the framework should support a great deal of extensibility at a lower level than modules and models. I don't have a good sense of what form this will take yet.

## Tracing & Logging

We should have a good deal of support for logging, snapshotting, etc over relevant variables of the model. We probably won't be able to have exhaustive logs if models get really big. But we should also support _tracing_ , i.e. identifying one agent and having a exceptionally detailed log of that agent's journey. Sort of like how in SimCity you can click on a resident and the camera will follow them around the city.

## Distributed computation

Outcomes of a simulation can vary with the scale of the simulation (e.g. how many agents are in it), so we want to be able to support fairly large simulations. Ideally without requiring investing in a lot of expensive hardware.

In any case, supporting distributed execution of simulations could go a long way here. Distributed computation is tricky but we could get a decent solution rolling that can later be improved upon.

## Calibration/validation support

To support more rigorous model development we should integrate tools for model calibration and validation.
