"""Canonical representation codec for experimental shadow-CPN definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetArcDefinition,
    ColoredPetriNetDefinition,
    ColoredPetriNetDefinitionIdentity,
    ColoredPetriNetGuardExpression,
    ColoredPetriNetInhibitorPattern,
    ColoredPetriNetInputInscription,
    ColoredPetriNetTokenPattern,
    ColoredPetriNetValue,
    ColoredPetriNetValueExpression,
    ColoredPetriNetValueExpressionKind,
    ColoredPetriNetValueKind,
)

_DEFINITION_PROFILE = "projectkoios.workflow.experimental-cpn-definition-json:0"
_MAX_DEFINITION_BYTES = 4 * 1024 * 1024
_MAX_TEXT_BYTES = 512
_MAX_EXPRESSION_DEPTH = 64
_MAX_ITEMS = 65_536


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


def _inspect_definition_representation(
    value: bytes,
    definition_identity: ColoredPetriNetDefinitionIdentity,
) -> tuple[int, str]:
    """Validate canonical representation bytes and return length and digest."""
    if type(value) is not bytes:
        raise TypeError("definition_bytes must be bytes")
    if not value:
        raise ValueError("definition_bytes must not be empty")
    if len(value) > _MAX_DEFINITION_BYTES:
        raise ValueError("definition_bytes exceed their bound")
    try:
        parsed = json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "definition_bytes must be canonical UTF-8 JSON"
        ) from exc
    if (
        type(parsed) is not dict
        or set(parsed) != {"definition", "schema"}
        or parsed.get("schema") != _DEFINITION_PROFILE
        or type(parsed.get("definition")) is not dict
        or parsed["definition"].get("identity") != definition_identity.value
    ):
        raise ValueError("definition_bytes differ from retained metadata")
    canonical = json.dumps(
        parsed,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if canonical != value:
        raise ValueError("definition_bytes must be canonical JSON")
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


def _value_state(value: ColoredPetriNetValue) -> dict[str, object]:
    active = value.value
    if value.kind is ColoredPetriNetValueKind.REAL:
        assert type(active) is float
        represented: object = active.hex()
    elif value.kind is ColoredPetriNetValueKind.INTEGER:
        assert type(active) is int
        represented = str(active)
    elif value.kind is ColoredPetriNetValueKind.STRING_SEQUENCE:
        assert type(active) is tuple
        represented = [
            _bounded(item, "string-sequence item") for item in active
        ]
    elif value.kind is ColoredPetriNetValueKind.STRING:
        assert type(active) is str
        represented = _bounded(active, "string literal")
    else:
        represented = active
    return {"kind": value.kind.value, "value": represented}


def _validate_count(values: tuple[object, ...], label: str) -> None:
    if len(values) > _MAX_ITEMS:
        raise ValueError(f"{label} exceed their count bound")


def _bounded(value: str, label: str) -> str:
    _validate_text(value, label)
    return value


def _validate_text(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value:
        raise ValueError(f"{label} must not be empty")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8") from exc
    if len(encoded) > _MAX_TEXT_BYTES:
        raise ValueError(f"{label} exceeds {_MAX_TEXT_BYTES} bytes")


__all__ = [
    "ExperimentalWorkflowCpnDefinitionEncoder",
    "ExperimentalWorkflowCpnDefinitionRepresentationProfileIdentity",
]
