r"""Software verification of ``CpnTransitionEnabler``.

Evidence profile: routine

Bounded artifact scope: the public ``CpnTransitionEnabler`` ActionObject.

Facet and represented meaning

Complete deterministic enabled-binding enumeration for one exact state.

Intrinsic and cross-object scope

Validation, multiset capacity, inhibitors, guards, identity binding, semantic
deduplication, and canonical ordering are covered.

VVUQ and scientific exclusions

This generic control-flow software verification establishes no firing, external
effect, scientific validation, or uncertainty quantification.
"""

from dataclasses import replace

import pytest
from _firing_fixtures import valid_firing_input
from _validation_fixtures import valid_definition, variable

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnDefinition,
    CpnTransitionDefinition,
)
from projectkoios.workflow.petrinet.colored.enablement.outcomes import (
    CpnEnablementFailureCode,
    CpnOrderingPolicyIdentity,
)
from projectkoios.workflow.petrinet.colored.enablement.transitions import (
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from projectkoios.workflow.petrinet.colored.expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnGuardExpression,
    CpnGuardOperator,
    CpnInhibitorPattern,
    CpnInputInscription,
    CpnInputMode,
    CpnTokenPattern,
    CpnValueExpression,
    CpnValueExpressionKind,
)
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
    CpnPlaceMarking,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnToken,
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = CpnTransitionEnabler


def marking(definition: CpnDefinition, values: tuple[int, ...]) -> CpnMarking:
    """Evidence ID: Owns no identifier; supports enablement examples.

    Requirement: Tests need a complete synthetic marking for one definition.

    Acceptance: The helper returns the exact requested anonymous integer multiset.
    """
    color = definition.colors[0].identity
    tokens = tuple(
        CpnToken(color, CpnValue(CpnValueKind.INTEGER, value))
        for value in values
    )
    return CpnMarking(
        CpnMarkingIdentity("marking"),
        definition.identity,
        (CpnPlaceMarking(definition.places[0].identity, tokens),),
    )


def test_method__execute__retained_vector__preserves_exact_identity() -> None:
    firing_input = valid_firing_input()

    result = SUT().execute(
        CpnTransitionEnablementRequest(
            firing_input.definition,
            firing_input.predecessor_marking,
        )
    )

    assert result.identity.value == (
        "2129292215957352322b9687254ea8b586ce34b26c8b2f03689ee491077627fe"
    )
    assert result.transition_enabler_identity.value == (
        "colored-petri-net-transition-enabler-v1"
    )
    assert result.ordering_policy_identity.value == (
        "colored-petri-net-enablement-order-v1"
    )


def test_method__execute__enumeration__orders_and_deduplicates_value_bindings() -> (
    None
):
    """Evidence ID: SV-PETRINET-098

    Requirement: Enablement returns every distinct semantic binding in policy order.

    Acceptance: Values are ordered canonically and equal anonymous occurrences collapse.
    """
    definition = valid_definition()
    state = marking(definition, (2, 1, 1))
    result = SUT().execute(CpnTransitionEnablementRequest(definition, state))
    replay = SUT().execute(CpnTransitionEnablementRequest(definition, state))
    changed = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, (3,)))
    )
    assert result.is_success
    assert replay.identity == result.identity
    assert changed.identity != result.identity
    assert result.enabled_bindings is not None
    assert tuple(
        binding.assignments[0].value.value
        for binding in result.enabled_bindings
    ) == (1, 2)
    assert result.definition_identity == definition.identity
    assert result.marking_identity == CpnMarkingIdentity("marking")
    assert result.expression_evaluator_identity.value == (
        "projectkoios.workflow.cpn.expression-evaluator:0.1"
    )
    assert result.ordering_policy_identity.value == (
        "colored-petri-net-enablement-order-v1"
    )
    assert result.transition_enabler_identity.value == (
        "colored-petri-net-transition-enabler-v1"
    )


