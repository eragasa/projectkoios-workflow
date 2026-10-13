"""Workflow transition inputs."""

from __future__ import annotations

from dataclasses import dataclass

from ..records.evidence import (
    WorkflowAdapterEvidence,
    WorkflowInfrastructureFailureEvidence,
)
from ..records.references import (
    WorkflowDefinitionReference,
)
from ..records.requests import WorkflowTransitionRequest
from ..records.runs import WorkflowRun
from ..records.states import WorkflowStateSnapshot


@dataclass(frozen=True, slots=True)
class WorkflowTransitionPreflightInput:
    """Immutable core records needed before any external adapter action."""

    definition: WorkflowDefinitionReference
    run: WorkflowRun
    prior_state: WorkflowStateSnapshot
    request: WorkflowTransitionRequest

    def __post_init__(self) -> None:
        _validate_preflight_record_types(
            self.definition,
            self.run,
            self.prior_state,
            self.request,
        )


@dataclass(frozen=True, slots=True)
class WorkflowTransitionInput:
    """Complete immutable input for one pure transition-processing attempt."""

    definition: WorkflowDefinitionReference
    run: WorkflowRun
    prior_state: WorkflowStateSnapshot
    request: WorkflowTransitionRequest
    adapter_evidence: WorkflowAdapterEvidence | None = None
    infrastructure_failure: WorkflowInfrastructureFailureEvidence | None = None

    def __post_init__(self) -> None:
        _validate_preflight_record_types(
            self.definition,
            self.run,
            self.prior_state,
            self.request,
        )
        if self.adapter_evidence is not None and (
            type(self.adapter_evidence) is not WorkflowAdapterEvidence
        ):
            raise TypeError(
                "adapter_evidence must be WorkflowAdapterEvidence or None"
            )
        if self.infrastructure_failure is not None and (
            type(self.infrastructure_failure)
            is not WorkflowInfrastructureFailureEvidence
        ):
            raise TypeError(
                "infrastructure_failure must be "
                "WorkflowInfrastructureFailureEvidence or None"
            )
        if (self.adapter_evidence is None) == (
            self.infrastructure_failure is None
        ):
            raise ValueError(
                "exactly one adapter result or infrastructure failure "
                "is required"
            )


def _validate_preflight_record_types(
    definition: object,
    run: object,
    prior_state: object,
    request: object,
) -> None:
    expected = (
        ("definition", definition, WorkflowDefinitionReference),
        ("run", run, WorkflowRun),
        ("prior_state", prior_state, WorkflowStateSnapshot),
        ("request", request, WorkflowTransitionRequest),
    )
    for name, value, value_type in expected:
        if type(value) is not value_type:
            raise TypeError(f"{name} must be {value_type.__name__}")
