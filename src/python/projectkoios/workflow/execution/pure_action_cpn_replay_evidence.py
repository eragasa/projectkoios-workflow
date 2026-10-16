"""Models and factory for durable pure-CPN replay evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from string import hexdigits

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowCpnMarkingDecoder,
    ExperimentalWorkflowPureActionCpnPlanIdentity,
)
from projectkoios.workflow.core.identities import stable_identity
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
)
from projectkoios.workflow_sdk.identities import WorkflowMarkingIdentity

from .pure_action_cpn_replay_bundle import (
    ExperimentalWorkflowPureActionCpnReplayBundleIdentity,
)
from .pure_action_cpn_replay_serialization import (
    ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec,
)

_EVIDENCE_DOMAIN = (
    "projectkoios.workflow.experimental-pure-action-cpn-replay-evidence:0"
)


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity:
    value: str

    def __post_init__(self) -> None:
        _sha256(self.value, "CPN replay evidence identity")


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayEvidence:
    """Bind one compact commit to exact canonical CPN replay bytes."""

    identity: ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity = field(
        init=False
    )
    commit_identity: ExperimentalWorkflowPureActionCommitIdentity
    bundle_identity: ExperimentalWorkflowPureActionCpnReplayBundleIdentity
    cpn_plan_identity: ExperimentalWorkflowPureActionCpnPlanIdentity
    cpn_firing_result_identity: str
    predecessor_marking_identity: WorkflowMarkingIdentity
    successor_marking_identity: WorkflowMarkingIdentity
    bundle_bytes: bytes = field(repr=False)

    def __post_init__(self) -> None:
        if (
            type(self.commit_identity)
            is not ExperimentalWorkflowPureActionCommitIdentity
        ):
            raise TypeError(
                "commit_identity must be "
                "ExperimentalWorkflowPureActionCommitIdentity"
            )
        bundle = (
            ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().decode(
                self.bundle_bytes
            )
        )
        if bundle.identity != self.bundle_identity:
            raise ValueError("bundle identity differs from canonical bytes")
        if bundle.cpn_plan_identity != self.cpn_plan_identity:
            raise ValueError("CPN plan identity differs from canonical bundle")
        if (
            bundle.expected_firing_result_identity.value
            != self.cpn_firing_result_identity
        ):
            raise ValueError("CPN firing result differs from canonical bundle")
        if (
            type(self.predecessor_marking_identity)
            is not WorkflowMarkingIdentity
            or type(self.successor_marking_identity)
            is not WorkflowMarkingIdentity
        ):
            raise TypeError(
                "marking identities must be WorkflowMarkingIdentity"
            )
        marking_decoder = ExperimentalWorkflowCpnMarkingDecoder()
        predecessor = marking_decoder.decode(bundle.predecessor_marking_bytes)
        successor = marking_decoder.decode(bundle.successor_marking_bytes)
        if (
            predecessor.identity.value
            != self.predecessor_marking_identity.value
            or successor.identity.value != self.successor_marking_identity.value
        ):
            raise ValueError("marking identities differ from canonical bundle")
        object.__setattr__(
            self,
            "identity",
            ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity(
                stable_identity(
                    _EVIDENCE_DOMAIN,
                    self.commit_identity.value,
                    self.bundle_identity.value,
                    self.cpn_plan_identity.value,
                    self.cpn_firing_result_identity,
                    self.predecessor_marking_identity.value,
                    self.successor_marking_identity.value,
                    len(self.bundle_bytes),
                    sha256(self.bundle_bytes).hexdigest(),
                )
            ),
        )


class ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus(StrEnum):
    FOUND = "found"
    ABSENT = "absent"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult:
    status: ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus
    evidence: ExperimentalWorkflowPureActionCpnReplayEvidence | None
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.status)
            is not ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus
        ):
            raise TypeError("status must be CPN replay evidence read status")
        if (
            self.status
            is ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus.FOUND
        ):
            if (
                type(self.evidence)
                is not ExperimentalWorkflowPureActionCpnReplayEvidence
            ):
                raise TypeError("found status requires replay evidence")
            if self.diagnostics:
                raise ValueError("found status prohibits diagnostics")
        elif self.evidence is not None or not self.diagnostics:
            raise ValueError(
                "non-found status requires diagnostics and prohibits evidence"
            )


def experimental_cpn_replay_evidence(
    record: ExperimentalWorkflowPureActionCommitRecord,
    bundle_bytes: bytes,
) -> ExperimentalWorkflowPureActionCpnReplayEvidence:
    """Construct evidence only after exact commit/bundle correlation."""
    if type(record) is not ExperimentalWorkflowPureActionCommitRecord:
        raise TypeError(
            "record must be ExperimentalWorkflowPureActionCommitRecord"
        )
    bundle = ExperimentalWorkflowPureActionCpnReplayBundleJsonCodec().decode(
        bundle_bytes
    )
    marking_decoder = ExperimentalWorkflowCpnMarkingDecoder()
    predecessor = marking_decoder.decode(bundle.predecessor_marking_bytes)
    successor = marking_decoder.decode(bundle.successor_marking_bytes)
    if (
        bundle.cpn_plan_identity != record.cpn_plan_identity
        or bundle.expected_firing_result_identity.value
        != record.cpn_firing_result_identity
        or predecessor.identity.value
        != record.predecessor_marking_identity.value
        or successor.identity.value != record.successor_marking_identity.value
    ):
        raise ValueError("replay bundle differs from compact commit")
    return ExperimentalWorkflowPureActionCpnReplayEvidence(
        commit_identity=record.commit_identity,
        bundle_identity=bundle.identity,
        cpn_plan_identity=record.cpn_plan_identity,
        cpn_firing_result_identity=record.cpn_firing_result_identity,
        predecessor_marking_identity=record.predecessor_marking_identity,
        successor_marking_identity=record.successor_marking_identity,
        bundle_bytes=bundle_bytes,
    )


def _sha256(value: str, label: str) -> None:
    if (
        type(value) is not str
        or len(value) != 64
        or value != value.lower()
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


__all__ = [
    "ExperimentalWorkflowPureActionCpnReplayEvidence",
    "ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity",
    "ExperimentalWorkflowPureActionCpnReplayEvidenceReadResult",
    "ExperimentalWorkflowPureActionCpnReplayEvidenceReadStatus",
    "experimental_cpn_replay_evidence",
]
