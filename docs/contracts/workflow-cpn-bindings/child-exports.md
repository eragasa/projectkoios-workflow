# Child workflow exports and ports

This document is one normative component of the [canonical CPN payload and hierarchical binding contract set](index.md). The shared scope, vocabulary, status, and interpretation rules in the index apply here.

## Child workflow export

## `WorkflowChildDefinitionExport`

A child owner MUST publish an immutable export containing:

- owner and workflow-family identities;
- child source-definition identity and contract version;
- exact compiled child execution-plan identity and digest;
- exact nominal flat child CPN definition identity;
- exact canonical flat-definition representation identity and digest;
- exact child CPN execution-profile identity;
- initial-marking constructor descriptor identity;
- bounded typed input-port definitions;
- bounded typed terminal-output-port definitions;
- admitted terminal classifications;
- exactly one terminal-delivery requirement for every admitted terminal
  classification;
- cancellation and reconciliation capability declarations;
- protected-effect capability declarations;
- compiler/exporter implementation and version identities;
- source revision identity; and
- export contract version.

The export MUST contain no live owner, provider, registry, interpreter, SNAKES
object, callable, mutable configuration, or post-hoc evidence that identifies
the export itself.

A separate `WorkflowChildExportEvidenceBinding` MUST bind the already-derived
child-export identity to canonical conformance-evidence references. That
evidence binding MAY contribute to deployment acceptance and
`WorkflowExecutionBindingsIdentity`, but MUST NOT change or become an input to
the child-export or child-plan identity.

A child sourced from another CPN engine MAY be exported only through an
owner-controlled deterministic translator or adapter that produces canonical
flat CPN IR and conformance evidence. Field access and reviewed owner
constructors MUST lower to the closed projection and control-record-construction
grammar above; live classes, callables, and constructor import paths are invalid
canonical semantics. A constructor import path or reported place/transition
count alone is insufficient. Parameter-dependent initial markings MUST be
separated from stable topology so a run subject does not silently redefine the
child plan.

## Port definitions

Each port MUST identify:

- port identity and direction;
- exact CPN place and color identity in the child plan;
- exact payload schema/codec or admitted scalar kind;
- minimum and maximum token cardinality;
- correlation fields or reference identities required by the mapping; and
- whether the port is initial, external-event, terminal, cancellation, or
  reconciliation traffic.

Terminal ports MUST form a closed set. A terminal payload is evidence about the
child outcome; it MUST NOT implicitly assert parent-domain acceptance.
