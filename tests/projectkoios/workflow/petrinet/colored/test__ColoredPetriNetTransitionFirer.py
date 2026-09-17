r"""Software verification of ``ColoredPetriNetTransitionFirer``.

Evidence profile: routine

Bounded artifact scope: the public ``ColoredPetriNetTransitionFirer`` ActionObject.

Facet and represented meaning

Identity-closed pure successor construction with complete occurrence audit.

Intrinsic and cross-object scope

Replay closure, consumption, production, external binding, and failures are covered.

VVUQ and scientific exclusions

This is software verification, not external execution, scientific validation, or UQ.
"""

from dataclasses import replace

import pytest
from _firing_fixtures import firing_input_for, valid_firing_input
from _validation_fixtures import literal, variable

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetFiringFailureCode,
    ColoredPetriNetFiringOutcomeKind,
    ColoredPetriNetInhibitorPattern,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetSelectionDirectiveIdentity,
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionFirer,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

pytestmark = pytest.mark.software_verification
SUT = ColoredPetriNetTransitionFirer


def test_method__execute__success__consumes_and_produces_pure_successor() -> None:
    """Evidence ID: SV-PETRINET-122

    Requirement: Firing removes exact consume occurrences and evaluates outputs.

    Acceptance: One token is consumed, value two is produced, and replay is equal.
    """
    firing_input = valid_firing_input()
    result = SUT().execute(firing_input)
    replay = SUT().execute(firing_input)
    assert result == replay
    assert result.outcome is ColoredPetriNetFiringOutcomeKind.SUCCESS
    assert result.successor_marking is not None
    assert result.audit is not None
    assert len(result.audit.consumed_occurrences) == 1
    assert result.audit.read_occurrences == ()
    assert len(result.audit.produced_tokens) == 1
    assert result.successor_marking.places[0].tokens[0].value.value == 2
    assert firing_input.predecessor_marking.places[0].tokens[0].value.value == 1


def test_method__execute__external_binding__returns_closed_mismatch_failure() -> None:
    """Evidence ID: SV-PETRINET-123

    Requirement: External output assignments exactly match declared order and identity.

    Acceptance: An empty external binding returns the stable mismatch failure.
    """
    firing_input = valid_firing_input()
    empty = ColoredPetriNetBinding(firing_input.transition_identity, ())
    result = SUT().execute(replace(firing_input, external_output_binding=empty))
    assert result.outcome is ColoredPetriNetFiringOutcomeKind.FAILURE
    assert result.failure is not None
    assert result.failure.code is (
        ColoredPetriNetFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH
    )
    assert result.successor_marking is None


def test_method__execute__selection_replay__rejects_stale_predecessor() -> None:
    """Evidence ID: SV-PETRINET-124

    Requirement: Firing recomputes enablement from the full predecessor state.

    Acceptance: A changed predecessor returns ``ENABLEMENT_MISMATCH``.
    """
    firing_input = valid_firing_input()
    empty_place = replace(firing_input.predecessor_marking.places[0], tokens=())
    changed = replace(firing_input.predecessor_marking, places=(empty_place,))
    result = SUT().execute(replace(firing_input, predecessor_marking=changed))
    assert result.failure is not None
    assert result.failure.code is ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH


def test_method__execute__selection_replay__rejects_changed_representation() -> None:
    """Evidence ID: SV-PETRINET-138

    Requirement: Enablement identity binds exact represented predecessor state, not
    only its nominal identity and enabled value bindings.

    Acceptance: Replacing an anonymous consumed token by differently identified
    equal-valued tokens while retaining the marking identity returns distinct
    content-identified ``ENABLEMENT_MISMATCH`` results.
    """
    firing_input = valid_firing_input()
    place = firing_input.predecessor_marking.places[0]
    identified = replace(
        place.tokens[0], token_identity=ColoredPetriNetTokenIdentity("replacement")
    )
    changed_place = replace(place, tokens=(identified,))
    changed = replace(firing_input.predecessor_marking, places=(changed_place,))
    result = SUT().execute(replace(firing_input, predecessor_marking=changed))
    other_token = replace(
        place.tokens[0], token_identity=ColoredPetriNetTokenIdentity("other")
    )
    other_marking = replace(
        firing_input.predecessor_marking,
        places=(replace(place, tokens=(other_token,)),),
    )
    other_result = SUT().execute(
        replace(firing_input, predecessor_marking=other_marking)
    )
    assert result.failure is not None
    assert result.failure.code is ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH
    assert other_result.failure is not None
    assert other_result.failure.code is (
        ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH
    )
    assert result.identity != other_result.identity


