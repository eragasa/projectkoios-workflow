"""Pure validation, transition processing, audit production, and replay.

This module performs no persistence, dispatch, external execution, clock access,
or mutation. Adapter results and infrastructure failures enter as explicit
immutable evidence supplied by outer layers.
"""

from __future__ import annotations

from dataclasses import dataclass

from .identities import (
    WorkflowAuditEventIdentity,
    WorkflowReplayIdentity,
    WorkflowTransitionOutcomeIdentity,
    stable_identity,
)
from .models import (
    WORKFLOW_CORE_CONTRACT_VERSION,
    WorkflowAdapterDisposition,
    WorkflowAdapterEvidence,
    WorkflowArtifactReference,
    WorkflowAuditEvent,
    WorkflowAuditReference,
    WorkflowDecisionReference,
    WorkflowDefinitionReference,
    WorkflowInfrastructureFailureEvidence,
    WorkflowRun,
    WorkflowRunStatus,
    WorkflowStateSnapshot,
    WorkflowTransitionOutcome,
    WorkflowTransitionOutcomeKind,
    WorkflowTransitionRequest,
    WorkflowValidationFinding,
    WorkflowValidationFindingCode,
    WorkflowValidationResult,
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
        expected = (
            ("definition", self.definition, WorkflowDefinitionReference),
            ("run", self.run, WorkflowRun),
            ("prior_state", self.prior_state, WorkflowStateSnapshot),
            ("request", self.request, WorkflowTransitionRequest),
        )
        for name, value, value_type in expected:
            if type(value) is not value_type:
                raise TypeError(f"{name} must be {value_type.__name__}")
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


@dataclass(frozen=True, slots=True)
class WorkflowTransitionExecution:
    """Pure transition outcome and its immutable audit event."""

    outcome: WorkflowTransitionOutcome
    audit_event: WorkflowAuditEvent

    def __post_init__(self) -> None:
        if type(self.outcome) is not WorkflowTransitionOutcome:
            raise TypeError("outcome must be WorkflowTransitionOutcome")
        if type(self.audit_event) is not WorkflowAuditEvent:
            raise TypeError("audit_event must be WorkflowAuditEvent")
        expected_subjects = (
            WorkflowAuditReference(self.outcome.request_identity),
            WorkflowAuditReference(self.outcome.identity),
        )
        expected_evidence = [
            WorkflowAuditReference(self.outcome.validation.identity)
        ]
        if self.outcome.adapter_evidence_identity is not None:
            expected_evidence.append(
                WorkflowAuditReference(self.outcome.adapter_evidence_identity)
            )
        if self.outcome.infrastructure_failure_identity is not None:
            expected_evidence.append(
                WorkflowAuditReference(
                    self.outcome.infrastructure_failure_identity
                )
            )
        expected_revision = (
            self.outcome.successor_run.revision
            if self.outcome.successor_run is not None
            else self.outcome.prior_revision
        )
        if (
            self.audit_event.run_identity != self.outcome.run_identity
            or self.audit_event.sequence_revision != expected_revision
            or self.audit_event.attempt_identity
            != self.outcome.request_identity
            or self.audit_event.event_kind
            != f"transition.{self.outcome.kind.value}"
            or self.audit_event.subject_references != expected_subjects
            or self.audit_event.evidence_references != tuple(expected_evidence)
        ):
            raise ValueError("audit event is inconsistent with its outcome")


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


@dataclass(frozen=True, slots=True)
class WorkflowReplayResult:
    """Deterministic comparison between retained and recomputed execution."""

    identity: WorkflowReplayIdentity
    expected_outcome_identity: WorkflowTransitionOutcomeIdentity
    replayed_outcome_identity: WorkflowTransitionOutcomeIdentity
    expected_audit_identity: WorkflowAuditEventIdentity
    replayed_audit_identity: WorkflowAuditEventIdentity
    matches: bool
    contract_version: str = WORKFLOW_CORE_CONTRACT_VERSION

    @classmethod
    def create(
        cls,
        *,
        expected: WorkflowTransitionExecution,
        replayed: WorkflowTransitionExecution,
    ) -> WorkflowReplayResult:
        """Create a content-identified replay comparison."""
        matches = expected == replayed
        identity = WorkflowReplayIdentity(
            stable_identity(
                "workflow-replay-result",
                expected.outcome.identity,
                replayed.outcome.identity,
                expected.audit_event.identity,
                replayed.audit_event.identity,
                matches,
                WORKFLOW_CORE_CONTRACT_VERSION,
            )
        )
        return cls(
            identity,
            expected.outcome.identity,
            replayed.outcome.identity,
            expected.audit_event.identity,
            replayed.audit_event.identity,
            matches,
        )

    def __post_init__(self) -> None:
        if type(self.identity) is not WorkflowReplayIdentity:
            raise TypeError("identity must be WorkflowReplayIdentity")
        for name in (
            "expected_outcome_identity",
            "replayed_outcome_identity",
        ):
            if (
                type(getattr(self, name))
                is not WorkflowTransitionOutcomeIdentity
            ):
                raise TypeError(
                    f"{name} must be WorkflowTransitionOutcomeIdentity"
                )
        for name in ("expected_audit_identity", "replayed_audit_identity"):
            if type(getattr(self, name)) is not WorkflowAuditEventIdentity:
                raise TypeError(f"{name} must be WorkflowAuditEventIdentity")
        if type(self.matches) is not bool:
            raise TypeError("matches must be a Boolean")
        if self.contract_version != WORKFLOW_CORE_CONTRACT_VERSION:
            raise ValueError("unsupported workflow-core contract version")
        expected_identity = WorkflowReplayIdentity(
            stable_identity(
                "workflow-replay-result",
                self.expected_outcome_identity,
                self.replayed_outcome_identity,
                self.expected_audit_identity,
                self.replayed_audit_identity,
                self.matches,
                WORKFLOW_CORE_CONTRACT_VERSION,
            )
        )
        if self.identity != expected_identity:
            raise ValueError("replay result identity is inconsistent")


class WorkflowTransitionReplayer:
    """Pure action recomputing a prior execution from its exact inputs."""

    def execute(
        self,
        transition_input: WorkflowTransitionInput,
        expected: WorkflowTransitionExecution,
    ) -> WorkflowReplayResult:
        """Replay without effects and compare immutable objects."""
        if type(transition_input) is not WorkflowTransitionInput:
            raise TypeError("transition_input must be WorkflowTransitionInput")
        if type(expected) is not WorkflowTransitionExecution:
            raise TypeError("expected must be WorkflowTransitionExecution")
        replayed = WorkflowTransitionProcessor().execute(transition_input)
        return WorkflowReplayResult.create(expected=expected, replayed=replayed)


def _validate_transition_input(
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


def _merge_artifacts(
    *collections: tuple[WorkflowArtifactReference, ...],
) -> tuple[WorkflowArtifactReference, ...]:
    by_identity: dict[str, WorkflowArtifactReference] = {}
    for item in (item for values in collections for item in values):
        existing = by_identity.get(item.identity.value)
        if existing is not None and existing != item:
            raise ValueError("artifact identity collision")
        by_identity[item.identity.value] = item
    return tuple(by_identity[key] for key in sorted(by_identity))


def _merge_decisions(
    *collections: tuple[WorkflowDecisionReference, ...],
) -> tuple[WorkflowDecisionReference, ...]:
    by_identity: dict[str, WorkflowDecisionReference] = {}
    for item in (item for values in collections for item in values):
        existing = by_identity.get(item.identity.value)
        if existing is not None and existing != item:
            raise ValueError("decision identity collision")
        by_identity[item.identity.value] = item
    return tuple(by_identity[key] for key in sorted(by_identity))


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
