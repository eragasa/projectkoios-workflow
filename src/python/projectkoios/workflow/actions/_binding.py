"""Canonical encoding of exact ordered shadow CPN bindings."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import final

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetBindingAssignment,
    ColoredPetriNetBindingVariableIdentity,
    ColoredPetriNetTransitionIdentity,
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

_BINDING_SCHEMA = "projectkoios.workflow.experimental-selected-binding:1"
_BINDING_PROFILE = (
    "projectkoios.workflow.experimental-selected-binding-canonical-json:1"
)
_MAX_ASSIGNMENTS = 256
_MAX_BINDING_BYTES = 65536
_MAX_IDENTITY_BYTES = 512
_MAX_STRING_BYTES = 4096
_MAX_STRING_SEQUENCE = 256


@final
class ExperimentalWorkflowSelectedBindingEncoder:
    """Encode one exact ordered shadow CPN binding with closed type tags."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowSelectedBindingEncoder is not subclassable"
        )

    @property
    def profile_identity(self) -> str:
        """Return the exact private representation-profile identity."""
        return _BINDING_PROFILE

    def encode(self, value: ColoredPetriNetBinding) -> bytes:
        """Return bounded canonical JSON preserving assignment order."""
        validated = _reconstruct_binding(value)
        if validated != value:
            raise ValueError("selected binding differs after validation")
        if len(value.assignments) > _MAX_ASSIGNMENTS:
            raise ValueError("selected binding exceeds 256 assignments")
        document = {
            "assignments": [
                {
                    "kind": assignment.value.kind.value,
                    "value": _value_state(assignment.value),
                    "variable_identity": assignment.variable_identity.value,
                }
                for assignment in value.assignments
            ],
            "schema_identity": _BINDING_SCHEMA,
            "transition_identity": value.transition_identity.value,
        }
        payload = json.dumps(
            document,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if not payload or len(payload) > _MAX_BINDING_BYTES:
            raise ValueError("selected binding exceeds 65536 canonical bytes")
        return payload

    def sha256(self, value: ColoredPetriNetBinding) -> str:
        """Return SHA-256 over the exact canonical selected-binding bytes."""
        return hashlib.sha256(self.encode(value)).hexdigest()


def _reconstruct_binding(
    value: ColoredPetriNetBinding,
) -> ColoredPetriNetBinding:
    if type(value) is not ColoredPetriNetBinding:
        raise TypeError("value must be ColoredPetriNetBinding")
    _validate_identity_text(
        value.transition_identity.value,
        "transition identity",
    )
    assignments: list[ColoredPetriNetBindingAssignment] = []
    for index, assignment in enumerate(value.assignments):
        if type(assignment) is not ColoredPetriNetBindingAssignment:
            raise TypeError(
                f"selected binding assignment {index} has the wrong type"
            )
        _validate_identity_text(
            assignment.variable_identity.value,
            f"assignment {index} variable identity",
        )
        validated_value = _reconstruct_value(assignment.value, index)
        assignments.append(
            ColoredPetriNetBindingAssignment(
                variable_identity=ColoredPetriNetBindingVariableIdentity(
                    assignment.variable_identity.value
                ),
                value=validated_value,
            )
        )
    return ColoredPetriNetBinding(
        transition_identity=ColoredPetriNetTransitionIdentity(
            value.transition_identity.value
        ),
        assignments=tuple(assignments),
    )


def _reconstruct_value(
    value: ColoredPetriNetValue,
    assignment_index: int,
) -> ColoredPetriNetValue:
    if type(value) is not ColoredPetriNetValue:
        raise TypeError(
            "selected binding assignment "
            f"{assignment_index} value has wrong type"
        )
    active = value.value
    if value.kind is ColoredPetriNetValueKind.STRING:
        assert type(active) is str
        _validate_string(active, f"assignment {assignment_index} string")
    elif value.kind is ColoredPetriNetValueKind.STRING_SEQUENCE:
        assert type(active) is tuple
        if len(active) > _MAX_STRING_SEQUENCE:
            raise ValueError("string sequence exceeds 256 entries")
        for item_index, item in enumerate(active):
            _validate_string(
                item,
                f"assignment {assignment_index} string sequence {item_index}",
            )
    return ColoredPetriNetValue(kind=value.kind, value=active)


def _value_state(value: ColoredPetriNetValue) -> object:
    active = value.value
    if value.kind is ColoredPetriNetValueKind.REAL:
        assert type(active) is float
        return active.hex()
    if value.kind is ColoredPetriNetValueKind.INTEGER:
        assert type(active) is int
        return str(active)
    if value.kind is ColoredPetriNetValueKind.STRING_SEQUENCE:
        assert type(active) is tuple
        return list(active)
    return active


def _validate_identity_text(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and stripped")
    payload = value.encode("utf-8")
    if len(payload) > _MAX_IDENTITY_BYTES:
        raise ValueError(f"{label} exceeds 512 UTF-8 bytes")
    if any(
        character.isspace() or unicodedata.category(character) == "Cc"
        for character in value
    ):
        raise ValueError(f"{label} must not contain whitespace or controls")


def _validate_string(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if len(value.encode("utf-8")) > _MAX_STRING_BYTES:
        raise ValueError(f"{label} exceeds 4096 UTF-8 bytes")


__all__ = ["ExperimentalWorkflowSelectedBindingEncoder"]
