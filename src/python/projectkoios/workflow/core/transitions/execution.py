"""Workflow transition execution."""

from __future__ import annotations

from ..records.audits import WorkflowAuditEvent, WorkflowAuditReference
from ..records.evidence import (
    WorkflowAdapterEvidence,
)
from ..records.kinds import (
    WorkflowAdapterDisposition,
    WorkflowRunStatus,
    WorkflowTransitionOutcomeKind,
    WorkflowValidationFindingCode,
)
from ..records.outcomes import WorkflowTransitionOutcome
from ..records.runs import WorkflowRun
from ..records.states import WorkflowStateSnapshot
from ..records.validation import (
    WorkflowValidationResult,
)
from .collections import _merge_artifacts, _merge_decisions
from .inputs import WorkflowTransitionInput
from .results import WorkflowTransitionExecution
from .validation import _bounded_findings, _validate_transition_input


class WorkflowTransitionProcessor:
    """Pure action validating and applying one workflow transition request."""

    def execute(
        self, transition_input: WorkflowTransitionInput
    ) -> WorkflowTransitionExecution:
        """Process one transition without mutating state or performing I/O.

        Parameters
        ----------
        transition_input
            Exact definition, run, prior state, request, and supplied adapter or
            infrastructure evidence.

        Returns
        -------
        WorkflowTransitionExecution
            Applied or non-applied outcome plus deterministic audit evidence.
        """
        if type(transition_input) is not WorkflowTransitionInput:
            raise TypeError("transition_input must be WorkflowTransitionInput")

        findings = _bounded_findings(
            _validate_transition_input(transition_input)
        )
        validation = WorkflowValidationResult.create(findings)
        outcome = self._outcome(transition_input, validation)
        evidence = _evidence_identities(transition_input, validation)
        event_revision = (
            outcome.successor_run.revision
            if outcome.successor_run is not None
            else transition_input.run.revision
        )
        audit = WorkflowAuditEvent.create(
            run_identity=transition_input.run.identity,
            sequence_revision=event_revision,
            attempt_identity=transition_input.request.identity,
            event_kind=f"transition.{outcome.kind.value}",
            subject_references=(
                WorkflowAuditReference(transition_input.request.identity),
                WorkflowAuditReference(outcome.identity),
            ),
            evidence_references=evidence,
        )
        return WorkflowTransitionExecution(outcome, audit)

    def _outcome(
        self,
        transition_input: WorkflowTransitionInput,
        validation: WorkflowValidationResult,
    ) -> WorkflowTransitionOutcome:
        conflict_codes = {WorkflowValidationFindingCode.REVISION_CONFLICT}
        finding_codes = {finding.code for finding in validation.findings}
        nonconflict_codes = finding_codes - conflict_codes
        adapter = transition_input.adapter_evidence
        failure = transition_input.infrastructure_failure
        request = transition_input.request
        prior = transition_input.prior_state

        if nonconflict_codes:
            return WorkflowTransitionOutcome.create(
                kind=WorkflowTransitionOutcomeKind.REJECTED_INVALID,
                run_identity=transition_input.run.identity,
                request_identity=request.identity,
                prior_state_identity=prior.identity,
                prior_revision=transition_input.run.revision,
                validation=validation,
                adapter_evidence_identity=(
                    None if adapter is None else adapter.identity
                ),
                infrastructure_failure_identity=(
                    None if failure is None else failure.identity
                ),
                reasons=_validation_reasons(validation),
            )
        if finding_codes:
            return WorkflowTransitionOutcome.create(
                kind=WorkflowTransitionOutcomeKind.CONFLICT,
                run_identity=transition_input.run.identity,
                request_identity=request.identity,
                prior_state_identity=prior.identity,
                prior_revision=transition_input.run.revision,
                validation=validation,
                adapter_evidence_identity=(
                    None if adapter is None else adapter.identity
                ),
                infrastructure_failure_identity=(
                    None if failure is None else failure.identity
                ),
                reasons=_validation_reasons(validation),
            )
        if failure is not None:
            return WorkflowTransitionOutcome.create(
                kind=WorkflowTransitionOutcomeKind.INFRASTRUCTURE_FAILURE,
                run_identity=transition_input.run.identity,
                request_identity=request.identity,
                prior_state_identity=prior.identity,
                prior_revision=transition_input.run.revision,
                validation=validation,
                infrastructure_failure_identity=failure.identity,
                reasons=(failure.message,),
            )
        assert adapter is not None
        if adapter.disposition is WorkflowAdapterDisposition.NOT_ENABLED:
            return WorkflowTransitionOutcome.create(
                kind=WorkflowTransitionOutcomeKind.NOT_ENABLED,
                run_identity=transition_input.run.identity,
                request_identity=request.identity,
                prior_state_identity=prior.identity,
                prior_revision=transition_input.run.revision,
                validation=validation,
                adapter_evidence_identity=adapter.identity,
                reasons=adapter.reasons,
            )
        if adapter.disposition is WorkflowAdapterDisposition.BLOCKED:
            return WorkflowTransitionOutcome.create(
                kind=WorkflowTransitionOutcomeKind.BLOCKED,
                run_identity=transition_input.run.identity,
                request_identity=request.identity,
                prior_state_identity=prior.identity,
                prior_revision=transition_input.run.revision,
                validation=validation,
                adapter_evidence_identity=adapter.identity,
                reasons=adapter.reasons,
            )

        successor_state, successor_run = _successor(transition_input, adapter)
        return WorkflowTransitionOutcome.create(
            kind=WorkflowTransitionOutcomeKind.APPLIED,
            run_identity=transition_input.run.identity,
            request_identity=request.identity,
            prior_state_identity=prior.identity,
            prior_revision=transition_input.run.revision,
            validation=validation,
            adapter_evidence_identity=adapter.identity,
            successor_state=successor_state,
            successor_run=successor_run,
            reasons=adapter.reasons,
        )


