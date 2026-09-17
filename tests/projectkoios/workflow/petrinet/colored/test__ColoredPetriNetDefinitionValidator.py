r"""Software verification of ``ColoredPetriNetDefinitionValidator``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetDefinitionValidator`` generic
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

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionValidator,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetValidationIssueCode,
    ColoredPetriNetValidationResult,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetDefinitionValidator


def issue_signatures(
    result: ColoredPetriNetValidationResult,
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
    assert SUT().execute(valid_definition()).issues == ()


def test_method__execute__returns_exact_ordered_relationship_findings() -> None:
    """Evidence ID: SV-PETRINET-068

    Requirement: Validation reports role, binder, color, and variable defects
    completely.

    Acceptance: Exact ordered path, code, related-identity, and message tuples match
    the fixed oracle.
    """
    base = valid_definition()
    transition = ColoredPetriNetTransitionDefinition(
        base.transitions[0].identity,
        (ColoredPetriNetBindingVariableIdentity("input"),),
        (ColoredPetriNetBindingVariableIdentity("output"),),
        ColoredPetriNetGuardExpression(
            ColoredPetriNetGuardOperator.EQUAL,
            left=variable("output"),
            right=literal(ColoredPetriNetValueKind.INTEGER, 1),
        ),
    )
    duplicate = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("input-2"),
        base.arcs[0].place_identity,
        transition.identity,
        base.arcs[0].input_inscription,
    )
    output = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("output"),
        base.places[0].identity,
        transition.identity,
        output_inscription=ColoredPetriNetOutputInscription(
            (
                ColoredPetriNetTokenTemplate(
                    ColoredPetriNetColorIdentity("unknown"), variable("missing")
                ),
            )
        ),
    )
    definition = ColoredPetriNetDefinition(
        base.identity,
        base.colors,
        base.places,
        (transition,),
        (base.arcs[0], duplicate, output),
        (transition.identity,),
    )
    assert issue_signatures(SUT().execute(definition)) == (
        (
            ("arcs", "output", "output_templates", "0", "color"),
            ColoredPetriNetValidationIssueCode.UNKNOWN_COLOR,
            ("output", "unknown"),
            "output template references an unknown color",
        ),
        (
            ("arcs", "output", "output_templates", "0", "variable"),
            ColoredPetriNetValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
            ("missing", "transition"),
            "output template references an undeclared variable",
        ),
        (
            ("transitions", "transition", "guard"),
            ColoredPetriNetValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
            ("output", "transition"),
            "guard references an external-output variable",
        ),
        (
            ("transitions", "transition", "variables"),
            ColoredPetriNetValidationIssueCode.DUPLICATE_BINDING_VARIABLE,
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
    pattern = ColoredPetriNetTokenPattern(
        transition.external_output_variable_identities[0],
        (base.colors[0].identity,),
    )
    input_arc = replace(
        base.arcs[0],
        input_inscription=ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.CONSUME, (pattern,)
        ),
    )
    definition = replace(base, arcs=(input_arc, base.arcs[1]))
    assert issue_signatures(SUT().execute(definition)) == (
        (
            ("arcs", "input", "input_patterns", "0", "variable"),
            ColoredPetriNetValidationIssueCode.UNDECLARED_BINDING_VARIABLE,
            ("output", "transition"),
            "input pattern binds an undeclared variable",
        ),
        (
            ("transitions", "transition", "variables"),
            ColoredPetriNetValidationIssueCode.UNBOUND_BINDING_VARIABLE,
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
        base.arcs[0], place_identity=ColoredPetriNetPlaceIdentity("unknown-place")
    )
    definition = replace(base, arcs=(invalid_input, base.arcs[1]))
    assert issue_signatures(SUT().execute(definition)) == (
        (
            ("arcs", "input", "place"),
            ColoredPetriNetValidationIssueCode.UNKNOWN_PLACE,
            ("input", "unknown-place"),
            "arc references an unknown place",
        ),
        (
            ("transitions", "transition", "variables"),
            ColoredPetriNetValidationIssueCode.UNBOUND_BINDING_VARIABLE,
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
    comparison = ColoredPetriNetGuardExpression(
        ColoredPetriNetGuardOperator.EQUAL,
        left=variable(external.value),
        right=literal(ColoredPetriNetValueKind.INTEGER, 1),
    )
    transition = replace(
        base.transitions[0],
        guard=ColoredPetriNetGuardExpression(
            ColoredPetriNetGuardOperator.ALL, (comparison, comparison)
        ),
    )
    repeated_result = SUT().execute(replace(base, transitions=(transition,)))
    repeated_issue = (
        ("transitions", "transition", "guard"),
        ColoredPetriNetValidationIssueCode.EXTERNAL_OUTPUT_VARIABLE_IN_GUARD,
        ("output", "transition"),
        "guard references an external-output variable",
    )
    assert issue_signatures(repeated_result) == (repeated_issue, repeated_issue)

    same = "same"
    unknown_transition_arc = replace(
        base.arcs[0],
        identity=ColoredPetriNetArcIdentity(same),
        transition_identity=base.transitions[0].identity.__class__(same),
    )
    nominal_result = SUT().execute(replace(base, arcs=(unknown_transition_arc,)))
    assert issue_signatures(nominal_result) == (
        (
            ("arcs", same, "transition"),
            ColoredPetriNetValidationIssueCode.UNKNOWN_TRANSITION,
            (same, same),
            "arc references an unknown transition",
        ),
        (
            ("transitions", "transition", "variables"),
            ColoredPetriNetValidationIssueCode.UNBOUND_BINDING_VARIABLE,
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
