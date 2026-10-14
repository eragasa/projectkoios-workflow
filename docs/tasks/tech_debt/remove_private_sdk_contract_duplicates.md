# Remove private Workflow SDK contract duplicates

## Problem

A separately installed Workflow SDK cannot be authoritative while the Workflow
service continues to define or consume private duplicate versions of the same
public identities, descriptors, requests, results, bindings, or manifests.

## Action

After the SDK alpha records exist:

- [ ] Inventory Workflow-private types that overlap the accepted SDK surface.
- [ ] Classify each as an internal implementation type, an SDK contract duplicate,
  or an adapter-specific record.
- [ ] Migrate public-contract use to the installed SDK package.
- [ ] Retain explicit adapters where internal representations intentionally differ.
- [ ] Remove duplicates only after equivalent tests and replay evidence pass.
- [ ] Add dependency-direction tests preventing the SDK from importing Workflow
  service internals.

## Completion evidence

- [ ] Retain a type-by-type ownership table.
- [ ] Prove through imports that Workflow consumes the installed SDK.
- [ ] Prove no duplicate public contract definitions remain.
- [ ] Retain isolated build and test results.
- [ ] Demonstrate replay equivalence for migrated retained records or provide an
  explicit versioned migration when equivalence is impossible.

This task must not delete prototypes or retained readers merely because names
look similar. Semantic equivalence and compatibility evidence are required.
