"""Verification of canonical experimental CPN definition and marking codecs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest
from _pure_action_fixtures import _cpn_firing_fixture
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnDefinitionDecoder,
    ExperimentalWorkflowCpnDefinitionEncoder,
    ExperimentalWorkflowCpnMarkingDecoder,
    ExperimentalWorkflowCpnMarkingEncoder,
)
from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinitionValidator,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInhibitorPattern,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetMarking,
    ColoredPetriNetMarkingIdentity,
    ColoredPetriNetMarkingValidator,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetPlaceMarking,
    ColoredPetriNetToken,
    ColoredPetriNetTokenIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def test_definition_codec_round_trips_exact_semantics() -> None:
    definition, _, _ = _cpn_firing_fixture()
    encoder = ExperimentalWorkflowCpnDefinitionEncoder()
    decoder = ExperimentalWorkflowCpnDefinitionDecoder()

    encoded = encoder.encode(definition)
    decoded = decoder.decode(encoded)

    assert decoded == definition
    assert encoder.encode(decoded) == encoded
    assert decoder.profile_identity == encoder.profile_identity
    assert ColoredPetriNetDefinitionValidator().execute(decoded).is_valid


def test_definition_codec_round_trips_closed_expression_variants() -> None:
    definition, _, _ = _cpn_firing_fixture()
    literal = ColoredPetriNetValueExpression(
        kind=ColoredPetriNetValueExpressionKind.LITERAL,
        literal=ColoredPetriNetValue(
            ColoredPetriNetValueKind.STRING, "literal"
        ),
    )
    guard_literal = ColoredPetriNetValueExpression(
        kind=ColoredPetriNetValueExpressionKind.LITERAL,
        literal=ColoredPetriNetValue(ColoredPetriNetValueKind.INTEGER, 1),
    )
    transition = replace(
        definition.transitions[0],
        guard=ColoredPetriNetGuardExpression(
            operator=ColoredPetriNetGuardOperator.EQUAL,
            left=guard_literal,
            right=guard_literal,
        ),
    )
    output_arc = definition.arcs[1]
    assert output_arc.output_inscription is not None
    template = replace(
        output_arc.output_inscription.templates[0],
        value_expression=literal,
        token_identity_expression=literal,
    )
    output_arc = replace(
        output_arc,
        output_inscription=replace(
            output_arc.output_inscription,
            templates=(template,),
        ),
    )
    inhibitor_arc = ColoredPetriNetArcDefinition(
        identity=ColoredPetriNetArcIdentity("fixture.inhibitor"),
        place_identity=definition.places[0].identity,
        transition_identity=transition.identity,
        input_inscription=ColoredPetriNetInputInscription(
            mode=ColoredPetriNetInputMode.INHIBIT,
            patterns=(
                ColoredPetriNetInhibitorPattern(
                    (definition.colors[0].identity,)
                ),
            ),
        ),
    )
    changed = replace(
        definition,
        transitions=(transition,),
        arcs=(definition.arcs[0], output_arc, inhibitor_arc),
    )

    encoded = ExperimentalWorkflowCpnDefinitionEncoder().encode(changed)

    assert ExperimentalWorkflowCpnDefinitionDecoder().decode(encoded) == changed


@pytest.mark.parametrize(
    "mutation",
    (
        lambda document: document | {"unknown": True},
        lambda document: document | {"schema": "unsupported"},
        lambda document: (
            document
            | {
                "definition": document["definition"]
                | {"selection_policy": "unsupported"}
            }
        ),
    ),
)
def test_definition_decoder_rejects_noncanonical_or_changed_documents(
    mutation: object,
) -> None:
    definition, _, _ = _cpn_firing_fixture()
    encoded = ExperimentalWorkflowCpnDefinitionEncoder().encode(definition)
    document = json.loads(encoded)
    assert callable(mutation)
    changed = mutation(document)

    with pytest.raises(ValueError):
        ExperimentalWorkflowCpnDefinitionDecoder().decode(_canonical(changed))

    with pytest.raises(ValueError):
        ExperimentalWorkflowCpnDefinitionDecoder().decode(b" " + encoded)


def test_marking_codec_round_trips_every_closed_value_kind() -> None:
    definition, _, _ = _cpn_firing_fixture()
    color = ColoredPetriNetColorIdentity("fixture.all-values")
    marking = ColoredPetriNetMarking(
        identity=ColoredPetriNetMarkingIdentity("fixture.all-values-marking"),
        definition_identity=definition.identity,
        places=(
            ColoredPetriNetPlaceMarking(
                place_identity=ColoredPetriNetPlaceIdentity("fixture.values"),
                tokens=(
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.NONE, None
                        ),
                    ),
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.BOOLEAN, True
                        ),
                    ),
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.INTEGER, -(2**63)
                        ),
                    ),
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.REAL, -0.0
                        ),
                    ),
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.STRING, "artifact:α"
                        ),
                        ColoredPetriNetTokenIdentity("fixture.identified"),
                    ),
                    ColoredPetriNetToken(
                        color,
                        ColoredPetriNetValue(
                            ColoredPetriNetValueKind.STRING_SEQUENCE,
                            ("a", "a", "β"),
                        ),
                    ),
                ),
            ),
        ),
    )
    encoder = ExperimentalWorkflowCpnMarkingEncoder()
    decoder = ExperimentalWorkflowCpnMarkingDecoder()

    encoded = encoder.encode(marking)
    decoded = decoder.decode(encoded)

    assert decoded == marking
    assert encoder.encode(decoded) == encoded
    assert decoder.profile_identity == encoder.profile_identity


def test_marking_codec_round_trips_a_definition_valid_marking() -> None:
    definition, marking, _ = _cpn_firing_fixture()
    encoded = ExperimentalWorkflowCpnMarkingEncoder().encode(marking)
    decoded = ExperimentalWorkflowCpnMarkingDecoder().decode(encoded)

    assert decoded == marking
    assert (
        ColoredPetriNetMarkingValidator().execute(definition, decoded).is_valid
    )
    assert hashlib.sha256(encoded).hexdigest() == (
        "93b117ab8a206d638e9138a9f3862e759495404b945d1650853ae45e5a19139b"
    )


def test_marking_decoder_rejects_unknown_fields_and_noncanonical_values() -> (
    None
):
    _, marking, _ = _cpn_firing_fixture()
    encoded = ExperimentalWorkflowCpnMarkingEncoder().encode(marking)
    document = json.loads(encoded)
    document["marking"]["places"][0]["tokens"][0]["unknown"] = True

    with pytest.raises(ValueError):
        ExperimentalWorkflowCpnMarkingDecoder().decode(_canonical(document))

    with pytest.raises(ValueError):
        ExperimentalWorkflowCpnMarkingDecoder().decode(b"\n" + encoded)


def test_representation_decoders_require_exact_bytes() -> None:
    with pytest.raises(TypeError):
        ExperimentalWorkflowCpnDefinitionDecoder().decode("{}")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ExperimentalWorkflowCpnMarkingDecoder().decode("{}")  # type: ignore[arg-type]
