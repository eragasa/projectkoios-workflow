# `projectkoios.workflow.compilation.planning` architecture

## Responsibility

Planning compiles the complete source-definition closure into the durable declarative `WorkflowExecutionPlan`. It composes fragments, resolves namespaces and priorities, validates ports, flattens to canonical CPN IR, and records exact action and nested-target mappings.

Owner action descriptors are explicit compiler inputs. Their request/result contracts constrain typed ports/colors, action identity binds behavior, declared effect class selects an eligible pure or lifecycle lowering, and authority/idempotency/evidence contracts constrain operational tokens. The workflow source definition still supplies every connection, guard, concurrency relationship, retry route, and acceptance transition explicitly.

Planning performs no provider selection, live binding, run creation, effect execution, signature-derived topology, or reflective auto-wiring.
