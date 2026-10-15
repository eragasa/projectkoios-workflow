"""Repository-authorized input construction for experimental pure actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from string import hexdigits
from typing import final

from projectkoios.workflow.actions import (
    ExperimentalWorkflowFiringRequestCoordinates,
    ExperimentalWorkflowSelectedBindingEvidence,
)
from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionExecutionBindings,
    ExperimentalWorkflowPureActionInputBindings,
    ExperimentalWorkflowPureActionInputPlan,
)
from projectkoios.workflow.core.identities import stable_identity

from .pure_action_inputs import (
    ExperimentalWorkflowPureActionAdmittedInputs,
    ExperimentalWorkflowPureActionInputAdmissionFactory,
    ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
)
from .pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceLoadResult,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
    ExperimentalWorkflowPureActionInputSourceRepository,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
)

_AUTHORITY_RECORD_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-source-authority:0"
)
_AUTHORIZED_INPUTS_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-authorized-inputs:0"
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceAuthorityIdentity:
    """Content identity of one repository-proven source observation."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "input source authority identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionAuthorizedInputsIdentity:
    """Content identity of one repository-authorized input aggregate."""

    value: str

    def __post_init__(self) -> None:
        _validate_sha256(self.value, "authorized inputs identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputSourceAuthority:
    """Bind one source reference to its exact retained immutable revision."""

    identity: ExperimentalWorkflowPureActionInputSourceAuthorityIdentity = (
        field(init=False)
    )
    reference_identity: (
        ExperimentalWorkflowPureActionInputSourceReferenceIdentity
    )
    revision_identity: ExperimentalWorkflowPureActionInputSourceRevisionIdentity
    evidence_identity: ExperimentalWorkflowPureActionInputSourceEvidenceIdentity

    def __post_init__(self) -> None:
        for name, expected in (
            (
                "reference_identity",
                ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
            ),
            (
                "revision_identity",
                ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
            ),
            (
                "evidence_identity",
                ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
            ),
        ):
            if type(getattr(self, name)) is not expected:
                raise TypeError(f"{name} must be {expected.__name__}")
        if self.revision_identity.value != self.evidence_identity.value:
            raise ValueError("source revision differs from evidence identity")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionInputSourceAuthorityIdentity(
                stable_identity(
                    _AUTHORITY_RECORD_DOMAIN,
                    self.reference_identity.value,
                    self.revision_identity.value,
                    self.evidence_identity.value,
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionAuthorizedInputs:
    """Bind structural input admission to repository-proven sources."""

    identity: ExperimentalWorkflowPureActionAuthorizedInputsIdentity = field(
        init=False
    )
    admitted_inputs: ExperimentalWorkflowPureActionAdmittedInputs
    source_authorities: tuple[
        ExperimentalWorkflowPureActionInputSourceAuthority, ...
    ]

    def __post_init__(self) -> None:
        admitted = _reconstruct_admitted_inputs(self.admitted_inputs)
        if type(self.source_authorities) is not tuple:
            raise TypeError("source_authorities must be a tuple")
        authorities = tuple(
            _reconstruct_authority(value) for value in self.source_authorities
        )
        if authorities != self.source_authorities:
            raise ValueError("source authorities differ after validation")
        sources = admitted.source_evidence
        if len(authorities) != len(sources):
            raise ValueError(
                "source authorities must exactly cover admitted sources"
            )
        for index, (authority, source) in enumerate(
            zip(authorities, sources, strict=True)
        ):
            reference = ExperimentalWorkflowPureActionInputSourceReference(
                source_kind=source.source_kind,
                source_profile_identity=source.source_profile_identity,
                source_identity=source.source_identity,
            )
            if (
                authority.reference_identity != reference.identity
                or authority.evidence_identity != source.identity
            ):
                raise ValueError(
                    f"source_authorities[{index}] differs from admitted source"
                )
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                stable_identity(
                    _AUTHORIZED_INPUTS_DOMAIN,
                    admitted.identity.value,
                    tuple(value.identity.value for value in authorities),
                )
            ),
        )


class ExperimentalWorkflowPureActionInputAuthorizationStatus(StrEnum):
    """Closed result of constructing repository-authorized inputs."""

    AUTHORIZED = "authorized"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionInputAuthorizationResult:
    """Expose authorized inputs only after every source loads exactly."""

    status: ExperimentalWorkflowPureActionInputAuthorizationStatus
    authorized_inputs: ExperimentalWorkflowPureActionAuthorizedInputs | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.status) is not (
            ExperimentalWorkflowPureActionInputAuthorizationStatus
        ):
            raise TypeError(
                "status must be "
                "ExperimentalWorkflowPureActionInputAuthorizationStatus"
            )
        _validate_diagnostics(self.diagnostics)
        if self.status is (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.AUTHORIZED
        ):
            if type(self.authorized_inputs) is not (
                ExperimentalWorkflowPureActionAuthorizedInputs
            ):
                raise TypeError("authorized status requires authorized inputs")
            _reconstruct_authorized_inputs(self.authorized_inputs)
        elif self.authorized_inputs is not None:
            raise ValueError("failed authorization prohibits authorized inputs")