def test_method__execute__multiset_capacity__uses_separate_reservations() -> (
    None
):
    """Evidence ID: SV-PETRINET-099

    Requirement: Read demands reserve distinct read occurrences, consume demands reserve
    distinct consume occurrences, and the same occurrence may satisfy one of each.

    Acceptance: Two equal occurrences satisfy one consume plus two reads; one does not.
    """
    base = valid_definition()
    consume, read_one, read_two = (
        CpnBindingVariableIdentity(name)
        for name in ("consume", "read_one", "read_two")
    )
    transition = CpnTransitionDefinition(
        base.transitions[0].identity,
        (consume, read_one, read_two),
        (),
        CpnGuardExpression(CpnGuardOperator.TRUE),
    )
    color = base.colors[0].identity
    place = base.places[0].identity
    arcs = (
        CpnArcDefinition(
            CpnArcIdentity("consume"),
            place,
            transition.identity,
            CpnInputInscription(
                CpnInputMode.CONSUME,
                (CpnTokenPattern(consume, (color,)),),
            ),
        ),
        CpnArcDefinition(
            CpnArcIdentity("read"),
            place,
            transition.identity,
            CpnInputInscription(
                CpnInputMode.READ,
                (
                    CpnTokenPattern(read_one, (color,)),
                    CpnTokenPattern(read_two, (color,)),
                ),
            ),
        ),
    )
    definition = CpnDefinition(
        base.identity,
        base.colors,
        base.places,
        (transition,),
        arcs,
        (transition.identity,),
    )
    one = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, (1,)))
    )
    two = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, (1, 1)))
    )
    assert one.enabled_bindings == ()
    assert two.enabled_bindings is not None
    assert len(two.enabled_bindings) == 1
    assert tuple(
        item.value.value for item in two.enabled_bindings[0].assignments
    ) == (
        1,
        1,
        1,
    )


def test_method__execute__inhibitor__requires_absence_without_binding() -> None:
    """Evidence ID: SV-PETRINET-100

    Requirement: Inhibitor patterns bind no value and require matching-token absence.

    Acceptance: Empty input enables one empty binding; a matching token disables it.
    """
    base = valid_definition()
    transition = replace(
        base.transitions[0],
        input_variable_identities=(),
        external_output_variable_identities=(),
    )
    inhibitor = replace(
        base.arcs[0],
        input_inscription=CpnInputInscription(
            CpnInputMode.INHIBIT,
            (CpnInhibitorPattern((base.colors[0].identity,)),),
        ),
    )
    definition = replace(
        base,
        transitions=(transition,),
        arcs=(inhibitor,),
        transition_priority=(transition.identity,),
    )
    empty = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, ()))
    )
    occupied = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, (1,)))
    )
    assert empty.enabled_bindings is not None
    assert len(empty.enabled_bindings) == 1
    assert empty.enabled_bindings[0].assignments == ()
    assert occupied.enabled_bindings == ()


def test_method__execute__failures__retains_validation_and_version_state() -> (
    None
):
    """Evidence ID: SV-PETRINET-101

    Requirement: Operational defects produce closed failures with no binding payload.

    Acceptance: Invalid marking and unsupported policy return exact stable codes.
    """
    definition = valid_definition()
    invalid_marking = CpnMarking(
        CpnMarkingIdentity("marking"), definition.identity, ()
    )
    invalid = SUT().execute(
        CpnTransitionEnablementRequest(definition, invalid_marking)
    )
    assert invalid.enabled_bindings is None
    assert invalid.failure is not None
    assert invalid.failure.code is CpnEnablementFailureCode.INVALID_MARKING
    assert invalid.failure.validation_issues

    unsupported = SUT().execute(
        CpnTransitionEnablementRequest(
            definition,
            marking(definition, (1,)),
            ordering_policy_identity=CpnOrderingPolicyIdentity("unknown"),
        )
    )
    assert unsupported.failure is not None
    assert unsupported.failure.code is (
        CpnEnablementFailureCode.UNSUPPORTED_ORDERING_POLICY
    )


def test_method__execute__guard_failure__fails_complete_operation() -> None:
    """Evidence ID: SV-PETRINET-102

    Requirement: A guard type failure is not silently interpreted as disabled.

    Acceptance: The complete operation returns ``GUARD_EVALUATION_FAILED``.
    """
    base = valid_definition()
    guard = CpnGuardExpression(
        CpnGuardOperator.EQUAL,
        left=variable("input"),
        right=CpnValueExpression(
            CpnValueExpressionKind.LITERAL,
            CpnValue(CpnValueKind.STRING, "one"),
        ),
    )
    definition = replace(
        base, transitions=(replace(base.transitions[0], guard=guard),)
    )
    result = SUT().execute(
        CpnTransitionEnablementRequest(definition, marking(definition, (1,)))
    )
    assert result.failure is not None
    assert result.failure.code is (
        CpnEnablementFailureCode.GUARD_EVALUATION_FAILED
    )


def test_method__execute__arguments__rejects_wrong_nominal_types() -> None:
    """Evidence ID: SV-PETRINET-103

    Requirement: Public arguments require their exact nominal types.

    Acceptance: Equal-looking strings and identity classes raise ``TypeError``.
    """
    definition = valid_definition()
    state = marking(definition, (1,))
    with pytest.raises(TypeError):
        SUT().execute("request")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        CpnTransitionEnablementRequest("definition", state)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        CpnTransitionEnablementRequest(
            definition,
            state,
            expression_evaluator_identity=CpnOrderingPolicyIdentity("x"),  # type: ignore[arg-type]
        )
