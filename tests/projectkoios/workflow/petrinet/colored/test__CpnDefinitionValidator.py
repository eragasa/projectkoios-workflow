r"""Software verification of ``CpnDefinitionValidator``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnDefinitionValidator`` generic
colored-Petri-net contract.

Facet and represented meaning

The class represents its documented immutable data or deterministic action boundary.

Intrinsic and cross-object scope

The focused class contract is covered; enablement and firing remain excluded.

VVUQ and scientific exclusions

These synthetic checks establish software behavior only, not numerical verification,
scientific validation, UQ, authority, execution, or human acceptance.
"""

from dataclasses import replace

import pytest
from _validation_fixtures import literal, valid_definition, variable

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnDefinition,
    CpnPlaceIdentity,
    CpnTransitionDefinition,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnInputInscription,
    CpnInputMode,
    CpnOutputInscription,
    CpnTokenPattern,
    CpnTokenTemplate,
)
from projectkoios.workflow.petrinet.colored.validation.definitions.complete import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from projectkoios.workflow.petrinet.colored.validation.findings import (
    CpnValidationIssueCode,
    CpnValidationResult,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnDefinitionValidator


def issue_signatures(
    result: CpnValidationResult,
) -> tuple[tuple[object, ...], ...]:
    """Evidence ID: Owns no identifier; supports exact validator oracles.

    Requirement: Validator tests compare path, code, identities, and message.

    Acceptance: The helper projects no less than path, code, identities, and message.
    """
    return tuple(
        (item.path, item.code, item.related_identities, item.message)
        for item in result.issues
    )


def test_method__execute__returns_no_findings_for_complete_graph() -> None:
    """Evidence ID: SV-PETRINET-067

    Requirement: A complete graph with separated variable roles is structurally valid.

    Acceptance: Execution returns the exact empty issue tuple.
    """
    assert (
        SUT().execute(CpnDefinitionValidationRequest(valid_definition())).issues
        == ()
    )


def test_method__execute__returns_exact_ordered_relationship_findings() -> None:
    """Evidence ID: SV-PETRINET-068

    Requirement: Validation reports role, binder, color, and variable defects
    completely.

    Acceptance: Exact ordered path, code, related-identity, and message tuples match
    the fixed oracle.
    """
    base = valid_definition()
    transition = CpnTransitionDefinition(
        base.transitions[0].identity,
        (CpnBindingVariableIdentity("input"),),
        (CpnBindingVariableIdentity("output"),),
        CpnGuardExpression(
            CpnGuardOperator.EQUAL,
            left=variable("output"),
            right=literal(CpnValueKind.INTEGER, 1),
        ),
    )
    duplicate = CpnArcDefinition(
        CpnArcIdentity("input-2"),
        base.arcs[0].place_identity,
        transition.identity,
        base.arcs[0].input_inscription,
    )
    output = CpnArcDefinition(
        CpnArcIdentity("output"),
        base.places[0].identity,
        transition.identity,
        output_inscription=CpnOutputInscription(
            (
                CpnTokenTemplate(
                    CpnColorIdentity("unknown"), variable("missing")
                ),
            )
        ),
    )
    definition = CpnDefinition(
        base.identity,
        base.colors,
        base.places,
        (transition,),
        (base.arcs[0], duplicate, output),
        (transition.identity,),
    )
    assert issue_signatures(
        SUT().execute(CpnDefinitionValidationRequest(definition))
    ) == (
        (
            ("arcs", "output", "output_templates", "0", "color"),
            CpnValidationIssueCode.UNKNOWN_COLOR,
            ("output", "unknown"),
            "output template references an unknown color",
        ),
        (
            ("arcs", "output", "output_templates", "0", "variable"),
            CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
            ("missing", "transition"),
            "output template references an undeclared variable",
        ),
        (
            ("transitions", "transition", "guard"),
            CpnValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
            ("output", "transition"),
            "guard references an external-output variable",
        ),
        (
            ("transitions", "transition", "variables"),
            CpnValidationIssueCode.DUPLICATE_BINDING_VARIABLE,
            ("input", "transition"),
            "declared input variable has multiple binding patterns",
        ),
    )


def test_method__execute__rejects_external_output_as_input_binder() -> None:
    """Evidence ID: SV-PETRINET-084

    Requirement: Consume/read patterns bind only declared input variables, never
    external-output variables.

    Acceptance: Exact undeclared-binder and unbound-input findings are returned.
    """
    base = valid_definition()
    transition = base.transitions[0]
    pattern = CpnTokenPattern(
        transition.external_output_variable_identities[0],
        (base.colors[0].identity,),
    )
    input_arc = replace(
        base.arcs[0],
        input_inscription=CpnInputInscription(CpnInputMode.CONSUME, (pattern,)),
    )
    definition = replace(base, arcs=(input_arc, base.arcs[1]))
    assert issue_signatures(
        SUT().execute(CpnDefinitionValidationRequest(definition))
    ) == (
        (
            ("arcs", "input", "input_patterns", "0", "variable"),
            CpnValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
            ("output", "transition"),
            "input pattern binds an undeclared variable",
        ),
        (
            ("transitions", "transition", "variables"),
            CpnValidationIssueCode.UNBOUND_BINDING_VARIABLE,
            ("input", "transition"),
            "declared input variable has no binding pattern",
        ),
    )


def test_method__execute__suppresses_cascades_from_unknown_references() -> None:
    """Evidence ID: SV-PETRINET-085

    Requirement: An unresolved arc reference emits its primary issue and cannot bind
    variables or cause dependent pattern/template findings.

    Acceptance: An unknown-place input arc returns ``UNKNOWN_PLACE`` plus the genuine
    transition-level ``UNBOUND_BINDING_VARIABLE`` only.
    """
    base = valid_definition()
    invalid_input = replace(
        base.arcs[0], place_identity=CpnPlaceIdentity("unknown-place")
    )
    definition = replace(base, arcs=(invalid_input, base.arcs[1]))
    assert issue_signatures(
        SUT().execute(CpnDefinitionValidationRequest(definition))
    ) == (
        (
            ("arcs", "input", "place"),
            CpnValidationIssueCode.UNKNOWN_PLACE,
            ("input", "unknown-place"),
            "arc references an unknown place",
        ),
        (
            ("transitions", "transition", "variables"),
            CpnValidationIssueCode.UNBOUND_BINDING_VARIABLE,
            ("input", "transition"),
            "declared input variable has no binding pattern",
        ),
    )


def test_method__execute__retains_repeated_and_nominal_findings() -> None:
    """Evidence ID: SV-PETRINET-086

    Requirement: Validation is total for repeated malformed occurrences and distinct
    nominal identities with equal lexical spelling.

    Acceptance: Repeated guard findings remain repeated, and equal arc/transition
    spellings remain repeated related identities without raising.
    """
    base = valid_definition()
    external = base.transitions[0].external_output_variable_identities[0]
    comparison = CpnGuardExpression(
        CpnGuardOperator.EQUAL,
        left=variable(external.value),
        right=literal(CpnValueKind.INTEGER, 1),
    )
    transition = replace(
        base.transitions[0],
        guard=CpnGuardExpression(
            CpnGuardOperator.ALL, (comparison, comparison)
        ),
    )
    repeated_result = SUT().execute(
        CpnDefinitionValidationRequest(replace(base, transitions=(transition,)))
    )
    repeated_issue = (
        ("transitions", "transition", "guard"),
        CpnValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
        ("output", "transition"),
        "guard references an external-output variable",
    )
    assert issue_signatures(repeated_result) == (repeated_issue, repeated_issue)

    same = "same"
    unknown_transition_arc = replace(
        base.arcs[0],
        identity=CpnArcIdentity(same),
        transition_identity=base.transitions[0].identity.__class__(same),
    )
    nominal_result = SUT().execute(
        CpnDefinitionValidationRequest(
            replace(base, arcs=(unknown_transition_arc,))
        )
    )
    assert issue_signatures(nominal_result) == (
        (
            ("arcs", same, "transition"),
            CpnValidationIssueCode.UNKNOWN_TRANSITION,
            (same, same),
            "arc references an unknown transition",
        ),
        (
            ("transitions", "transition", "variables"),
            CpnValidationIssueCode.UNBOUND_BINDING_VARIABLE,
            ("input", "transition"),
            "declared input variable has no binding pattern",
        ),
    )


def test_method__execute__rejects_wrong_nominal_type() -> None:
    """Evidence ID: SV-PETRINET-087

    Requirement: Definition validation accepts only the exact public definition type.

    Acceptance: An equal-looking object raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT().execute("definition")  # type: ignore[arg-type]
