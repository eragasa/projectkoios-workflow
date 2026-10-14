# `projectkoios.workflow.cpn.kernel` architecture

## Responsibility

The kernel module owns immutable CPN definitions and markings plus total, deterministic validation, enablement, selection, and firing operations. A marking is a place-indexed token multiset; equal anonymous tokens retain multiplicity, while identified tokens have globally correlated occurrences.

Enabledness is distinct from selection. Firing is pure and consumes exactly the selected occurrences after validating predecessor identities and any external-output binding.
