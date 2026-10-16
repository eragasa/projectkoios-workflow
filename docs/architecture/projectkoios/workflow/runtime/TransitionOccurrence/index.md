# `TransitionOccurrence`

> **Status: provisional architecture iteration 2.**

## Responsibility

`TransitionOccurrence` is the durable identity of one selected and reserved CPN
transition binding at one exact enabling marking. When the transition represents
a Task route, the occurrence correlates to one exact run-scoped Task instance
and Task invocation without becoming either identity.

Repeated loop firing creates a new occurrence. Operational retries create new
attempts under the same occurrence. A workflow-backed Task additionally creates
a distinct child Workflow run correlated through durable child intent and
delivery records.

The occurrence binds definition and plan evidence, net instance, transition,
ordered binding, predecessor revision, selection, reservation, Task mapping, and
outcome evidence. Worker context additionally binds attempt identity and ordinal.
