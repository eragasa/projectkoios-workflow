"""Shared closed scalar primitives for experimental canonical CPN codecs."""

from __future__ import annotations

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetValue,
    ColoredPetriNetValueKind,
)

MAX_CPN_REPRESENTATION_ITEMS = 65_536
MAX_CPN_REPRESENTATION_TEXT_BYTES = 512


def value_state(value: ColoredPetriNetValue) -> dict[str, object]:
    """Return the exact JSON-ready representation of one closed CPN value."""
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
            bounded_text(item, "string-sequence item") for item in active
        ]
    elif value.kind is ColoredPetriNetValueKind.STRING:
        assert type(active) is str
        represented = bounded_text(active, "string literal")
    else:
        represented = active
    return {"kind": value.kind.value, "value": represented}


def value_from_state(value: object) -> ColoredPetriNetValue:
    """Reconstruct one closed CPN value from its exact represented state."""
    state = closed_object(value, {"kind", "value"})
    kind = ColoredPetriNetValueKind(exact_text(state["kind"]))
    represented = state["value"]
    active: None | bool | int | float | str | tuple[str, ...]
    if kind is ColoredPetriNetValueKind.NONE:
        if represented is not None:
            raise TypeError("none value must be null")
        active = None
    elif kind is ColoredPetriNetValueKind.BOOLEAN:
        if type(represented) is not bool:
            raise TypeError("boolean value must be a Boolean")
        active = represented
    elif kind is ColoredPetriNetValueKind.INTEGER:
        text = exact_text(represented)
        active = int(text)
        if str(active) != text:
            raise ValueError("integer value is not canonical")
    elif kind is ColoredPetriNetValueKind.REAL:
        text = exact_text(represented)
        active = float.fromhex(text)
        if active.hex() != text:
            raise ValueError("real value is not canonical")
    elif kind is ColoredPetriNetValueKind.STRING:
        active = exact_text(represented)
    else:
        active = tuple(exact_text(item) for item in closed_array(represented))
        bounded_count(active, "string-sequence entries")
    return ColoredPetriNetValue(kind=kind, value=active)


def closed_object(value: object, fields: set[str]) -> dict[str, object]:
    """Require one exact closed JSON-object field set."""
    if type(value) is not dict or set(value) != fields:
        raise ValueError("object fields do not match the closed schema")
    return value


def closed_array(value: object) -> list[object]:
    """Require one bounded exact JSON array."""
    if type(value) is not list:
        raise TypeError("array value must be a list")
    if len(value) > MAX_CPN_REPRESENTATION_ITEMS:
        raise ValueError("array exceeds its count bound")
    return value


def exact_text(value: object) -> str:
    """Require one bounded exact built-in UTF-8 string."""
    if type(value) is not str:
        raise TypeError("text value must be a string")
    validate_text(value, "represented text")
    return value


def bounded_count(values: tuple[object, ...], label: str) -> None:
    """Require one tuple not to exceed the common representation count bound."""
    if len(values) > MAX_CPN_REPRESENTATION_ITEMS:
        raise ValueError(f"{label} exceed their count bound")


def bounded_text(value: str, label: str) -> str:
    """Validate and return one representation string."""
    validate_text(value, label)
    return value


def validate_text(value: str, label: str) -> None:
    """Require one nonempty exact built-in bounded UTF-8 string."""
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value:
        raise ValueError(f"{label} must not be empty")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8") from exc
    if len(encoded) > MAX_CPN_REPRESENTATION_TEXT_BYTES:
        raise ValueError(
            f"{label} exceeds {MAX_CPN_REPRESENTATION_TEXT_BYTES} bytes"
        )


__all__ = []
