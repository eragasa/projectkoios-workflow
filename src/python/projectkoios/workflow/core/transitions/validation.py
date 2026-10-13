"""Workflow transition validation."""

from __future__ import annotations

from ..records.kinds import (
    WorkflowAdapterDisposition,
    WorkflowValidationFindingCode,
)
from ..records.runs import WorkflowRun
from ..records.validation import (
    WorkflowValidationFinding,
    WorkflowValidationResult,
)
from .collections import _merge_artifacts, _merge_decisions
from .inputs import WorkflowTransitionInput, WorkflowTransitionPreflightInput


class WorkflowTransitionValidator:
    """Pure structural preflight before an external adapter may act."""

    def execute(
        self,
        preflight_input: WorkflowTransitionPreflightInput,
    ) -> WorkflowValidationResult:
        """Validate exact core records without adapter execution or I/O.

        Parameters
        ----------
        preflight_input
            Definition, run, prior state, and request to check before dispatch.

        Returns
        -------
        WorkflowValidationResult
            Bounded structural findings. An empty result means only that the
            records agree; owning policy must still verify authority evidence.

        Raises
        ------
        TypeError
            ``preflight_input`` is not the exact public preflight type.

        Notes
        -----
        This action is deterministic and performs no mutation, policy lookup,
        persistence, dispatch, or external I/O.
        """
        if type(preflight_input) is not WorkflowTransitionPreflightInput:
            raise TypeError(
                "preflight_input must be WorkflowTransitionPreflightInput"
            )
        findings = _bounded_findings(
            _validate_transition_preflight(preflight_input)
        )
        return WorkflowValidationResult.create(findings)


def _validate_transition_preflight(
    preflight_input: WorkflowTransitionPreflightInput,
) -> list[WorkflowValidationFinding]:
    definition = preflight_input.definition
    run = preflight_input.run
    prior = preflight_input.prior_state
    request = preflight_input.request
    findings: list[WorkflowValidationFinding] = []

    def add(
        code: WorkflowValidationFindingCode,
        path: tuple[str, ...],
        identities: tuple[str, ...],
        message: str,
    ) -> None:
        findings.append(
            WorkflowValidationFinding.create(
                code=code,
                path=path,
                related_identities=identities,
                message=message,
            )
        )

    if run.definition_identity != definition.identity:
        add(
            WorkflowValidationFindingCode.DEFINITION_MISMATCH,
            ("run", "definition_identity"),
            (run.definition_identity.value, definition.identity.value),
            "run and supplied definition do not match",
        )
    if prior.definition_identity != definition.identity:
        add(
            WorkflowValidationFindingCode.DEFINITION_MISMATCH,
            ("prior_state", "definition_identity"),
            (prior.definition_identity.value, definition.identity.value),
            "prior state and supplied definition do not match",
        )
    if prior.run_identity != run.identity:
        add(
            WorkflowValidationFindingCode.RUN_MISMATCH,
            ("prior_state", "run_identity"),
            (prior.run_identity.value, run.identity.value),
            "prior state and run identities do not match",
        )
    if (
        run.current_state_identity != prior.identity
        or run.revision != prior.revision
        or run.status != prior.run_status
    ):
        add(
            WorkflowValidationFindingCode.STATE_MISMATCH,
            ("run", "current_state"),
            (run.current_state_identity.value, prior.identity.value),
            "run does not identify the supplied prior state exactly",
        )
    if request.run_identity != run.identity:
        add(
            WorkflowValidationFindingCode.RUN_MISMATCH,
            ("request", "run_identity"),
            (request.run_identity.value, run.identity.value),
            "request and run identities do not match",
        )
    if request.expected_prior_state_identity != prior.identity:
        add(
            WorkflowValidationFindingCode.REVISION_CONFLICT,
            ("request", "expected_prior_state_identity"),
            (
                request.expected_prior_state_identity.value,
                prior.identity.value,
            ),
            "request expected a different prior state",
        )
    if request.expected_revision != run.revision:
        add(
            WorkflowValidationFindingCode.REVISION_CONFLICT,
            ("request", "expected_revision"),
            (str(request.expected_revision), str(run.revision)),
            "request expected a different run revision",
        )
    if run.status.is_terminal:
        add(
            WorkflowValidationFindingCode.TERMINAL_RUN,
            ("run", "status"),
            (run.status.value,),
            "terminal runs cannot apply later transitions",
        )
    if request.operation_identity not in definition.operation_identities:
        add(
            WorkflowValidationFindingCode.UNKNOWN_OPERATION,
            ("request", "operation_identity"),
            (request.operation_identity.value,),
            "requested operation is absent from the workflow definition",
        )
    authority = request.authority_reference
    if authority.subject_identity != run.subject_identity:
        add(
            WorkflowValidationFindingCode.AUTHORITY_SUBJECT_MISMATCH,
            ("request", "authority_reference", "subject_identity"),
            (
                authority.subject_identity.value,
                run.subject_identity.value,
            ),
            "authority evidence applies to a different workflow subject",
        )
    if request.operation_identity not in authority.operation_identities:
        add(
            WorkflowValidationFindingCode.AUTHORITY_SCOPE_MISMATCH,
            ("request", "authority_reference", "operation_identities"),
            (request.operation_identity.value,),
            "authority evidence does not cover the requested operation",
        )
    for decision in request.decision_references:
        if decision.subject_identity != run.subject_identity:
            add(
                WorkflowValidationFindingCode.STATE_MISMATCH,
                ("request", "decision_references"),
                (
                    decision.identity.value,
                    decision.subject_identity.value,
                    run.subject_identity.value,
                ),
                "request decision applies to a different workflow subject",
            )

    return findings


