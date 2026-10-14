"""Control-record type-graph validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ....values import (
    CpnControlRecordTypeDefinition,
    CpnControlRecordTypeIdentity,
)
from ..findings import (
    CpnControlRecordValidationIssue,
    CpnControlRecordValidationIssueCode,
    CpnControlRecordValidationResult,
)


@dataclass(frozen=True, slots=True)
class CpnControlRecordTypeGraphValidatorIdentity:
    """Identity of exact type-graph validation semantics."""

    value: str = (
        "projectkoios.workflow.cpn.control-record-type-graph-validator:0.1"
    )

    def __post_init__(self) -> None:
        if type(self.value) is not str or not self.value:
            raise TypeError("validator identity must be a nonempty string")


@dataclass(frozen=True, slots=True)
class CpnControlRecordTypeGraphValidationInput:
    """Exact immutable input to type-graph validation."""

    definitions: tuple[CpnControlRecordTypeDefinition, ...]

    def __post_init__(self) -> None:
        if type(self.definitions) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.definitions
        ):
            raise TypeError(
                "definitions must be a tuple of CpnControlRecordTypeDefinition"
            )


@final
class CpnControlRecordTypeGraphValidator:
    """Directly validate closed record schemas and their acyclic type graph."""

    __slots__ = ()

    @property
    def identity(self) -> CpnControlRecordTypeGraphValidatorIdentity:
        """Return the exact semantics identity."""
        return CpnControlRecordTypeGraphValidatorIdentity()

    def execute(
        self, validation_input: CpnControlRecordTypeGraphValidationInput
    ) -> CpnControlRecordValidationResult:
        """Return every bounded type-definition and graph finding."""
        if (
            type(validation_input)
            is not CpnControlRecordTypeGraphValidationInput
        ):
            raise TypeError(
                "validation_input must be "
                "CpnControlRecordTypeGraphValidationInput"
            )
        definitions = validation_input.definitions
        issues: list[CpnControlRecordValidationIssue] = []
        if len(definitions) > 256:
            issues.append(
                CpnControlRecordValidationIssue(
                    CpnControlRecordValidationIssueCode.TOO_MANY_TYPE_DEFINITIONS,
                    ("control_record_types",),
                    "a definition may contain at most 256 record types",
                )
            )
        identities = tuple(item.identity for item in definitions)
        if len(set(identities)) != len(identities):
            issues.append(
                CpnControlRecordValidationIssue(
                    CpnControlRecordValidationIssueCode.DUPLICATE_TYPE_IDENTITY,
                    ("control_record_types",),
                    "record type identities must be unique",
                )
            )
        by_identity = {item.identity: item for item in definitions}
        for definition in definitions:
            field_names = tuple(
                item.identity.value for item in definition.fields
            )
            definition_path = (
                "control_record_types",
                definition.identity.value,
                "fields",
            )
            if not 1 <= len(definition.fields) <= 64:
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.INVALID_FIELD_COUNT,
                        definition_path,
                        "a record type must contain 1..64 fields",
                    )
                )
            if len(set(field_names)) != len(field_names):
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.DUPLICATE_FIELD_IDENTITY,
                        definition_path,
                        "record type field identities must be unique",
                    )
                )
            if field_names != tuple(sorted(field_names)):
                issues.append(
                    CpnControlRecordValidationIssue(
                        CpnControlRecordValidationIssueCode.NONCANONICAL_FIELD_ORDER,
                        definition_path,
                        "record type fields must use lexical identity order",
                    )
                )
            for field in definition.fields:
                target = field.record_type_identity
                if target is not None and target not in by_identity:
                    issues.append(
                        CpnControlRecordValidationIssue(
                            CpnControlRecordValidationIssueCode.UNKNOWN_RECORD_TYPE,
                            definition_path + (field.identity.value,),
                            "nested field references an unknown record type",
                        )
                    )
        for root in identities:
            stack: list[
                tuple[
                    CpnControlRecordTypeIdentity,
                    tuple[CpnControlRecordTypeIdentity, ...],
                    int,
                ]
            ] = [(root, (), 1)]
            while stack:
                identity, ancestors, depth = stack.pop()
                traversal_path = tuple(
                    item.value for item in ancestors + (identity,)
                )
                if identity in ancestors:
                    issues.append(
                        CpnControlRecordValidationIssue(
                            CpnControlRecordValidationIssueCode.CYCLIC_TYPE_GRAPH,
                            traversal_path,
                            "record type graph must be acyclic",
                        )
                    )
                    continue
                if depth > 8:
                    issues.append(
                        CpnControlRecordValidationIssue(
                            CpnControlRecordValidationIssueCode.TYPE_GRAPH_TOO_DEEP,
                            traversal_path,
                            "record type graph exceeds depth 8",
                        )
                    )
                    continue
                current_definition = by_identity.get(identity)
                if current_definition is None:
                    continue
                for field in reversed(current_definition.fields):
                    if field.record_type_identity is not None:
                        stack.append(
                            (
                                field.record_type_identity,
                                ancestors + (identity,),
                                depth + 1,
                            )
                        )
        return CpnControlRecordValidationResult(tuple(issues))