def test_method__execute__definition_replay__rejects_changed_representation() -> None:
    """Evidence ID: SV-PETRINET-139

    Requirement: Enablement identity binds exact represented definition state.

    Acceptance: Expanding an admitted-kind set under the same nominal definition
    identity returns ``ENABLEMENT_MISMATCH``.
    """
    firing_input = valid_firing_input()
    color = firing_input.definition.colors[0]
    changed_color = replace(
        color,
        allowed_value_kinds=(
            ColoredPetriNetValueKind.INTEGER,
            ColoredPetriNetValueKind.STRING,
        ),
    )
    changed_definition = replace(firing_input.definition, colors=(changed_color,))
    result = SUT().execute(replace(firing_input, definition=changed_definition))
    assert result.failure is not None
    assert result.failure.code is ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH


def test_method__execute__occurrence_capacity__shares_across_modes() -> None:
    """Evidence ID: SV-PETRINET-140

    Requirement: Consume and read capacity are separate while each mode reserves
    distinct occurrences internally.

    Acceptance: One predecessor occurrence satisfies one consume and one read demand.
    """
    base = valid_firing_input()
    definition = base.definition
    transition = definition.transitions[0]
    read_variable = ColoredPetriNetBindingVariableIdentity("read")
    changed_transition = replace(
        transition,
        input_variable_identities=(
            transition.input_variable_identities[0],
            read_variable,
        ),
    )
    read_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("read"),
        definition.places[0].identity,
        transition.identity,
        ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.READ,
            (
                ColoredPetriNetTokenPattern(
                    read_variable, (definition.colors[0].identity,)
                ),
            ),
        ),
    )
    changed_definition = replace(
        definition,
        transitions=(changed_transition,),
        arcs=definition.arcs + (read_arc,),
    )
    marking = replace(
        base.predecessor_marking, definition_identity=changed_definition.identity
    )
    firing_input = firing_input_for(
        changed_definition,
        marking,
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
    result = SUT().execute(firing_input)
    assert result.audit is not None
    assert result.audit.consumed_occurrences[0].occurrence_ordinal == 0
    assert result.audit.read_occurrences[0].occurrence_ordinal == 0


def test_method__execute__occurrence_ordering__uses_distinct_least_tuple() -> None:
    """Evidence ID: SV-PETRINET-141

    Requirement: Multiple consume demands reserve distinct occurrences and choose the
    lexically least feasible occurrence tuple.

    Acceptance: Two equal demands consume predecessor ordinals zero and one.
    """
    base = valid_firing_input()
    definition = base.definition
    transition = definition.transitions[0]
    second = ColoredPetriNetBindingVariableIdentity("second")
    changed_transition = replace(
        transition,
        input_variable_identities=(
            transition.input_variable_identities[0],
            second,
        ),
    )
    input_arc = next(arc for arc in definition.arcs if arc.input_inscription)
    assert input_arc.input_inscription is not None
    first_pattern = input_arc.input_inscription.patterns[0]
    assert type(first_pattern) is ColoredPetriNetTokenPattern
    changed_input = replace(
        input_arc,
        input_inscription=ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.CONSUME,
            (
                first_pattern,
                ColoredPetriNetTokenPattern(second, (definition.colors[0].identity,)),
            ),
        ),
    )
    changed_definition = replace(
        definition,
        transitions=(changed_transition,),
        arcs=tuple(
            changed_input if arc is input_arc else arc for arc in definition.arcs
        ),
    )
    token = base.predecessor_marking.places[0].tokens[0]
    marking = replace(
        base.predecessor_marking,
        places=(replace(base.predecessor_marking.places[0], tokens=(token, token)),),
    )
    firing_input = firing_input_for(
        changed_definition,
        marking,
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
    result = SUT().execute(firing_input)
    assert result.audit is not None
    assert tuple(
        item.occurrence_ordinal for item in result.audit.consumed_occurrences
    ) == (0, 1)


def test_method__execute__inhibitor__audits_absence_and_rejects_presence() -> None:
    """Evidence ID: SV-PETRINET-142

    Requirement: Inhibitors are nonbinding absence constraints with explicit success
    audit; changed presence cannot pass stale replay.

    Acceptance: Absence records count zero and later presence yields mismatch failure.
    """
    base = valid_firing_input()
    definition = base.definition
    empty_place = ColoredPetriNetPlaceDefinition(
        ColoredPetriNetPlaceIdentity("inhibitor-place"),
        (definition.colors[0].identity,),
    )
    inhibitor_arc = ColoredPetriNetArcDefinition(
        ColoredPetriNetArcIdentity("inhibitor"),
        empty_place.identity,
        definition.transitions[0].identity,
        ColoredPetriNetInputInscription(
            ColoredPetriNetInputMode.INHIBIT,
            (ColoredPetriNetInhibitorPattern((definition.colors[0].identity,)),),
        ),
    )
    changed_definition = replace(
        definition,
        places=definition.places + (empty_place,),
        arcs=definition.arcs + (inhibitor_arc,),
    )
    empty_marking = replace(
        base.predecessor_marking,
        places=base.predecessor_marking.places
        + (ColoredPetriNetPlaceMarking(empty_place.identity, ()),),
    )
    firing_input = firing_input_for(
        changed_definition,
        empty_marking,
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
    success = SUT().execute(firing_input)
    assert success.audit is not None
    assert success.audit.inhibitor_evaluations[0].matching_count == 0
    present = replace(
        empty_marking,
        places=tuple(
            ColoredPetriNetPlaceMarking(
                item.place_identity,
                (base.predecessor_marking.places[0].tokens[0],),
            )
            if item.place_identity == empty_place.identity
            else item
            for item in empty_marking.places
        ),
    )
    failure = SUT().execute(replace(firing_input, predecessor_marking=present))
    assert failure.failure is not None
    assert failure.failure.code is ColoredPetriNetFiringFailureCode.ENABLEMENT_MISMATCH


@pytest.mark.parametrize(
    "variant",
    ["extra", "wrong_transition", "wrong_value"],
    ids=["extra_assignment", "wrong_transition", "wrong_value_kind"],
)
def test_method__execute__external_binding__rejects_defects(variant: str) -> None:
    """Evidence ID: SV-PETRINET-143

    Requirement: External outputs match exact transition, variables, order, and
    definition-compatible values.

    Acceptance: Extra, wrong-transition, and wrong-valued variants fail closed.
    """
    firing_input = valid_firing_input()
    assignment = firing_input.external_output_binding.assignments[0]
    if variant == "extra":
        external = replace(
            firing_input.external_output_binding,
            assignments=firing_input.external_output_binding.assignments
            + (
                ColoredPetriNetBindingAssignment(
                    ColoredPetriNetBindingVariableIdentity("extra"), assignment.value
                ),
            ),
        )
        expected = ColoredPetriNetFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH
    elif variant == "wrong_transition":
        external = replace(
            firing_input.external_output_binding,
            transition_identity=ColoredPetriNetTransitionIdentity("other"),
        )
        expected = ColoredPetriNetFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH
    else:
        external = replace(
            firing_input.external_output_binding,
            assignments=(
                replace(
                    assignment,
                    value=ColoredPetriNetValue(
                        ColoredPetriNetValueKind.STRING, "wrong-kind"
                    ),
                ),
            ),
        )
        expected = ColoredPetriNetFiringFailureCode.PRODUCED_TOKEN_INVALID
    result = SUT().execute(replace(firing_input, external_output_binding=external))
    assert result.failure is not None
    assert result.failure.code is expected


def test_method__execute__external_order__rejects_reordering() -> None:
    """Evidence ID: SV-PETRINET-144

    Requirement: External assignment order is definition-declared order.

    Acceptance: A complete reversed two-variable binding returns mismatch.
    """
    base = valid_firing_input()
    definition = base.definition
    transition = definition.transitions[0]
    first, second = (
        ColoredPetriNetBindingVariableIdentity("first"),
        ColoredPetriNetBindingVariableIdentity("second"),
    )
    changed_transition = replace(
        transition, external_output_variable_identities=(first, second)
    )
    output_arc = next(arc for arc in definition.arcs if arc.output_inscription)
    changed_output = replace(
        output_arc,
        output_inscription=ColoredPetriNetOutputInscription(
            (
                ColoredPetriNetTokenTemplate(
                    definition.colors[0].identity, variable("first")
                ),
                ColoredPetriNetTokenTemplate(
                    definition.colors[0].identity, variable("second")
                ),
            )
        ),
    )
    changed_definition = replace(
        definition,
        transitions=(changed_transition,),
        arcs=tuple(
            changed_output if arc is output_arc else arc for arc in definition.arcs
        ),
    )
    firing_input = firing_input_for(
        changed_definition,
        base.predecessor_marking,
        (
            ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),
            ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 3),
        ),
    )
    reversed_external = replace(
        firing_input.external_output_binding,
        assignments=tuple(reversed(firing_input.external_output_binding.assignments)),
    )
    result = SUT().execute(
        replace(firing_input, external_output_binding=reversed_external)
    )
    assert result.failure is not None
    assert result.failure.code is (
        ColoredPetriNetFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH
    )


