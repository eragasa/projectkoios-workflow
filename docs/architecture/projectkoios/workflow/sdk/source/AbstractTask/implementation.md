# `AbstractTask` implementation

## Responsibility

Use a nominal ABC with non-overridable definition construction and explicit
subclass validation. Reject a subclass that supplies both atomic route state and
Workflow composition, inherits conflicting route declarations, or replaces the
validated definition template method.

Atomic Task definitions retain bounded identities and exact route descriptors.
Pure routes name an SDK firer descriptor; effectful routes name a separately
accepted lifecycle descriptor. Neither retains a live implementation. Provider
specialization remains owner-controlled: QE and VASP may derive different owner
Task records from one common owner Task role without adding backend fields to
this generic source contract.

Workflow specialization is defined by `AbstractWorkflow`; nesting creates a
separate child run at runtime. Tests must cover nominal membership, final-method
enforcement, immutable-definition stability, ambiguous route rejection, live
object exclusion, and owner mutation after definition construction.
