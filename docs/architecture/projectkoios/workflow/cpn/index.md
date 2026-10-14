# `projectkoios.workflow.cpn` architecture

## Responsibility

The CPN package owns the sole authoritative executable process semantics and the deterministic composition that produces executable definitions. It validates immutable flat nets and markings, enumerates enabled bindings, selects one binding under an explicit policy, and performs pure firing.

It contains no scheduler, database, external effect, plugin loading, scientific rule, or application status model. Operational services surround the kernel without changing its semantics.
