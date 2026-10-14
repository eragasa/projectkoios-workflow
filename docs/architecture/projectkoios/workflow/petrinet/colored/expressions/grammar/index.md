# `projectkoios.workflow.petrinet.colored.expressions.grammar`

## Purpose

Closed declarative expressions, inscriptions, and pure evaluation. The generic expression language admits literals and definition-owned bound variables only. It has no source text, callable, attribute traversal, import, ``eval``, filesystem, network, Workflow, Task, or scientific-policy surface. Transitions compose input patterns, an optional guard, and output templates; the public evaluator evaluates only values and guards and grants no firing or execution authority.

## Coordination boundary

This node coordinates no child package or module nodes and declares `CpnBindingVariableIdentity`, `CpnExpressionGrammarIdentity`, `CpnValueExpressionKind`, `CpnControlRecordConstructorField`, `CpnGuardOperator`, `CpnInputMode`, `CpnValueExpression`, `CpnGuardExpression`, `CpnTokenPattern`, `CpnInhibitorPattern`, `CpnInputInscription`, `CpnTokenTemplate`, `CpnOutputInscription`, `CpnGuardEvaluationResult`. It selects typed
collaborators and preserves dependency direction. It does not resolve payload
bodies, invoke providers, access persistence, or grant execution authority.

## Composition strategy

Composition uses immutable values and identity-bearing operations. Child modules
own their local validation, representation, mapping, linking, or CPN semantics.
This level must not copy domain topology or merge schema admission,
authorization, firing, numerical verification, and scientific validation.

## Source

The production owner is `src/python/projectkoios/workflow/petrinet/colored/expressions/grammar.py`. The companion implementation and
schematics documents record dependency rules and composition flow.