def _validate_transition_evidence(
    transition_input: WorkflowTransitionInput,
) -> list[WorkflowValidationFinding]:
    definition = transition_input.definition
    run = transition_input.run
    prior = transition_input.prior_state
    request = transition_input.request
    adapter = transition_input.adapter_evidence
    failure = transition_input.infrastructure_failure
    findings: list[WorkflowValidationFinding] = []

    def add(
        code: WorkflowValidationFindingCode,
        path: tuple[str, ...],
        identities: tuple[str, ...],
        message: str,
    ) -> None:
        findings.append(
            WorkflowValidationFinding.create(
                code=code,
                path=path,
                related_identities=identities,
                message=message,
            )
        )

    if adapter is not None:
        mismatches = (
            adapter.definition_identity != definition.identity,
            adapter.request_identity != request.identity,
            adapter.prior_state_identity != prior.identity,
        )
        if any(mismatches):
            add(
                WorkflowValidationFindingCode.ADAPTER_EVIDENCE_MISMATCH,
                ("adapter_evidence",),
                (adapter.identity.value, request.identity.value),
                "adapter evidence does not bind the exact transition input",
            )
        if (
            adapter.disposition is WorkflowAdapterDisposition.ENABLED
            and len(adapter.successor_state_references)
            > request.bounds.max_successor_state_references
        ):
            add(
                WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                ("adapter_evidence", "successor_state_references"),
                (adapter.identity.value,),
                "adapter successor state exceeds request bounds",
            )
        if len(adapter.produced_artifact_references) > (
            request.bounds.max_artifact_references
        ):
            add(
                WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                ("adapter_evidence", "produced_artifact_references"),
                (adapter.identity.value,),
                "adapter artifact output exceeds request bounds",
            )
        if len(adapter.recorded_decision_references) > (
            request.bounds.max_decision_references
        ):
            add(
                WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                ("adapter_evidence", "recorded_decision_references"),
                (adapter.identity.value,),
                "adapter decision output exceeds request bounds",
            )
        for decision in adapter.recorded_decision_references:
            if decision.subject_identity != run.subject_identity:
                add(
                    WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                    ("adapter_evidence", "recorded_decision_references"),
                    (decision.identity.value,),
                    "adapter decision applies to a different workflow subject",
                )
        if adapter.disposition is WorkflowAdapterDisposition.ENABLED:
            aggregate_artifacts = _merge_artifacts(
                run.artifact_references,
                request.artifact_references,
                adapter.produced_artifact_references,
            )
            if len(aggregate_artifacts) > WorkflowRun.MAX_ARTIFACT_REFERENCES:
                add(
                    WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                    ("successor_run", "artifact_references"),
                    (adapter.identity.value,),
                    "successor artifact references exceed run bounds",
                )
            aggregate_decisions = _merge_decisions(
                run.decision_references,
                request.decision_references,
                adapter.recorded_decision_references,
            )
            if len(aggregate_decisions) > WorkflowRun.MAX_DECISION_REFERENCES:
                add(
                    WorkflowValidationFindingCode.ADAPTER_OUTPUT_INVALID,
                    ("successor_run", "decision_references"),
                    (adapter.identity.value,),
                    "successor decision references exceed run bounds",
                )
    if failure is not None and failure.request_identity != request.identity:
        add(
            WorkflowValidationFindingCode.INFRASTRUCTURE_EVIDENCE_MISMATCH,
            ("infrastructure_failure", "request_identity"),
            (failure.request_identity.value, request.identity.value),
            "infrastructure failure does not bind the exact request",
        )
    return findings


def _validate_transition_input(
    transition_input: WorkflowTransitionInput,
) -> list[WorkflowValidationFinding]:
    preflight_input = WorkflowTransitionPreflightInput(
        transition_input.definition,
        transition_input.run,
        transition_input.prior_state,
        transition_input.request,
    )
    return _validate_transition_preflight(
        preflight_input
    ) + _validate_transition_evidence(transition_input)


def _bounded_findings(
    findings: list[WorkflowValidationFinding],
) -> tuple[WorkflowValidationFinding, ...]:
    maximum = WorkflowValidationResult.MAX_FINDINGS
    if len(findings) <= maximum:
        return tuple(findings)
    retained = findings[: maximum - 1]
    retained_count = len(retained)
    omitted = len(findings) - retained_count
    retained.append(
        WorkflowValidationFinding.create(
            code=WorkflowValidationFindingCode.FINDINGS_TRUNCATED,
            path=("validation", "findings"),
            related_identities=(str(len(findings)), str(omitted)),
            message=(
                f"validation retained {retained_count} findings and omitted "
                f"{omitted} additional findings"
            ),
        )
    )
    return tuple(retained)