def test_method__execute__output_evaluation__closes_identity_type_failure() -> None:
    """Evidence ID: SV-PETRINET-145

    Requirement: Output evaluation type defects return a closed failure.

    Acceptance: An integer token-identity expression returns evaluation failure.
    """
    base = valid_firing_input()
    definition = base.definition
    output_arc = next(arc for arc in definition.arcs if arc.output_inscription)
    assert output_arc.output_inscription is not None
    template = output_arc.output_inscription.templates[0]
    changed_output = replace(
        output_arc,
        output_inscription=ColoredPetriNetOutputInscription(
            (replace(template, token_identity_expression=variable("output")),)
        ),
    )
    changed_definition = replace(
        definition,
        arcs=tuple(
            changed_output if arc is output_arc else arc for arc in definition.arcs
        ),
    )
    firing_input = firing_input_for(
        changed_definition,
        base.predecessor_marking,
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
    result = SUT().execute(firing_input)
    assert result.failure is not None
    assert (
        result.failure.code is ColoredPetriNetFiringFailureCode.OUTPUT_EVALUATION_FAILED
    )


@pytest.mark.parametrize(
    "retained", [True, False], ids=["retained_collision", "released_reuse"]
)
def test_method__execute__token_identity__handles_collision_and_reuse(
    retained: bool,
) -> None:
    """Evidence ID: SV-PETRINET-146

    Requirement: Produced identities cannot collide with retained tokens, while an
    identity released by consumption may be reused.

    Acceptance: Retained collision fails; consumed-only reuse succeeds.
    """
    base = valid_firing_input()
    definition = base.definition
    output_arc = next(arc for arc in definition.arcs if arc.output_inscription)
    assert output_arc.output_inscription is not None
    template = output_arc.output_inscription.templates[0]
    changed_output = replace(
        output_arc,
        output_inscription=ColoredPetriNetOutputInscription(
            (
                replace(
                    template,
                    token_identity_expression=literal(
                        ColoredPetriNetValueKind.STRING, "shared"
                    ),
                ),
            )
        ),
    )
    changed_definition = replace(
        definition,
        arcs=tuple(
            changed_output if arc is output_arc else arc for arc in definition.arcs
        ),
    )
    consumed = replace(
        base.predecessor_marking.places[0].tokens[0],
        token_identity=(None if retained else ColoredPetriNetTokenIdentity("shared")),
    )
    tokens: tuple[ColoredPetriNetToken, ...] = (consumed,)
    if retained:
        tokens += (
            ColoredPetriNetToken(
                definition.colors[0].identity,
                ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 9),
                ColoredPetriNetTokenIdentity("shared"),
            ),
        )
    marking = replace(
        base.predecessor_marking,
        places=(replace(base.predecessor_marking.places[0], tokens=tokens),),
    )
    firing_input = firing_input_for(
        changed_definition,
        marking,
        (ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 2),),
    )
    result = SUT().execute(firing_input)
    if retained:
        assert result.failure is not None
        assert result.failure.code is (
            ColoredPetriNetFiringFailureCode.TOKEN_IDENTITY_COLLISION
        )
    else:
        assert result.outcome is ColoredPetriNetFiringOutcomeKind.SUCCESS


