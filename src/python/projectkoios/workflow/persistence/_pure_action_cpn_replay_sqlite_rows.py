"""SQLite row codec and integrity checks for CPN replay evidence."""

from __future__ import annotations

import hashlib
import sqlite3

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
)
from projectkoios.workflow.execution.pure_action_cpn_replay_bundle import (
    ExperimentalWorkflowPureActionCpnReplayBundleIdentity,
)
from projectkoios.workflow.execution.pure_action_cpn_replay_evidence import (
    ExperimentalWorkflowPureActionCpnReplayEvidence,
    ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionCommitIdentity,
)
from projectkoios.workflow_sdk.identities import WorkflowMarkingIdentity

from ._sqlite_private import SQLiteStoreFault as _StoreFault


def _reconstruct_replay_evidence(
    value: ExperimentalWorkflowPureActionCpnReplayEvidence,
) -> ExperimentalWorkflowPureActionCpnReplayEvidence:
    if type(value) is not ExperimentalWorkflowPureActionCpnReplayEvidence:
        raise TypeError(
            "value must be ExperimentalWorkflowPureActionCpnReplayEvidence"
        )
    reconstructed = ExperimentalWorkflowPureActionCpnReplayEvidence(
        commit_identity=value.commit_identity,
        bundle_identity=value.bundle_identity,
        cpn_plan_identity=value.cpn_plan_identity,
        cpn_firing_result_identity=value.cpn_firing_result_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        successor_marking_identity=value.successor_marking_identity,
        bundle_bytes=value.bundle_bytes,
    )
    if reconstructed != value:
        raise ValueError("CPN replay evidence differs after reconstruction")
    return reconstructed


def _insert_replay_evidence(
    connection: sqlite3.Connection,
    evidence: ExperimentalWorkflowPureActionCpnReplayEvidence,
) -> None:
    existing = connection.execute(
        "SELECT event_bytes, event_digest FROM cpn_replay_bundles "
        "WHERE bundle_identity = ?",
        (evidence.bundle_identity.value,),
    ).fetchone()
    bundle_digest = hashlib.sha256(evidence.bundle_bytes).digest()
    if existing is None:
        connection.execute(
            "INSERT INTO cpn_replay_bundles VALUES (?, ?, ?)",
            (
                evidence.bundle_identity.value,
                evidence.bundle_bytes,
                bundle_digest,
            ),
        )
    elif tuple(existing) != (evidence.bundle_bytes, bundle_digest):
        raise _StoreFault("cpn_replay_bundle_identity_mismatch")
    connection.execute(
        "INSERT INTO commit_cpn_replay_evidence VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?)",
        (
            evidence.commit_identity.value,
            evidence.identity.value,
            evidence.bundle_identity.value,
            evidence.cpn_plan_identity.value,
            evidence.cpn_firing_result_identity,
            evidence.predecessor_marking_identity.value,
            evidence.successor_marking_identity.value,
            _replay_evidence_digest(evidence),
        ),
    )


def _load_replay_evidence_pair(
    connection: sqlite3.Connection,
    commit_identity: ExperimentalWorkflowPureActionCommitIdentity,
) -> ExperimentalWorkflowPureActionCpnReplayEvidence | None:
    row = connection.execute(
        "SELECT e.evidence_identity, e.bundle_identity, e.cpn_plan_identity, "
        "e.cpn_firing_result_identity, e.predecessor_marking_identity, "
        "e.successor_marking_identity, e.evidence_digest, "
        "b.event_bytes, b.event_digest, c.cpn_plan_identity, "
        "c.cpn_firing_result_identity, c.predecessor_marking_identity, "
        "c.successor_marking_identity "
        "FROM commit_cpn_replay_evidence e LEFT JOIN cpn_replay_bundles b "
        "ON b.bundle_identity = e.bundle_identity LEFT JOIN commits c "
        "ON c.commit_identity = e.commit_identity WHERE e.commit_identity = ?",
        (commit_identity.value,),
    ).fetchone()
    if row is None:
        return None
    if len(row) != 13:
        raise _StoreFault("invalid_cpn_replay_evidence_shape")
    if tuple(row[2:6]) != tuple(row[9:13]):
        raise _StoreFault("cpn_replay_commit_correlation_mismatch")
    bundle_bytes, bundle_digest = row[7], row[8]
    if type(bundle_bytes) is not bytes or type(bundle_digest) is not bytes:
        raise _StoreFault("invalid_cpn_replay_bundle")
    if hashlib.sha256(bundle_bytes).digest() != bundle_digest:
        raise _StoreFault("cpn_replay_bundle_digest_mismatch")
    try:
        evidence = ExperimentalWorkflowPureActionCpnReplayEvidence(
            commit_identity=commit_identity,
            bundle_identity=ExperimentalWorkflowPureActionCpnReplayBundleIdentity(
                _required_replay_text(row[1], "bundle_identity")
            ),
            cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
                _required_replay_text(row[2], "cpn_plan_identity")
            ),
            cpn_firing_result_identity=_required_replay_text(
                row[3], "cpn_firing_result_identity"
            ),
            predecessor_marking_identity=WorkflowMarkingIdentity(
                _required_replay_text(row[4], "predecessor_marking_identity")
            ),
            successor_marking_identity=WorkflowMarkingIdentity(
                _required_replay_text(row[5], "successor_marking_identity")
            ),
            bundle_bytes=bundle_bytes,
        )
        retained_identity = (
            ExperimentalWorkflowPureActionCpnReplayEvidenceIdentity(
                _required_replay_text(row[0], "evidence_identity")
            )
        )
    except (TypeError, ValueError) as error:
        raise _StoreFault("invalid_cpn_replay_evidence") from error
    if evidence.identity != retained_identity:
        raise _StoreFault("cpn_replay_evidence_identity_mismatch")
    digest = row[6]
    if type(digest) is not bytes or digest != _replay_evidence_digest(evidence):
        raise _StoreFault("cpn_replay_evidence_digest_mismatch")
    return evidence


def _replay_evidence_digest(
    evidence: ExperimentalWorkflowPureActionCpnReplayEvidence,
) -> bytes:
    digest = hashlib.sha256(
        b"projectkoios.workflow.experimental-pure-action-cpn-replay-row:0\x00"
    )
    for value in (
        evidence.identity.value,
        evidence.commit_identity.value,
        evidence.bundle_identity.value,
        evidence.cpn_plan_identity.value,
        evidence.cpn_firing_result_identity,
        evidence.predecessor_marking_identity.value,
        evidence.successor_marking_identity.value,
        str(len(evidence.bundle_bytes)),
        hashlib.sha256(evidence.bundle_bytes).hexdigest(),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.digest()


def _required_replay_text(value: object, field: str) -> str:
    if type(value) is not str or not value:
        raise _StoreFault(f"invalid_{field}")
    return value


__all__ = [
    "_insert_replay_evidence",
    "_load_replay_evidence_pair",
    "_reconstruct_replay_evidence",
]
