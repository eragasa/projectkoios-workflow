"""Canonical representation codec for experimental shadow-CPN definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetArcIdentity,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetColorDefinition,
    ColoredPetriNetColorIdentity,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetDefinitionValidator,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetGuardOperator,
    ColoredPetriNetInhibitorPattern,
    ColoredPetriNetInputInscription,
    ColoredPetriNetInputMode,
    ColoredPetriNetOutputInscription,
    ColoredPetriNetPlaceDefinition,
    ColoredPetriNetPlaceIdentity,
    ColoredPetriNetSelectionPolicy,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetTokenTemplate,
    ColoredPetriNetTransitionDefinition,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

from ._cpn_representation import (
    MAX_CPN_REPRESENTATION_ITEMS as _MAX_ITEMS,
)
from ._cpn_representation import (
    bounded_count as _bounded_count,
)
from ._cpn_representation import (
    bounded_text as _bounded,
)
from ._cpn_representation import (
    closed_array as _array,
)
from ._cpn_representation import (
    closed_object as _object,
)
from ._cpn_representation import (
    exact_text as _text,
)
from ._cpn_representation import (
    validate_text as _validate_text,
)
from ._cpn_representation import (
    value_from_state as _value_from_state,
)
from ._cpn_representation import (
    value_state as _value_state,
)

_DEFINITION_PROFILE = "projectkoios.workflow.experimental-cpn-definition-json:0"
_MAX_DEFINITION_BYTES = 4 * 1024 * 1024
_MAX_EXPRESSION_DEPTH = 64


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity:
    """Identity of the bounded canonical flat-definition representation."""

    value: str

    def __post_init__(self) -> None:
        _validate_text(self.value, "definition representation profile identity")


@final
class ExperimentalWorkflowCpnDefinitionEncoder:
    """Encode exact shadow-CPN definition state as bounded canonical JSON."""

    __slots__ = ()

    @property
    def profile_identity(
        self,
    ) -> ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity:
        return ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity(
            _DEFINITION_PROFILE
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowCpnDefinitionEncoder is not subclassable"
        )

    def encode(self, definition: ColoredPetriNetDefinition) -> bytes:
        """Return the exact bounded representation selected by this profile."""
        if type(definition) is not ColoredPetriNetDefinition:
            raise TypeError("definition must be ColoredPetriNetDefinition")
        state = _definition_state(definition)
        payload = json.dumps(
            {
                "definition": state,
                "schema": _DEFINITION_PROFILE,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > _MAX_DEFINITION_BYTES:
            raise ValueError("encoded definition exceeds its byte bound")
        return payload


@final
class ExperimentalWorkflowCpnDefinitionDecoder:
    """Decode only the exact bounded canonical definition representation."""

    __slots__ = ()

    @property
    def profile_identity(
        self,
    ) -> ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity:
        return ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity(
            _DEFINITION_PROFILE
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowCpnDefinitionDecoder is not subclassable"
        )

    def decode(self, value: bytes) -> ColoredPetriNetDefinition:
        """Return the exact definition represented by canonical ``value``."""
        parsed = _parse_canonical_payload(value)
        if (
            set(parsed) != {"definition", "schema"}
            or parsed.get("schema") != _DEFINITION_PROFILE
            or type(parsed.get("definition")) is not dict
        ):
            raise ValueError(
                "definition representation has an invalid envelope"
            )
        try:
            definition = _definition_from_state(parsed["definition"])
        except (
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
            RecursionError,
        ) as exc:
            raise ValueError("definition representation is invalid") from exc
        if (
            ExperimentalWorkflowCpnDefinitionEncoder().encode(definition)
            != value
        ):
            raise ValueError("definition representation is not canonical")
        return definition


def _parse_canonical_payload(value: bytes) -> dict[str, object]:
    if type(value) is not bytes:
        raise TypeError("definition representation must be bytes")
    if not value:
        raise ValueError("definition representation must not be empty")
    if len(value) > _MAX_DEFINITION_BYTES:
        raise ValueError("definition representation exceeds its byte bound")
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(
            "definition representation must be UTF-8 JSON"
        ) from exc
    if type(parsed) is not dict:
        raise ValueError("definition representation must be a JSON object")
    try:
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError(
            "definition representation contains invalid JSON values"
        ) from exc
    if canonical != value:
        raise ValueError("definition representation must be canonical JSON")
    return parsed


def _inspect_definition_representation(
    value: bytes,
    definition_identity: ColoredPetriNetDefinitionIdentity,
) -> tuple[int, str]:
    """Validate canonical representation bytes and return length and digest."""
    definition = ExperimentalWorkflowCpnDefinitionDecoder().decode(value)
    if definition.identity != definition_identity:
        raise ValueError("definition_bytes differ from retained metadata")
    if not ColoredPetriNetDefinitionValidator().execute(definition).is_valid:
        raise ValueError("definition_bytes contain an invalid CPN definition")
    return len(value), sha256(value).hexdigest()


def _definition_state(
    definition: ColoredPetriNetDefinition,
) -> dict[str, object]:
    _validate_text(definition.identity.value, "definition identity")
    _validate_count(definition.colors, "colors")
    _validate_count(definition.places, "places")
    _validate_count(definition.transitions, "transitions")
    _validate_count(definition.arcs, "arcs")
    return {
        "identity": definition.identity.value,
        "selection_policy": definition.selection_policy.value,
        "colors": [
            {
                "identity": _bounded(item.identity.value, "color identity"),
                "allowed_value_kinds": [
                    kind.value for kind in item.allowed_value_kinds
                ],
            }
            for item in definition.colors
        ],
        "places": [
            {
                "identity": _bounded(item.identity.value, "place identity"),
                "allowed_color_identities": [
                    _bounded(value.value, "place color identity")
                    for value in item.allowed_color_identities
                ],
            }
            for item in definition.places
        ],
        "transitions": [
            {
                "identity": _bounded(
                    item.identity.value, "transition identity"
                ),
                "input_variable_identities": [
                    _bounded(value.value, "input variable identity")
                    for value in item.input_variable_identities
                ],
                "external_output_variable_identities": [
                    _bounded(value.value, "external variable identity")
                    for value in item.external_output_variable_identities
                ],
                "guard": _guard_state(item.guard, 0),
            }
            for item in definition.transitions
        ],
        "arcs": [_arc_state(item) for item in definition.arcs],
        "transition_priority": [
            _bounded(item.value, "priority transition identity")
            for item in definition.transition_priority
        ],
    }


def _arc_state(arc: ColoredPetriNetArcDefinition) -> dict[str, object]:
    if arc.input_inscription is not None:
        inscription: dict[str, object] = {
            "kind": "input",
            "value": _input_state(arc.input_inscription),
        }
    else:
        assert arc.output_inscription is not None
        _validate_count(arc.output_inscription.templates, "output templates")
        inscription = {
            "kind": "output",
            "value": {
                "templates": [
                    {
                        "color_identity": _bounded(
                            item.color_identity.value,
                            "template color identity",
                        ),
                        "value_expression": _value_expression_state(
                            item.value_expression
                        ),
                        "token_identity_expression": (
                            None
                            if item.token_identity_expression is None
                            else _value_expression_state(
                                item.token_identity_expression
                            )
                        ),
                    }
                    for item in arc.output_inscription.templates
                ]
            },
        }
    return {
        "identity": _bounded(arc.identity.value, "arc identity"),
        "place_identity": _bounded(
            arc.place_identity.value, "arc place identity"
        ),
        "transition_identity": _bounded(
            arc.transition_identity.value,
            "arc transition identity",
        ),
        "inscription": inscription,
    }


def _input_state(value: ColoredPetriNetInputInscription) -> dict[str, object]:
    _validate_count(value.patterns, "input patterns")
    patterns: list[dict[str, object]] = []
    for pattern in value.patterns:
        if type(pattern) is ColoredPetriNetTokenPattern:
            patterns.append(
                {
                    "kind": "token",
                    "variable_identity": _bounded(
                        pattern.variable_identity.value,
                        "pattern variable identity",
                    ),
                    "allowed_color_identities": [
                        _bounded(item.value, "pattern color identity")
                        for item in pattern.allowed_color_identities
                    ],
                }
            )
        elif type(pattern) is ColoredPetriNetInhibitorPattern:
            patterns.append(
                {
                    "kind": "inhibitor",
                    "allowed_color_identities": [
                        _bounded(item.value, "inhibitor color identity")
                        for item in pattern.allowed_color_identities
                    ],
                }
            )
        else:
            raise TypeError("input inscription contains an unsupported pattern")
    return {"mode": value.mode.value, "patterns": patterns}


def _guard_state(
    value: ColoredPetriNetGuardExpression,
    depth: int,
) -> dict[str, object]:
    if depth > _MAX_EXPRESSION_DEPTH:
        raise ValueError("guard expression exceeds its depth bound")
    _validate_count(value.operands, "guard operands")
    return {
        "operator": value.operator.value,
        "operands": [_guard_state(item, depth + 1) for item in value.operands],
        "left": (
            None if value.left is None else _value_expression_state(value.left)
        ),
        "right": (
            None
            if value.right is None
            else _value_expression_state(value.right)
        ),
    }


def _value_expression_state(
    value: ColoredPetriNetValueExpression,
) -> dict[str, object]:
    if value.kind is ColoredPetriNetValueExpressionKind.LITERAL:
        assert value.literal is not None
        return {
            "kind": value.kind.value,
            "literal": _value_state(value.literal),
        }
    assert value.variable_identity is not None
    return {
        "kind": value.kind.value,
        "variable_identity": _bounded(
            value.variable_identity.value,
            "expression variable identity",
        ),
    }


def _definition_from_state(value: object) -> ColoredPetriNetDefinition:
    state = _object(
        value,
        {
            "identity",
            "selection_policy",
            "colors",
            "places",
            "transitions",
            "arcs",
            "transition_priority",
        },
    )
    colors = tuple(_color_from_state(item) for item in _array(state["colors"]))
    places = tuple(_place_from_state(item) for item in _array(state["places"]))
    transitions = tuple(
        _transition_from_state(item) for item in _array(state["transitions"])
    )
    arcs = tuple(_arc_from_state(item) for item in _array(state["arcs"]))
    priorities = tuple(
        ColoredPetriNetTransitionIdentity(_text(item))
        for item in _array(state["transition_priority"])
    )
    _bounded_count(colors, "colors")
    _bounded_count(places, "places")
    _bounded_count(transitions, "transitions")
    _bounded_count(arcs, "arcs")
    _bounded_count(priorities, "transition priorities")
    return ColoredPetriNetDefinition(
        identity=ColoredPetriNetDefinitionIdentity(_text(state["identity"])),
        colors=colors,
        places=places,
        transitions=transitions,
        arcs=arcs,
        transition_priority=priorities,
        selection_policy=ColoredPetriNetSelectionPolicy(
            _text(state["selection_policy"])
        ),
    )


def _color_from_state(value: object) -> ColoredPetriNetColorDefinition:
    state = _object(value, {"identity", "allowed_value_kinds"})
    kinds = tuple(
        ColoredPetriNetValueKind(_text(item))
        for item in _array(state["allowed_value_kinds"])
    )
    _bounded_count(kinds, "allowed value kinds")
    return ColoredPetriNetColorDefinition(
        identity=ColoredPetriNetColorIdentity(_text(state["identity"])),
        allowed_value_kinds=kinds,
    )


def _place_from_state(value: object) -> ColoredPetriNetPlaceDefinition:
    state = _object(value, {"identity", "allowed_color_identities"})
    colors = tuple(
        ColoredPetriNetColorIdentity(_text(item))
        for item in _array(state["allowed_color_identities"])
    )
    _bounded_count(colors, "allowed color identities")
    return ColoredPetriNetPlaceDefinition(
        identity=ColoredPetriNetPlaceIdentity(_text(state["identity"])),
        allowed_color_identities=colors,
    )


def _transition_from_state(
    value: object,
) -> ColoredPetriNetTransitionDefinition:
    state = _object(
        value,
        {
            "identity",
            "input_variable_identities",
            "external_output_variable_identities",
            "guard",
        },
    )
    inputs = tuple(
        ColoredPetriNetBindingVariableIdentity(_text(item))
        for item in _array(state["input_variable_identities"])
    )
    outputs = tuple(
        ColoredPetriNetBindingVariableIdentity(_text(item))
        for item in _array(state["external_output_variable_identities"])
    )
    _bounded_count(inputs, "input variables")
    _bounded_count(outputs, "external output variables")
    return ColoredPetriNetTransitionDefinition(
        identity=ColoredPetriNetTransitionIdentity(_text(state["identity"])),
        input_variable_identities=inputs,
        external_output_variable_identities=outputs,
        guard=_guard_from_state(state["guard"], 0),
    )


def _arc_from_state(value: object) -> ColoredPetriNetArcDefinition:
    state = _object(
        value,
        {"identity", "place_identity", "transition_identity", "inscription"},
    )
    inscription = _object(state["inscription"], {"kind", "value"})
    kind = _text(inscription["kind"])
    identity = ColoredPetriNetArcIdentity(_text(state["identity"]))
    place_identity = ColoredPetriNetPlaceIdentity(
        _text(state["place_identity"])
    )
    transition_identity = ColoredPetriNetTransitionIdentity(
        _text(state["transition_identity"])
    )
    if kind == "input":
        return ColoredPetriNetArcDefinition(
            identity=identity,
            place_identity=place_identity,
            transition_identity=transition_identity,
            input_inscription=_input_from_state(inscription["value"]),
        )
    if kind == "output":
        output = _object(inscription["value"], {"templates"})
        templates = tuple(
            _template_from_state(item) for item in _array(output["templates"])
        )
        _bounded_count(templates, "output templates")
        return ColoredPetriNetArcDefinition(
            identity=identity,
            place_identity=place_identity,
            transition_identity=transition_identity,
            output_inscription=ColoredPetriNetOutputInscription(templates),
        )
    raise ValueError("arc inscription kind is unsupported")


def _input_from_state(value: object) -> ColoredPetriNetInputInscription:
    state = _object(value, {"mode", "patterns"})
    patterns = tuple(
        _pattern_from_state(item) for item in _array(state["patterns"])
    )
    _bounded_count(patterns, "input patterns")
    return ColoredPetriNetInputInscription(
        mode=ColoredPetriNetInputMode(_text(state["mode"])),
        patterns=patterns,
    )


def _pattern_from_state(
    value: object,
) -> ColoredPetriNetTokenPattern | ColoredPetriNetInhibitorPattern:
    if type(value) is not dict:
        raise TypeError("pattern must be an object")
    kind = _text(value.get("kind"))
    if kind == "token":
        state = _object(
            value,
            {"kind", "variable_identity", "allowed_color_identities"},
        )
        colors = _color_identities(state["allowed_color_identities"])
        return ColoredPetriNetTokenPattern(
            variable_identity=ColoredPetriNetBindingVariableIdentity(
                _text(state["variable_identity"])
            ),
            allowed_color_identities=colors,
        )
    if kind == "inhibitor":
        state = _object(value, {"kind", "allowed_color_identities"})
        return ColoredPetriNetInhibitorPattern(
            allowed_color_identities=_color_identities(
                state["allowed_color_identities"]
            )
        )
    raise ValueError("input pattern kind is unsupported")


def _color_identities(
    value: object,
) -> tuple[ColoredPetriNetColorIdentity, ...]:
    result = tuple(
        ColoredPetriNetColorIdentity(_text(item)) for item in _array(value)
    )
    _bounded_count(result, "pattern color identities")
    return result


def _template_from_state(value: object) -> ColoredPetriNetTokenTemplate:
    state = _object(
        value,
        {
            "color_identity",
            "value_expression",
            "token_identity_expression",
        },
    )
    token_identity = state["token_identity_expression"]
    return ColoredPetriNetTokenTemplate(
        color_identity=ColoredPetriNetColorIdentity(
            _text(state["color_identity"])
        ),
        value_expression=_value_expression_from_state(
            state["value_expression"]
        ),
        token_identity_expression=(
            None
            if token_identity is None
            else _value_expression_from_state(token_identity)
        ),
    )


def _guard_from_state(
    value: object, depth: int
) -> ColoredPetriNetGuardExpression:
    if depth > _MAX_EXPRESSION_DEPTH:
        raise ValueError("guard expression exceeds its depth bound")
    state = _object(value, {"operator", "operands", "left", "right"})
    operands = tuple(
        _guard_from_state(item, depth + 1) for item in _array(state["operands"])
    )
    _bounded_count(operands, "guard operands")
    left = state["left"]
    right = state["right"]
    return ColoredPetriNetGuardExpression(
        operator=ColoredPetriNetGuardOperator(_text(state["operator"])),
        operands=operands,
        left=(None if left is None else _value_expression_from_state(left)),
        right=(None if right is None else _value_expression_from_state(right)),
    )


def _value_expression_from_state(
    value: object,
) -> ColoredPetriNetValueExpression:
    if type(value) is not dict:
        raise TypeError("value expression must be an object")
    kind = ColoredPetriNetValueExpressionKind(_text(value.get("kind")))
    if kind is ColoredPetriNetValueExpressionKind.LITERAL:
        state = _object(value, {"kind", "literal"})
        return ColoredPetriNetValueExpression(
            kind=kind,
            literal=_value_from_state(state["literal"]),
        )
    state = _object(value, {"kind", "variable_identity"})
    return ColoredPetriNetValueExpression(
        kind=kind,
        variable_identity=ColoredPetriNetBindingVariableIdentity(
            _text(state["variable_identity"])
        ),
    )


def _validate_count(values: tuple[object, ...], label: str) -> None:
    if len(values) > _MAX_ITEMS:
        raise ValueError(f"{label} exceed their count bound")


__all__ = [
    "ExperimentalWorkflowCpnDefinitionDecoder",
    "ExperimentalWorkflowCpnDefinitionEncoder",
    "ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity",
]