@final
class ExperimentalWorkflowPureActionInputAuthorizationService:
    """Resolve exact source references before constructing SDK inputs."""

    __slots__ = ("_repository",)

    def __init__(
        self,
        repository: ExperimentalWorkflowPureActionInputSourceRepository,
    ) -> None:
        if not isinstance(
            repository,
            ExperimentalWorkflowPureActionInputSourceRepository,
        ):
            raise TypeError(
                "repository must implement "
                "ExperimentalWorkflowPureActionInputSourceRepository"
            )
        self._repository = repository

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionInputAuthorizationService "
            "is not subclassable"
        )

    def execute(
        self,
        *,
        input_bindings: ExperimentalWorkflowPureActionInputBindings,
        selected_binding_evidence: ExperimentalWorkflowSelectedBindingEvidence,
        coordinates: ExperimentalWorkflowFiringRequestCoordinates,
        source_references: tuple[
            ExperimentalWorkflowPureActionInputSourceReference, ...
        ],
    ) -> ExperimentalWorkflowPureActionInputAuthorizationResult:
        """Load every exact source and construct authorized SDK inputs."""
        bindings = _reconstruct_input_bindings(input_bindings)
        evidence = _reconstruct_selected_binding_evidence(
            selected_binding_evidence
        )
        invocation_coordinates = _reconstruct_coordinates(coordinates)
        selected_profile = (
            bindings.input_plan.execution_plan.selected_binding_profile_identity
        )
        if evidence.profile_identity != selected_profile:
            raise ValueError("selected-binding profile differs from input plan")
        if type(source_references) is not tuple:
            raise TypeError("source_references must be a tuple")
        references = tuple(
            _reconstruct_reference(value) for value in source_references
        )
        mappings = bindings.input_plan.input_mappings
        if len(references) != len(mappings):
            raise ValueError(
                "source references must exactly satisfy input mappings"
            )
        for index, (reference, mapping) in enumerate(
            zip(references, mappings, strict=True)
        ):
            if reference.source_kind != mapping.source_kind:
                raise ValueError(
                    f"source_references[{index}] kind differs from mapping"
                )
            if (
                reference.source_profile_identity
                != mapping.source_profile_identity
            ):
                raise ValueError(
                    f"source_references[{index}] profile differs from mapping"
                )
        sources = []
        authorities = []
        for reference in references:
            try:
                loaded = self._repository.load(reference)
            except Exception:
                return ExperimentalWorkflowPureActionInputAuthorizationResult(
                    status=(
                        ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR
                    ),
                    authorized_inputs=None,
                    diagnostics=("source_repository_error",),
                )
            if type(loaded) is not (
                ExperimentalWorkflowPureActionInputSourceLoadResult
            ):
                return ExperimentalWorkflowPureActionInputAuthorizationResult(
                    status=(
                        ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR
                    ),
                    authorized_inputs=None,
                    diagnostics=("source_repository_invalid_result",),
                )
            if loaded.status is not (
                ExperimentalWorkflowPureActionInputSourceLoadStatus.LOADED
            ):
                return ExperimentalWorkflowPureActionInputAuthorizationResult(
                    status=_authorization_failure(loaded.status),
                    authorized_inputs=None,
                    diagnostics=loaded.diagnostics,
                )
            assert loaded.evidence is not None
            assert loaded.revision_identity is not None
            sources.append(loaded.evidence)
            authorities.append(
                ExperimentalWorkflowPureActionInputSourceAuthority(
                    reference_identity=reference.identity,
                    revision_identity=loaded.revision_identity,
                    evidence_identity=loaded.evidence.identity,
                )
            )
        admitted = (
            ExperimentalWorkflowPureActionInputAdmissionFactory().execute(
                input_bindings=bindings,
                selected_binding_evidence=evidence,
                coordinates=invocation_coordinates,
                source_evidence=tuple(sources),
            )
        )
        authorized = ExperimentalWorkflowPureActionAuthorizedInputs(
            admitted_inputs=admitted,
            source_authorities=tuple(authorities),
        )
        return ExperimentalWorkflowPureActionInputAuthorizationResult(
            status=(
                ExperimentalWorkflowPureActionInputAuthorizationStatus.AUTHORIZED
            ),
            authorized_inputs=authorized,
            diagnostics=(),
        )


