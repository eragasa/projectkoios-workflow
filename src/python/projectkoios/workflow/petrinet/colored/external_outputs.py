"""Public validation of already-admitted external CPN output bindings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import final

from .control.records.schema import (
    CpnControlRecordSchemaValidationInput,
    CpnControlRecordSchemaValidator,
)
from .definitions import CpnDefinition
from .bindings import CpnBinding
from .definitions import CpnTransitionIdentity
from .values import CpnControlRecord, CpnValueKind


class CpnExternalOutputValidationIssueCode(StrEnum):
    """Closed external-output binding findings."""

    UNKNOWN_TRANSITION = "unknown_transition"
    TRANSITION_MISMATCH = "transition_mismatch"
    VARIABLE_SET_MISMATCH = "variable_set_mismatch"
    DUPLICATE_VARIABLE = "duplicate_variable"
    INVALID_CONTROL_RECORD = "invalid_control_record"


@dataclass(frozen=True, slots=True)
class CpnExternalOutputValidationIssue:
    """One deterministic external-output finding."""

    code: CpnExternalOutputValidationIssueCode
    path: tuple[str, ...]
    message: str


@dataclass(frozen=True, slots=True)
class CpnExternalOutputValidationResult:
    """Complete ordered findings for one external-output binding."""

    issues: tuple[CpnExternalOutputValidationIssue, ...]

    def __post_init__(self) -> None:
        if type(self.issues) is not tuple or any(
            type(item) is not CpnExternalOutputValidationIssue
            for item in self.issues
        ):
            raise TypeError(
                "issues must be a tuple of CpnExternalOutputValidationIssue"
            )
        ordered = [
            ((item.path, item.code.value), ordinal, item)
            for ordinal, item in enumerate(self.issues)
        ]
        ordered.sort()
        object.__setattr__(self, "issues", tuple(item[2] for item in ordered))

    @property
    def is_valid(self) -> bool:
        """Return whether the external binding exactly matches its transition."""
        return not self.issues


@dataclass(frozen=True, slots=True)
class CpnExternalOutputValidationInput:
    """Definition, transition, and already-admitted external binding."""

    definition: CpnDefinition
    transition_identity: CpnTransitionIdentity
    binding: CpnBinding

    def __post_init__(self) -> None:
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.transition_identity) is not CpnTransitionIdentity:
            raise TypeError("transition_identity must be CpnTransitionIdentity")
        if type(self.binding) is not CpnBinding:
            raise TypeError("binding must be CpnBinding")


@dataclass(frozen=True, slots=True)
class CpnExternalOutputValidatorIdentity:
    """Identity of exact external-output validation semantics."""

    value: str = "projectkoios.workflow.cpn.external-output-validator:0.1"


@final
class CpnExternalOutputValidator:
    """Directly validate external values without resolving payloads or effects."""

    __slots__ = ()

    @property
    def identity(self) -> CpnExternalOutputValidatorIdentity:
        """Return exact validation semantics identity."""
        return CpnExternalOutputValidatorIdentity()

    def execute(
        self, validation_input: CpnExternalOutputValidationInput
    ) -> CpnExternalOutputValidationResult:
        """Validate correlation, variable closure, and bounded record values."""
        if type(validation_input) is not CpnExternalOutputValidationInput:
            raise TypeError(
                "validation_input must be CpnExternalOutputValidationInput"
            )
        issues: list[CpnExternalOutputValidationIssue] = []
        transitions = {
            item.identity: item
            for item in validation_input.definition.transitions
        }
        transition = transitions.get(validation_input.transition_identity)
        if transition is None:
            return CpnExternalOutputValidationResult(
                (
                    CpnExternalOutputValidationIssue(
                        CpnExternalOutputValidationIssueCode.UNKNOWN_TRANSITION,
                        ("transition",),
                        "external output references an unknown transition",
                    ),
                )
            )
        if validation_input.binding.transition_identity != transition.identity:
            issues.append(
                CpnExternalOutputValidationIssue(
                    CpnExternalOutputValidationIssueCode.TRANSITION_MISMATCH,
                    ("binding", "transition"),
                    "external binding identifies a different transition",
                )
            )
        variables = tuple(
            item.variable_identity
            for item in validation_input.binding.assignments
        )
        if len(set(variables)) != len(variables):
            issues.append(
                CpnExternalOutputValidationIssue(
                    CpnExternalOutputValidationIssueCode.DUPLICATE_VARIABLE,
                    ("binding", "assignments"),
                    "external binding variables must be unique",
                )
            )
        if variables != transition.external_output_variable_identities:
            issues.append(
                CpnExternalOutputValidationIssue(
                    CpnExternalOutputValidationIssueCode.VARIABLE_SET_MISMATCH,
                    ("binding", "assignments"),
                    "external binding must use exact declared variable order",
                )
            )
        for assignment in validation_input.binding.assignments:
            if assignment.value.kind is CpnValueKind.CONTROL_RECORD:
                assert type(assignment.value.value) is CpnControlRecord
                result = CpnControlRecordSchemaValidator().execute(
                    CpnControlRecordSchemaValidationInput(
                        assignment.value.value,
                        validation_input.definition.control_record_types,
                    )
                )
                for finding in result.issues:
                    issues.append(
                        CpnExternalOutputValidationIssue(
                            CpnExternalOutputValidationIssueCode.INVALID_CONTROL_RECORD,
                            ("binding", assignment.variable_identity.value)
                            + finding.path,
                            finding.code.value,
                        )
                    )
        return CpnExternalOutputValidationResult(tuple(issues))
