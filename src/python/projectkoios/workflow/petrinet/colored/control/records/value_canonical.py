"""Canonical tagged CPN value projection and reconstruction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ...values import (
    CpnControlRecord,
    CpnControlRecordField,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
    CpnValue,
    CpnValueKind,
)
from .schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizerIdentity:
    """Identity of exact JSON-safe tagged-value projection semantics."""

    value: str = "projectkoios.workflow.cpn.value-canonicalizer:0.1"


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizationInput:
    """One exact generic value to project into canonical state."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalizationResult:
    """Exact immutable canonical bytes for one active value."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")


@final
class CpnValueCanonicalizer:
    """Directly project scalar and record values without owner callbacks."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueCanonicalizerIdentity:
        """Return the exact canonical projection identity."""
        return CpnValueCanonicalizerIdentity()

    def execute(
        self, canonicalization_input: CpnValueCanonicalizationInput
    ) -> CpnValueCanonicalizationResult:
        """Return an immutable canonical state using explicit scalar tags."""
        if type(canonicalization_input) is not CpnValueCanonicalizationInput:
            raise TypeError(
                "canonicalization_input must be CpnValueCanonicalizationInput"
            )
        root = canonicalization_input.value
        states: dict[int, object] = {}
        stack: list[tuple[CpnValue, bool, frozenset[int], int]] = [
            (root, False, frozenset(), 1)
        ]
        nodes = 0
        while stack:
            value, ready, ancestors, record_depth = stack.pop()
            if not ready:
                nodes += 1
                if nodes > 256:
                    raise ValueError("control-record value exceeds 256 nodes")
            if value.kind is CpnValueKind.CONTROL_RECORD and not ready:
                if record_depth > 8:
                    raise ValueError("control-record nesting exceeds depth 8")
                assert type(value.value) is CpnControlRecord
                marker = id(value.value)
                if marker in ancestors:
                    raise ValueError("cyclic control-record value")
                stack.append((value, True, ancestors, record_depth))
                for field in reversed(value.value.fields):
                    stack.append(
                        (
                            field.value,
                            False,
                            ancestors | {marker},
                            record_depth
                            + (
                                1
                                if field.value.kind
                                is CpnValueKind.CONTROL_RECORD
                                else 0
                            ),
                        )
                    )
                continue
            active: object
            if value.kind is CpnValueKind.INTEGER:
                active = str(value.value)
            elif value.kind is CpnValueKind.REAL:
                assert type(value.value) is float
                active = value.value.hex()
            elif value.kind is CpnValueKind.STRING_SEQUENCE:
                assert type(value.value) is tuple
                active = tuple(value.value)
            elif value.kind is CpnValueKind.CONTROL_RECORD:
                assert type(value.value) is CpnControlRecord
                active = (
                    "control_record",
                    value.value.type_identity.value,
                    tuple(
                        (
                            field.identity.value,
                            field.value.kind.value,
                            states[id(field.value)],
                        )
                        for field in value.value.fields
                    ),
                )
            else:
                assert value.value is None or type(value.value) in (bool, str)
                active = value.value
            states[id(value)] = active
        return CpnValueCanonicalizationResult(
            json.dumps(
                states[id(root)],
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalDecoderIdentity:
    """Identity of exact tagged canonical-value reconstruction semantics."""

    value: str = "projectkoios.workflow.cpn.value-canonical-decoder:0.1"


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalDecodingInput:
    """One tagged kind/state pair and exact retained record schemas."""

    kind: str
    canonical_bytes: bytes
    type_definitions: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.kind) is not str:
            raise TypeError("kind must be a string")
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if type(self.type_definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.type_definitions
        ):
            raise TypeError(
                "type_definitions must be a tuple of "
                "CpnControlRecordTypeDefinition"
            )


@dataclass(frozen=True, slots=True)
class CpnValueCanonicalDecodingResult:
    """One reconstructed and bounded generic value."""

    value: CpnValue

    def __post_init__(self) -> None:
        if type(self.value) is not CpnValue:
            raise TypeError("value must be CpnValue")


@final
class CpnValueCanonicalDecoder:
    """Directly reconstruct tagged scalar and control-record canonical state."""

    __slots__ = ()

    @property
    def identity(self) -> CpnValueCanonicalDecoderIdentity:
        """Return the exact decoding semantics identity."""
        return CpnValueCanonicalDecoderIdentity()

    def execute(
        self, decoding_input: CpnValueCanonicalDecodingInput
    ) -> CpnValueCanonicalDecodingResult:
        """Decode and schema-validate without callbacks or external resolution."""
        if type(decoding_input) is not CpnValueCanonicalDecodingInput:
            raise TypeError(
                "decoding_input must be CpnValueCanonicalDecodingInput"
            )
        try:
            active_root = json.loads(decoding_input.canonical_bytes)
            recanonical = json.dumps(
                active_root,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError("canonical value state is invalid JSON") from exc
        if recanonical != decoding_input.canonical_bytes:
            raise ValueError("canonical value state bytes are noncanonical")
        values: dict[tuple[str, ...], CpnValue] = {}
        stack: list[tuple[str, object, tuple[str, ...], bool, int]] = [
            (decoding_input.kind, active_root, ("value",), False, 1)
        ]
        nodes = 0
        while stack:
            kind_text, active, path, ready, record_depth = stack.pop()
            try:
                kind = CpnValueKind(kind_text)
            except ValueError as exc:
                raise ValueError(
                    f"unsupported value kind at {'.'.join(path)}"
                ) from exc
            if not ready:
                nodes += 1
                if nodes > 256:
                    raise ValueError("canonical value exceeds 256 nodes")
            if kind is CpnValueKind.CONTROL_RECORD and not ready:
                if record_depth > 8:
                    raise ValueError("control-record nesting exceeds depth 8")
                if (
                    type(active) is not list
                    or len(active) != 3
                    or active[0] != "control_record"
                    or type(active[1]) is not str
                    or type(active[2]) is not list
                ):
                    raise ValueError(
                        f"invalid control-record shape at {'.'.join(path)}"
                    )
                fields_state = active[2]
                assert type(fields_state) is list
                if not 1 <= len(fields_state) <= 64:
                    raise ValueError(
                        f"record field count is outside 1..64 at {'.'.join(path)}"
                    )
                stack.append((kind_text, active, path, True, record_depth))
                for index in range(len(fields_state) - 1, -1, -1):
                    field_state = fields_state[index]
                    if (
                        type(field_state) is not list
                        or len(field_state) != 3
                        or type(field_state[0]) is not str
                        or type(field_state[1]) is not str
                    ):
                        raise ValueError(
                            "field must contain exact identity, kind, and state"
                        )
                    stack.append(
                        (
                            field_state[1],
                            field_state[2],
                            path + ("fields", str(index), "value"),
                            False,
                            record_depth
                            + (
                                1
                                if field_state[1]
                                == CpnValueKind.CONTROL_RECORD.value
                                else 0
                            ),
                        )
                    )
                continue
            if kind is CpnValueKind.NONE:
                if active is not None:
                    raise ValueError("NONE canonical state must be null")
                represented: (
                    None
                    | bool
                    | int
                    | float
                    | str
                    | tuple[str, ...]
                    | CpnControlRecord
                ) = None
            elif kind is CpnValueKind.BOOLEAN:
                if type(active) is not bool:
                    raise ValueError("BOOLEAN canonical state must be Boolean")
                represented = active
            elif kind is CpnValueKind.INTEGER:
                if type(active) is not str:
                    raise ValueError("INTEGER canonical state must be a string")
                if (
                    active == "-0"
                    or (active.startswith("0") and active != "0")
                    or (active.startswith("-0") and active != "-0")
                ):
                    raise ValueError("INTEGER canonical state is noncanonical")
                try:
                    represented = int(active)
                except ValueError as exc:
                    raise ValueError(
                        "INTEGER canonical state is invalid"
                    ) from exc
                if str(represented) != active:
                    raise ValueError("INTEGER canonical state is noncanonical")
            elif kind is CpnValueKind.REAL:
                if type(active) is not str:
                    raise ValueError("REAL canonical state must be a string")
                try:
                    represented = float.fromhex(active)
                except ValueError as exc:
                    raise ValueError("REAL canonical state is invalid") from exc
                if represented.hex() != active:
                    raise ValueError("REAL canonical state is noncanonical")
            elif kind is CpnValueKind.STRING:
                if type(active) is not str:
                    raise ValueError("STRING canonical state must be a string")
                represented = active
            elif kind is CpnValueKind.STRING_SEQUENCE:
                if type(active) is not list or any(
                    type(item) is not str for item in active
                ):
                    raise ValueError(
                        "STRING_SEQUENCE canonical state must be a string array"
                    )
                represented = tuple(active)
            else:
                assert type(active) is list
                fields_state = active[2]
                assert type(fields_state) is list
                fields = tuple(
                    CpnControlRecordField(
                        CpnControlRecordFieldIdentity(field_state[0]),
                        values[path + ("fields", str(index), "value")],
                    )
                    for index, field_state in enumerate(fields_state)
                )
                represented = CpnControlRecord(
                    CpnControlRecordTypeIdentity(active[1]), fields
                )
            try:
                values[path] = CpnValue(kind, represented)
            except (OverflowError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"canonical value violates its kind at {'.'.join(path)}"
                ) from exc
        value = values[("value",)]
        if value.kind is CpnValueKind.CONTROL_RECORD:
            assert type(value.value) is CpnControlRecord
            validation = CpnControlRecordSchemaValidator().execute(
                CpnControlRecordSchemaValidationInput(
                    value.value, decoding_input.type_definitions
                )
            )
            if not validation.is_valid:
                raise ValueError(validation.issues[0].code.value)
        return CpnValueCanonicalDecodingResult(value)