def _authorization_failure(
    status: ExperimentalWorkflowPureActionInputSourceLoadStatus,
) -> ExperimentalWorkflowPureActionInputAuthorizationStatus:
    return {
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ABSENT: (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.ABSENT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INCOMPATIBLE: (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INCOMPATIBLE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.CORRUPT: (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.CORRUPT
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.INDETERMINATE: (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INDETERMINATE
        ),
        ExperimentalWorkflowPureActionInputSourceLoadStatus.ERROR: (
            ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR
        ),
    }[status]


def _reconstruct_input_bindings(
    value: ExperimentalWorkflowPureActionInputBindings,
) -> ExperimentalWorkflowPureActionInputBindings:
    if type(value) is not ExperimentalWorkflowPureActionInputBindings:
        raise TypeError(
            "input_bindings must be ExperimentalWorkflowPureActionInputBindings"
        )
    reconstructed = ExperimentalWorkflowPureActionInputBindings(
        input_plan=ExperimentalWorkflowPureActionInputPlan(
            execution_plan=value.input_plan.execution_plan,
            input_mappings=value.input_plan.input_mappings,
        ),
        execution_bindings=ExperimentalWorkflowPureActionExecutionBindings(
            execution_plan=value.execution_bindings.execution_plan,
            integration_manifest=value.execution_bindings.integration_manifest,
        ),
    )
    if reconstructed != value:
        raise ValueError("input bindings differ after validation")
    return reconstructed


def _reconstruct_selected_binding_evidence(
    value: ExperimentalWorkflowSelectedBindingEvidence,
) -> ExperimentalWorkflowSelectedBindingEvidence:
    if type(value) is not ExperimentalWorkflowSelectedBindingEvidence:
        raise TypeError(
            "selected_binding_evidence must be "
            "ExperimentalWorkflowSelectedBindingEvidence"
        )
    reconstructed = ExperimentalWorkflowSelectedBindingEvidence(
        enablement_result=value.enablement_result,
        selection_result=value.selection_result,
    )
    if reconstructed != value:
        raise ValueError("selected binding evidence differs after validation")
    return reconstructed


def _reconstruct_coordinates(
    value: ExperimentalWorkflowFiringRequestCoordinates,
) -> ExperimentalWorkflowFiringRequestCoordinates:
    if type(value) is not ExperimentalWorkflowFiringRequestCoordinates:
        raise TypeError(
            "coordinates must be ExperimentalWorkflowFiringRequestCoordinates"
        )
    reconstructed = ExperimentalWorkflowFiringRequestCoordinates(
        net_instance_identity=value.net_instance_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        occurrence_identity=value.occurrence_identity,
        attempt_identity=value.attempt_identity,
        attempt_ordinal=value.attempt_ordinal,
    )
    if reconstructed != value:
        raise ValueError("coordinates differ after validation")
    return reconstructed


def _reconstruct_authority(
    value: ExperimentalWorkflowPureActionInputSourceAuthority,
) -> ExperimentalWorkflowPureActionInputSourceAuthority:
    if type(value) is not ExperimentalWorkflowPureActionInputSourceAuthority:
        raise TypeError(
            "source_authorities must contain "
            "ExperimentalWorkflowPureActionInputSourceAuthority"
        )
    reconstructed = ExperimentalWorkflowPureActionInputSourceAuthority(
        reference_identity=value.reference_identity,
        revision_identity=value.revision_identity,
        evidence_identity=value.evidence_identity,
    )
    if reconstructed != value:
        raise ValueError("source authority differs after validation")
    return reconstructed


def _reconstruct_admitted_inputs(
    value: ExperimentalWorkflowPureActionAdmittedInputs,
) -> ExperimentalWorkflowPureActionAdmittedInputs:
    if type(value) is not ExperimentalWorkflowPureActionAdmittedInputs:
        raise TypeError(
            "admitted_inputs must be "
            "ExperimentalWorkflowPureActionAdmittedInputs"
        )
    reconstructed = ExperimentalWorkflowPureActionAdmittedInputs(
        input_bindings=value.input_bindings,
        selected_binding_evidence=value.selected_binding_evidence,
        coordinates=value.coordinates,
        source_evidence=value.source_evidence,
        request=value.request,
    )
    if reconstructed != value:
        raise ValueError("admitted inputs differ after validation")
    return reconstructed


def _reconstruct_authorized_inputs(
    value: ExperimentalWorkflowPureActionAuthorizedInputs,
) -> ExperimentalWorkflowPureActionAuthorizedInputs:
    if type(value) is not ExperimentalWorkflowPureActionAuthorizedInputs:
        raise TypeError(
            "authorized_inputs must be "
            "ExperimentalWorkflowPureActionAuthorizedInputs"
        )
    reconstructed = ExperimentalWorkflowPureActionAuthorizedInputs(
        admitted_inputs=value.admitted_inputs,
        source_authorities=value.source_authorities,
    )
    if reconstructed != value:
        raise ValueError("authorized inputs differ after validation")
    return reconstructed


def _reconstruct_reference(
    value: ExperimentalWorkflowPureActionInputSourceReference,
) -> ExperimentalWorkflowPureActionInputSourceReference:
    if type(value) is not ExperimentalWorkflowPureActionInputSourceReference:
        raise TypeError(
            "source_references must contain "
            "ExperimentalWorkflowPureActionInputSourceReference"
        )
    reconstructed = ExperimentalWorkflowPureActionInputSourceReference(
        source_kind=value.source_kind,
        source_profile_identity=value.source_profile_identity,
        source_identity=value.source_identity,
    )
    if reconstructed != value:
        raise ValueError("source reference differs after validation")
    return reconstructed


def _validate_sha256(value: str, label: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if (
        len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _validate_diagnostics(values: tuple[str, ...]) -> None:
    if type(values) is not tuple or len(values) > 32:
        raise TypeError("diagnostics must be a bounded tuple")
    if any(type(value) is not str or not value for value in values):
        raise TypeError("diagnostics must contain nonempty strings")


__all__ = [
    "ExperimentalWorkflowPureActionAuthorizedInputs",
    "ExperimentalWorkflowPureActionAuthorizedInputsIdentity",
    "ExperimentalWorkflowPureActionInputAuthorizationResult",
    "ExperimentalWorkflowPureActionInputAuthorizationService",
    "ExperimentalWorkflowPureActionInputAuthorizationStatus",
    "ExperimentalWorkflowPureActionInputSourceAuthority",
    "ExperimentalWorkflowPureActionInputSourceAuthorityIdentity",
]
