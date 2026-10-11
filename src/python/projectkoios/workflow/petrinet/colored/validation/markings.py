"""Complete CPN marking compatibility validation."""

from __future__ import annotations

from dataclasses import dataclass

from ..control.records.schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)
from ..definitions import CpnDefinition
from ..markings import CpnMarking
from ..values import CpnControlRecord, CpnValueKind
from .findings import (
    CpnValidationIssue,
    CpnValidationIssueCode,
    CpnValidationResult,
)


@dataclass(frozen=True, slots=True)
class CpnMarkingValidatorIdentity:
    """Identity of exact generic marking-validation semantics."""

    value: str = "projectkoios.workflow.cpn.marking-validator:0.1"


@dataclass(frozen=True, slots=True)
class CpnMarkingValidationInput:
    """Complete immutable definition-relative marking validation request."""

    definition: CpnDefinition
    marking: CpnMarking

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.marking) is not CpnMarking:
            raise TypeError("marking must be CpnMarking")


class CpnMarkingValidator:
    """ActionObject for definition-relative generic marking validation."""

    __slots__ = ()

    @property
    def identity(self) -> CpnMarkingValidatorIdentity:
        """Return exact marking-validation semantics identity."""
        return CpnMarkingValidatorIdentity()

    def execute(
        self, validation_input: CpnMarkingValidationInput
    ) -> CpnValidationResult:
        """Return all declared definition-relative marking findings.

        Parameters
        ----------
        definition
            Exact immutable generic definition providing place/color contracts.
        marking
            Exact immutable semantic marking to inspect.

        Returns
        -------
        CpnValidationResult
            Complete canonically ordered structural findings.

        Raises
        ------
        TypeError
            Either argument has the wrong exact nominal type.
        """
        if type(validation_input) is not CpnMarkingValidationInput:
            raise TypeError(
                "validation_input must be CpnMarkingValidationInput"
            )
        definition = validation_input.definition
        marking = validation_input.marking
        issues: list[CpnValidationIssue] = []
        places = {item.identity: item for item in definition.places}
        colors = {item.identity: item for item in definition.colors}
        if marking.definition_identity != definition.identity:
            issues.append(
                CpnValidationIssue(
                    CpnValidationIssueCode.DEFINITION_IDENTITY_MISMATCH,
                    ("marking", "definition_identity"),
                    (
                        marking.definition_identity.value,
                        definition.identity.value,
                    ),
                    "marking and supplied definition identities differ",
                )
            )
        marking_places = {item.place_identity for item in marking.places}
        definition_places = set(places)
        if marking_places != definition_places:
            issues.append(
                CpnValidationIssue(
                    CpnValidationIssueCode.PLACE_SET_MISMATCH,
                    ("marking", "places"),
                    tuple(
                        item.value
                        for item in marking_places ^ definition_places
                    ),
                    "marking place set differs from definition place set",
                )
            )
        for place_marking in marking.places:
            place = places.get(place_marking.place_identity)
            for index, token in enumerate(place_marking.tokens):
                path = (
                    "marking",
                    "places",
                    place_marking.place_identity.value,
                    "tokens",
                    str(index),
                )
                color = colors.get(token.color_identity)
                if color is None:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.UNKNOWN_COLOR,
                            path + ("color",),
                            (token.color_identity.value,),
                            "token references an unknown color",
                        )
                    )
                    continue
                if (
                    place is not None
                    and token.color_identity
                    not in place.allowed_color_identities
                ):
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.COLOR_NOT_ALLOWED,
                            path + ("color",),
                            (place.identity.value, token.color_identity.value),
                            "token color is not admitted by the place",
                        )
                    )
                if token.value.kind not in color.allowed_value_kinds:
                    issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode.VALUE_KIND_NOT_ALLOWED,
                            path + ("value_kind",),
                            (
                                token.color_identity.value,
                                token.value.kind.value,
                            ),
                            "token value kind is not admitted by its color",
                        )
                    )
                if token.value.kind is CpnValueKind.CONTROL_RECORD:
                    assert type(token.value.value) is CpnControlRecord
                    record = token.value.value
                    if record.type_identity not in (
                        color.allowed_control_record_type_identities
                    ):
                        issues.append(
                            CpnValidationIssue(
                                CpnValidationIssueCode.CONTROL_RECORD_TYPE_NOT_ALLOWED,
                                path + ("value", "type"),
                                (
                                    token.color_identity.value,
                                    record.type_identity.value,
                                ),
                                "record type is not admitted by the token color",
                            )
                        )
                    record_result = CpnControlRecordSchemaValidator().execute(
                        CpnControlRecordSchemaValidationInput(
                            record, definition.control_record_types
                        )
                    )
                    for record_issue in record_result.issues:
                        issues.append(
                            CpnValidationIssue(
                                CpnValidationIssueCode.INVALID_CONTROL_RECORD_VALUE,
                                path + ("value",) + record_issue.path,
                                (
                                    record.type_identity.value,
                                    record_issue.code.value,
                                ),
                                record_issue.message,
                            )
                        )
        return CpnValidationResult(tuple(issues))
