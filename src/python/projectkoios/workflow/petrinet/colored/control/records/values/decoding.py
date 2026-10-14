"""Canonical tagged CPN value reconstruction."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....values import (
    CpnControlRecord,
    CpnControlRecordField,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
    CpnValue,
    CpnValueKind,
)
from ..schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
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