def _successor(
    transition_input: WorkflowTransitionInput,
    adapter: WorkflowAdapterEvidence,
) -> tuple[WorkflowStateSnapshot, WorkflowRun]:
    run = transition_input.run
    prior = transition_input.prior_state
    request = transition_input.request
    assert adapter.successor_run_status is not None
    revision = run.revision + 1
    state = WorkflowStateSnapshot.create(
        run_identity=run.identity,
        definition_identity=run.definition_identity,
        revision=revision,
        run_status=adapter.successor_run_status,
        state_references=adapter.successor_state_references,
        predecessor_state_identity=prior.identity,
    )
    artifacts = _merge_artifacts(
        run.artifact_references,
        request.artifact_references,
        adapter.produced_artifact_references,
    )
    decisions = _merge_decisions(
        run.decision_references,
        request.decision_references,
        adapter.recorded_decision_references,
    )
    successor = WorkflowRun(
        identity=run.identity,
        run_key=run.run_key,
        definition_identity=run.definition_identity,
        subject_identity=run.subject_identity,
        current_state_identity=state.identity,
        revision=revision,
        status=adapter.successor_run_status,
        status_reasons=(
            ()
            if adapter.successor_run_status is WorkflowRunStatus.ACTIVE
            else adapter.reasons
        ),
        artifact_references=artifacts,
        decision_references=decisions,
        parent_run_identity=run.parent_run_identity,
        predecessor_run_identity=run.predecessor_run_identity,
    )
    return state, successor


def _validation_reasons(
    validation: WorkflowValidationResult,
) -> tuple[str, ...]:
    messages = tuple(item.message for item in validation.findings)
    maximum = WorkflowTransitionOutcome.MAX_REASONS
    if len(messages) <= maximum:
        return messages
    retained = messages[: maximum - 1]
    return retained + (
        f"{len(messages) - len(retained)} additional validation reasons "
        "retained in the validation result",
    )


def _evidence_identities(
    transition_input: WorkflowTransitionInput,
    validation: WorkflowValidationResult,
) -> tuple[WorkflowAuditReference, ...]:
    references = [WorkflowAuditReference(validation.identity)]
    if transition_input.adapter_evidence is not None:
        references.append(
            WorkflowAuditReference(transition_input.adapter_evidence.identity)
        )
    if transition_input.infrastructure_failure is not None:
        references.append(
            WorkflowAuditReference(
                transition_input.infrastructure_failure.identity
            )
        )
    return tuple(references)
