"""Strict canonical transport for complete flat CPN definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from enum import StrEnum
from hashlib import sha256
from string import hexdigits
from typing import final

from .json import CpnCanonicalJsonParser, CpnCanonicalJsonParsingInput
from .expressions.guards.canonicalization import (
    CpnGuardCanonicalizationInput,
    CpnGuardCanonicalizer,
)
from .expressions.guards.decoding import (
    CpnGuardCanonicalDecoder,
    CpnGuardCanonicalDecodingInput,
)
from .expressions.values.canonicalization import (
    CpnValueExpressionCanonicalizationInput,
    CpnValueExpressionCanonicalizer,
)
from .expressions.values.decoding import (
    CpnValueExpressionCanonicalDecoder,
    CpnValueExpressionCanonicalDecodingInput,
)
from ..definitions import (
    CpnArcDefinition,
    CpnArcIdentity,
    CpnColorDefinition,
    CpnDefinition,
    CpnDefinitionIdentity,
    CpnPlaceDefinition,
    CpnPlaceIdentity,
    CpnSelectionPolicy,
    CpnTransitionDefinition,
    CpnTransitionIdentity,
)
from ..expressions.grammar import (
    CpnBindingVariableIdentity,
    CpnInhibitorPattern,
    CpnInputInscription,
    CpnInputMode,
    CpnOutputInscription,
    CpnTokenPattern,
    CpnTokenTemplate,
)
from ..values import (
    CpnControlRecordFieldDefinition,
    CpnControlRecordFieldIdentity,
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
    CpnColorIdentity,
    CpnValueKind,
)

_DEFINITION_PROFILE = "projectkoios/workflow/cpn-definition/v0.1"


class CpnCanonicalDefinitionCodecErrorCode(StrEnum):
    """Closed canonical-definition transport failures."""

    INVALID_ARGUMENT = "invalid_argument"
    INVALID_DEFINITION = "invalid_definition"
    INVALID_DOCUMENT = "invalid_document"
    UNSUPPORTED_PROFILE = "unsupported_profile"
    IDENTITY_MISMATCH = "identity_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    NONCANONICAL_RECONSTRUCTION = "noncanonical_reconstruction"


class CpnCanonicalDefinitionCodecError(ValueError):
    """One translated canonical-definition transport failure."""

    def __init__(
        self,
        code: CpnCanonicalDefinitionCodecErrorCode,
        path: tuple[str, ...],
        message: str,
    ) -> None:
        self.code = code
        self.path = path
        self.message = message
        rendered = ".".join(path) if path else "<root>"
        super().__init__(f"{code.value} at {rendered}: {message}")


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinitionIdentity:
    """Content-derived identity of exact canonical flat-definition bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-definition:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError("identity must end in lowercase SHA-256")


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinition:
    """Exact bytes plus constructor-derived content correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = dataclass_field(init=False)
    sha256: str = dataclass_field(init=False)
    identity: CpnCanonicalDefinitionIdentity = dataclass_field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _DEFINITION_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalDefinitionIdentity(
                "projectkoios.workflow.cpn-definition:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinitionEncodingInput:
    """One structurally valid flat generic CPN definition."""

    definition: CpnDefinition

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinitionDecodingInput:
    """One exact correlated canonical-definition document."""

    document: CpnCanonicalDefinition

    def __post_init__(self) -> None:
        if type(self.document) is not CpnCanonicalDefinition:
            raise TypeError("document must be CpnCanonicalDefinition")


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinitionDecodingResult:
    """One reconstructed flat definition and its exact transport."""

    definition: CpnDefinition
    document: CpnCanonicalDefinition


@dataclass(frozen=True, slots=True)
class CpnCanonicalDefinitionCodecIdentity:
    """Identity of exact flat-definition canonical transport semantics."""

    value: str = "projectkoios.workflow.cpn.canonical-definition-codec:0.1"


@final
class CpnCanonicalDefinitionCodec:
    """Directly encode/decode complete bounded generic CPN definitions."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalDefinitionCodecIdentity:
        """Return exact codec semantics identity."""
        return CpnCanonicalDefinitionCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalDefinitionEncodingInput
    ) -> CpnCanonicalDefinition:
        """Validate and encode one complete definition with no owner callbacks."""
        if type(encoding_input) is not CpnCanonicalDefinitionEncodingInput:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnCanonicalDefinitionEncodingInput",
            )
        definition = encoding_input.definition
        type_states = []
        for record_type in definition.control_record_types:
            fields = []
            for field in record_type.fields:
                fields.append(
                    [
                        field.identity.value,
                        field.value_kind.value
                        if field.value_kind is not None
                        else None,
                        (
                            field.record_type_identity.value
                            if field.record_type_identity is not None
                            else None
                        ),
                        field.reference_role_identity,
                    ]
                )
            type_states.append(
                [
                    record_type.identity.value,
                    str(record_type.contract_version),
                    fields,
                ]
            )
        transition_states = []
        for transition in definition.transitions:
            guard_state = json.loads(
                CpnGuardCanonicalizer()
                .execute(
                    CpnGuardCanonicalizationInput(
                        transition.guard, definition.control_record_types
                    )
                )
                .canonical_bytes
            )
            transition_states.append(
                [
                    transition.identity.value,
                    [
                        item.value
                        for item in transition.input_variable_identities
                    ],
                    [
                        item.value
                        for item in transition.external_output_variable_identities
                    ],
                    guard_state,
                ]
            )
        arc_states = []
        for arc in definition.arcs:
            input_state: object = None
            output_state: object = None
            if arc.input_inscription is not None:
                patterns: list[object] = []
                for pattern in arc.input_inscription.patterns:
                    if type(pattern) is CpnTokenPattern:
                        patterns.append(
                            [
                                "binding",
                                pattern.variable_identity.value,
                                [
                                    item.value
                                    for item in pattern.allowed_color_identities
                                ],
                            ]
                        )
                    else:
                        assert type(pattern) is CpnInhibitorPattern
                        patterns.append(
                            [
                                "inhibitor",
                                None,
                                [
                                    item.value
                                    for item in pattern.allowed_color_identities
                                ],
                            ]
                        )
                input_state = [arc.input_inscription.mode.value, patterns]
            else:
                assert arc.output_inscription is not None
                templates = []
                for template in arc.output_inscription.templates:
                    value_expression = json.loads(
                        CpnValueExpressionCanonicalizer()
                        .execute(
                            CpnValueExpressionCanonicalizationInput(
                                template.value_expression,
                                definition.control_record_types,
                            )
                        )
                        .canonical_bytes
                    )
                    token_expression = (
                        json.loads(
                            CpnValueExpressionCanonicalizer()
                            .execute(
                                CpnValueExpressionCanonicalizationInput(
                                    template.token_identity_expression,
                                    definition.control_record_types,
                                )
                            )
                            .canonical_bytes
                        )
                        if template.token_identity_expression is not None
                        else None
                    )
                    templates.append(
                        [
                            template.color_identity.value,
                            value_expression,
                            token_expression,
                        ]
                    )
                output_state = templates
            arc_states.append(
                [
                    arc.identity.value,
                    arc.place_identity.value,
                    arc.transition_identity.value,
                    input_state,
                    output_state,
                ]
            )
        state = {
            "arcs": arc_states,
            "colors": [
                [
                    color.identity.value,
                    [item.value for item in color.allowed_value_kinds],
                    [
                        item.value
                        for item in color.allowed_control_record_type_identities
                    ],
                ]
                for color in definition.colors
            ],
            "definition_identity": definition.identity.value,
            "places": [
                [
                    place.identity.value,
                    [item.value for item in place.allowed_color_identities],
                ]
                for place in definition.places
            ],
            "profile": _DEFINITION_PROFILE,
            "record_types": type_states,
            "selection_policy": definition.selection_policy.value,
            "transition_priority": [
                item.value for item in definition.transition_priority
            ],
            "transitions": transition_states,
        }
        try:
            canonical_bytes = json.dumps(
                state,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.INVALID_DEFINITION,
                (),
                "definition cannot be represented as canonical UTF-8 JSON",
            ) from exc
        return CpnCanonicalDefinition(canonical_bytes)

    def decode(
        self, decoding_input: CpnCanonicalDefinitionDecodingInput
    ) -> CpnCanonicalDefinitionDecodingResult:
        """Verify correlations, strictly parse, reconstruct, and re-encode."""
        if type(decoding_input) is not CpnCanonicalDefinitionDecodingInput:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnCanonicalDefinitionDecodingInput",
            )
        document = decoding_input.document
        digest = sha256(document.canonical_bytes).hexdigest()
        if document.sha256 != digest:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.DIGEST_MISMATCH,
                ("sha256",),
                "declared digest differs from exact bytes",
            )
        expected_identity = "projectkoios.workflow.cpn-definition:0.1:" + digest
        if document.identity.value != expected_identity:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.IDENTITY_MISMATCH,
                ("identity",),
                "declared identity differs from exact bytes",
            )
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            if type(state) is not dict or set(state) != {
                "arcs",
                "colors",
                "definition_identity",
                "places",
                "profile",
                "record_types",
                "selection_policy",
                "transition_priority",
                "transitions",
            }:
                raise TypeError("root shape")
            if state["profile"] != _DEFINITION_PROFILE:
                raise CpnCanonicalDefinitionCodecError(
                    CpnCanonicalDefinitionCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical-definition profile",
                )
            for name in (
                "arcs",
                "colors",
                "places",
                "record_types",
                "transition_priority",
                "transitions",
            ):
                if type(state[name]) is not list:
                    raise TypeError(f"{name} must be an array")
            if (
                type(state["definition_identity"]) is not str
                or type(state["selection_policy"]) is not str
            ):
                raise TypeError("scalar root fields")
            record_types = []
            for item in state["record_types"]:
                if (
                    type(item) is not list
                    or len(item) != 3
                    or type(item[0]) is not str
                    or type(item[1]) is not str
                    or type(item[2]) is not list
                ):
                    raise TypeError("record type shape")
                fields = []
                for field in item[2]:
                    if (
                        type(field) is not list
                        or len(field) != 4
                        or type(field[0]) is not str
                        or (field[1] is not None and type(field[1]) is not str)
                        or (field[2] is not None and type(field[2]) is not str)
                        or (field[3] is not None and type(field[3]) is not str)
                    ):
                        raise TypeError("record field shape")
                    fields.append(
                        CpnControlRecordFieldDefinition(
                            CpnControlRecordFieldIdentity(field[0]),
                            (
                                CpnValueKind(field[1])
                                if field[1] is not None
                                else None
                            ),
                            (
                                CpnControlRecordTypeIdentity(field[2])
                                if field[2] is not None
                                else None
                            ),
                            (field[3] if field[3] is not None else None),
                        )
                    )
                record_types.append(
                    CpnControlRecordTypeDefinition(
                        CpnControlRecordTypeIdentity(item[0]),
                        int(item[1]),
                        tuple(fields),
                    )
                )
            retained_types = tuple(record_types)
            colors = []
            for item in state["colors"]:
                if (
                    type(item) is not list
                    or len(item) != 3
                    or type(item[0]) is not str
                    or type(item[1]) is not list
                    or type(item[2]) is not list
                    or any(
                        type(value) is not str for value in item[1] + item[2]
                    )
                ):
                    raise TypeError("color shape")
                colors.append(
                    CpnColorDefinition(
                        CpnColorIdentity(item[0]),
                        tuple(CpnValueKind(value) for value in item[1]),
                        tuple(
                            CpnControlRecordTypeIdentity(value)
                            for value in item[2]
                        ),
                    )
                )
            places = []
            for item in state["places"]:
                if (
                    type(item) is not list
                    or len(item) != 2
                    or type(item[0]) is not str
                    or type(item[1]) is not list
                    or any(type(value) is not str for value in item[1])
                ):
                    raise TypeError("place shape")
                places.append(
                    CpnPlaceDefinition(
                        CpnPlaceIdentity(item[0]),
                        tuple(CpnColorIdentity(value) for value in item[1]),
                    )
                )
            transitions = []
            for item in state["transitions"]:
                if (
                    type(item) is not list
                    or len(item) != 4
                    or type(item[0]) is not str
                    or type(item[1]) is not list
                    or type(item[2]) is not list
                    or any(
                        type(value) is not str for value in item[1] + item[2]
                    )
                ):
                    raise TypeError("transition shape")
                guard = (
                    CpnGuardCanonicalDecoder()
                    .execute(
                        CpnGuardCanonicalDecodingInput(
                            json.dumps(
                                item[3],
                                ensure_ascii=False,
                                allow_nan=False,
                                separators=(",", ":"),
                            ).encode("utf-8"),
                            retained_types,
                        )
                    )
                    .guard
                )
                transitions.append(
                    CpnTransitionDefinition(
                        CpnTransitionIdentity(item[0]),
                        tuple(
                            CpnBindingVariableIdentity(value)
                            for value in item[1]
                        ),
                        tuple(
                            CpnBindingVariableIdentity(value)
                            for value in item[2]
                        ),
                        guard,
                    )
                )
            arcs = []
            for item in state["arcs"]:
                if (
                    type(item) is not list
                    or len(item) != 5
                    or any(type(item[index]) is not str for index in (0, 1, 2))
                    or ((item[3] is None) == (item[4] is None))
                ):
                    raise TypeError("arc shape")
                input_inscription = None
                output_inscription = None
                if item[3] is not None:
                    input_item = item[3]
                    if (
                        type(input_item) is not list
                        or len(input_item) != 2
                        or type(input_item[0]) is not str
                        or type(input_item[1]) is not list
                    ):
                        raise TypeError("input inscription shape")
                    mode = CpnInputMode(input_item[0])
                    patterns: list[CpnTokenPattern | CpnInhibitorPattern] = []
                    for pattern in input_item[1]:
                        if (
                            type(pattern) is not list
                            or len(pattern) != 3
                            or pattern[0] not in ("binding", "inhibitor")
                            or type(pattern[2]) is not list
                            or any(
                                type(value) is not str for value in pattern[2]
                            )
                        ):
                            raise TypeError("input pattern shape")
                        admitted = tuple(
                            CpnColorIdentity(value) for value in pattern[2]
                        )
                        if pattern[0] == "binding":
                            if type(pattern[1]) is not str:
                                raise TypeError("binding pattern variable")
                            patterns.append(
                                CpnTokenPattern(
                                    CpnBindingVariableIdentity(pattern[1]),
                                    admitted,
                                )
                            )
                        else:
                            if pattern[1] is not None:
                                raise TypeError(
                                    "inhibitor variable must be null"
                                )
                            patterns.append(CpnInhibitorPattern(admitted))
                    input_inscription = CpnInputInscription(
                        mode, tuple(patterns)
                    )
                else:
                    if type(item[4]) is not list:
                        raise TypeError("output inscription shape")
                    templates = []
                    for template in item[4]:
                        if (
                            type(template) is not list
                            or len(template) != 3
                            or type(template[0]) is not str
                        ):
                            raise TypeError("output template shape")
                        value_expression = (
                            CpnValueExpressionCanonicalDecoder()
                            .execute(
                                CpnValueExpressionCanonicalDecodingInput(
                                    json.dumps(
                                        template[1],
                                        ensure_ascii=False,
                                        allow_nan=False,
                                        separators=(",", ":"),
                                    ).encode("utf-8"),
                                    retained_types,
                                )
                            )
                            .expression
                        )
                        token_expression = (
                            CpnValueExpressionCanonicalDecoder()
                            .execute(
                                CpnValueExpressionCanonicalDecodingInput(
                                    json.dumps(
                                        template[2],
                                        ensure_ascii=False,
                                        allow_nan=False,
                                        separators=(",", ":"),
                                    ).encode("utf-8"),
                                    retained_types,
                                )
                            )
                            .expression
                            if template[2] is not None
                            else None
                        )
                        templates.append(
                            CpnTokenTemplate(
                                CpnColorIdentity(template[0]),
                                value_expression,
                                token_expression,
                            )
                        )
                    output_inscription = CpnOutputInscription(tuple(templates))
                arcs.append(
                    CpnArcDefinition(
                        CpnArcIdentity(item[0]),
                        CpnPlaceIdentity(item[1]),
                        CpnTransitionIdentity(item[2]),
                        input_inscription,
                        output_inscription,
                    )
                )
            if any(
                type(value) is not str for value in state["transition_priority"]
            ):
                raise TypeError("transition priority")
            definition = CpnDefinition(
                CpnDefinitionIdentity(state["definition_identity"]),
                tuple(colors),
                tuple(places),
                tuple(transitions),
                tuple(arcs),
                tuple(
                    CpnTransitionIdentity(value)
                    for value in state["transition_priority"]
                ),
                CpnSelectionPolicy(state["selection_policy"]),
                retained_types,
            )
        except CpnCanonicalDefinitionCodecError:
            raise
        except (
            KeyError,
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.INVALID_DOCUMENT,
                (),
                "document violates the complete flat-definition representation",
            ) from exc
        reconstructed = self.encode(
            CpnCanonicalDefinitionEncodingInput(definition)
        )
        if reconstructed != document:
            raise CpnCanonicalDefinitionCodecError(
                CpnCanonicalDefinitionCodecErrorCode.NONCANONICAL_RECONSTRUCTION,
                (),
                "reconstructed definition does not reproduce every exact byte",
            )
        return CpnCanonicalDefinitionDecodingResult(definition, document)