@pytest.mark.parametrize(
    "variant",
    ["selection", "directive", "binding", "transition"],
    ids=["selection", "directive", "binding", "transition"],
)
def test_method__execute__derivation_links__rejects_mismatch(variant: str) -> None:
    """Evidence ID: SV-PETRINET-147

    Requirement: Firing rejects altered selection, directive, and selected binding.

    Acceptance: Each altered derivation link returns its dedicated failure code.
    """
    firing_input = valid_firing_input()
    assignment = firing_input.selected_binding.assignments[0]
    alternate = ColoredPetriNetBinding(
        firing_input.transition_identity,
        (
            replace(
                assignment,
                value=ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 99),
            ),
        ),
    )
    if variant == "selection":
        changed = replace(
            firing_input,
            selection_result=replace(
                firing_input.selection_result, selected_binding=alternate
            ),
        )
        expected = ColoredPetriNetFiringFailureCode.SELECTION_MISMATCH
    elif variant == "directive":
        changed = replace(
            firing_input,
            directive_identity=ColoredPetriNetSelectionDirectiveIdentity("0" * 64),
        )
        expected = ColoredPetriNetFiringFailureCode.DIRECTIVE_MISMATCH
    elif variant == "binding":
        changed = replace(firing_input, selected_binding=alternate)
        expected = ColoredPetriNetFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH
    else:
        changed = replace(
            firing_input,
            transition_identity=ColoredPetriNetTransitionIdentity("other"),
        )
        expected = ColoredPetriNetFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH
    result = SUT().execute(changed)
    assert result.failure is not None
    assert result.failure.code is expected


def test_method__execute__argument__rejects_wrong_nominal_type() -> None:
    """Evidence ID: SV-PETRINET-125

    Requirement: The firer accepts exactly one ``ColoredPetriNetFiringInput``.

    Acceptance: An equal-looking object raises ``TypeError``.
    """
    with pytest.raises(TypeError):
        SUT().execute("input")  # type: ignore[arg-type]
