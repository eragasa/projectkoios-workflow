"""Identity-bound evidence for one selected shadow CPN binding."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from projectkoios.workflow.petrinet.colored import (
    ColoredPetriNetBinding,
    ColoredPetriNetEnablementResult,
    ColoredPetriNetSelectionOutcomeKind,
    ColoredPetriNetSelectionResult,
)

from ._binding import ExperimentalWorkflowSelectedBindingEncoder
from ._validation import (
    _semantic_sha256,
    _validate_ascii_token,
    _validate_sha256,
)

_SELECTED_BINDING_EVIDENCE_CONTRACT = (
    "projectkoios.workflow.experimental-selected-binding-evidence:1"
)
_MAX_PROFILE_IDENTITY_BYTES = 512


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity:
    """Nominal identity of exact selected-binding byte semantics."""

    value: str

    def __post_init__(self) -> None:
        _validate_ascii_token(self.value, "selected binding profile identity")
        if len(self.value.encode("ascii")) > _MAX_PROFILE_IDENTITY_BYTES:
            raise ValueError(
                "selected binding profile identity exceeds 512 ASCII bytes"
            )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowSelectedBindingEvidenceIdentity:
    """Content identity of one exact selected-binding evidence record."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "selected binding evidence identity")


_ProfileIdentity = (
    ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowSelectedBindingEvidence:
    """Bind a successful selection result to exact canonical binding bytes."""

    identity: ExperimentalWorkflowSelectedBindingEvidenceIdentity = field(
        init=False
    )
    profile_identity: _ProfileIdentity = field(init=False)
    selected_binding_sha256: str = field(init=False)
    selected_binding_bytes: bytes = field(init=False, repr=False)
    enablement_result: ColoredPetriNetEnablementResult
    selection_result: ColoredPetriNetSelectionResult

    def __post_init__(self) -> None:
        if type(self.enablement_result) is not ColoredPetriNetEnablementResult:
            raise TypeError(
                "enablement_result must be ColoredPetriNetEnablementResult"
            )
        if type(self.selection_result) is not ColoredPetriNetSelectionResult:
            raise TypeError(
                "selection_result must be ColoredPetriNetSelectionResult"
            )
        enablement = ColoredPetriNetEnablementResult(
            identity=self.enablement_result.identity,
            definition_identity=self.enablement_result.definition_identity,
            selection_policy=self.enablement_result.selection_policy,
            marking_identity=self.enablement_result.marking_identity,
            expression_evaluator_identity=(
                self.enablement_result.expression_evaluator_identity
            ),
            ordering_policy_identity=(
                self.enablement_result.ordering_policy_identity
            ),
            transition_enabler_identity=(
                self.enablement_result.transition_enabler_identity
            ),
            enabled_bindings=self.enablement_result.enabled_bindings,
            failure=self.enablement_result.failure,
        )
        if enablement != self.enablement_result:
            raise ValueError("enablement result differs after validation")
        selection = ColoredPetriNetSelectionResult(
            enablement_result_identity=(
                self.selection_result.enablement_result_identity
            ),
            selector_identity=self.selection_result.selector_identity,
            ordering_policy_identity=(
                self.selection_result.ordering_policy_identity
            ),
            outcome=self.selection_result.outcome,
            selected_binding=self.selection_result.selected_binding,
            directive=self.selection_result.directive,
            failure_code=self.selection_result.failure_code,
        )
        if selection != self.selection_result:
            raise ValueError("selection result differs after validation")
        if not enablement.is_success or enablement.enabled_bindings is None:
            raise ValueError(
                "selected binding evidence requires successful enablement"
            )
        if (
            selection.outcome
            is not ColoredPetriNetSelectionOutcomeKind.SELECTED
        ):
            raise ValueError(
                "selected binding evidence requires a selected result"
            )
        selected_binding = selection.selected_binding
        if selected_binding is None:
            raise ValueError(
                "selected result must contain one selected binding"
            )
        if selection.enablement_result_identity != enablement.identity:
            raise ValueError("selection result differs from enablement result")
        if (
            selection.ordering_policy_identity
            != enablement.ordering_policy_identity
        ):
            raise ValueError(
                "selection ordering differs from enablement ordering"
            )
        if selected_binding not in enablement.enabled_bindings:
            raise ValueError(
                "selected binding is absent from enablement result"
            )

        encoder = ExperimentalWorkflowSelectedBindingEncoder()
        selected_binding_bytes = encoder.encode(selected_binding)
        selected_binding_sha256 = hashlib.sha256(
            selected_binding_bytes
        ).hexdigest()
        profile_identity = (
            ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity(
                encoder.profile_identity
            )
        )
        predecessor_identity = enablement.marking_identity.value
        transition_identity = selected_binding.transition_identity.value
        identity = ExperimentalWorkflowSelectedBindingEvidenceIdentity(
            _semantic_sha256(
                {
                    "binding_byte_length": len(selected_binding_bytes),
                    "contract": _SELECTED_BINDING_EVIDENCE_CONTRACT,
                    "definition_identity": enablement.definition_identity.value,
                    "enablement_result_identity": enablement.identity.value,
                    "predecessor_marking_identity": predecessor_identity,
                    "profile_identity": profile_identity.value,
                    "selected_binding_sha256": selected_binding_sha256,
                    "selection_result_identity": selection.identity.value,
                    "transition_identity": transition_identity,
                }
            )
        )
        object.__setattr__(self, "profile_identity", profile_identity)
        object.__setattr__(
            self,
            "selected_binding_sha256",
            selected_binding_sha256,
        )
        object.__setattr__(
            self,
            "selected_binding_bytes",
            selected_binding_bytes,
        )
        object.__setattr__(self, "identity", identity)

    @property
    def selected_binding(self) -> ColoredPetriNetBinding:
        """Return the exact binding carried by the selected result."""
        selected_binding = self.selection_result.selected_binding
        assert selected_binding is not None
        return selected_binding


__all__ = [
    "ExperimentalWorkflowSelectedBindingEvidence",
    "ExperimentalWorkflowSelectedBindingEvidenceIdentity",
    "ExperimentalWorkflowSelectedBindingRepresentationProfileIdentity",
]
