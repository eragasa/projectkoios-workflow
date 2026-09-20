"""Verification for immutable workflow-core records and identities."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest
from _core_fixtures import core_fixture
from projectkoios.workflow.core import (
    WorkflowActorIdentity,
    WorkflowArtifactDisposition,
    WorkflowArtifactReference,
    WorkflowArtifactReferenceIdentity,
    WorkflowAuditReference,
    WorkflowDecisionReferenceIdentity,
    WorkflowDefinitionReference,
    WorkflowExternalReferenceIdentity,
    WorkflowIdempotencyIdentity,
    WorkflowOperationIdentity,
    WorkflowRequestBounds,
    WorkflowRunStarter,
    WorkflowTransitionRequest,
    WorkflowTypedReference,
)

_DIGEST = "b" * 64


def test__workflow_records__remain_immutable_and_deterministic() -> None:
    """Equivalent starts have equal identities and cannot be mutated."""
    fixture = core_fixture()
    repeated = WorkflowRunStarter().execute(
        definition=fixture.definition,
        subject_identity=fixture.subject,
        run_key=fixture.run.run_key,
        initial_state_references=fixture.state.state_references,
    )

    assert repeated.run == fixture.run
    assert repeated.state == fixture.state
    with pytest.raises(FrozenInstanceError):
        fixture.run.revision = 4  # type: ignore[misc]


def test__workflow_definition__canonicalizes_operation_identity_order() -> None:
    """Definition identity does not depend on caller collection order."""
    first = WorkflowOperationIdentity("a")
    second = WorkflowOperationIdentity("b")

    left = WorkflowDefinitionReference.create(
        contract_id="test.definition",
        definition_version="1",
        definition_digest_sha256=_DIGEST,
        operation_identities=(second, first),
    )
    right = WorkflowDefinitionReference.create(
        contract_id="test.definition",
        definition_version="1",
        definition_digest_sha256=_DIGEST,
        operation_identities=(first, second),
    )

    assert left == right
    assert left.operation_identities == (first, second)


def test__workflow_artifact__does_not_encode_domain_acceptance() -> None:
    """Artifact disposition records origin, not scientific acceptance."""
    external = WorkflowExternalReferenceIdentity("artifact:one")
    provenance = WorkflowExternalReferenceIdentity("provenance:one")
    produced = WorkflowArtifactReference.create(
        artifact_identity=external,
        artifact_kind="literal-transcript",
        digest_sha256=_DIGEST,
        role="output",
        disposition=WorkflowArtifactDisposition.GENERATED_UNREVIEWED,
        provenance_identity=provenance,
    )
    observed = WorkflowArtifactReference.create(
        artifact_identity=external,
        artifact_kind="literal-transcript",
        digest_sha256=_DIGEST,
        role="output",
        disposition=WorkflowArtifactDisposition.OBSERVED,
        provenance_identity=provenance,
    )

    assert produced.identity != observed.identity
    assert (
        produced.disposition is WorkflowArtifactDisposition.GENERATED_UNREVIEWED
    )
    assert observed.disposition is WorkflowArtifactDisposition.OBSERVED
    assert {item.value for item in WorkflowArtifactDisposition} == {
        "observed",
        "generated_unreviewed",
    }


def test__audit_reference__preserves_artifact_and_decision_nominality() -> None:
    """Artifact and decision audit subjects remain distinct nominal values."""
    artifact_identity = WorkflowArtifactReferenceIdentity("same-value")
    decision_identity = WorkflowDecisionReferenceIdentity("same-value")

    artifact_reference = WorkflowAuditReference(artifact_identity)
    decision_reference = WorkflowAuditReference(decision_identity)

    assert type(artifact_reference.reference_identity) is (
        WorkflowArtifactReferenceIdentity
    )
    assert type(decision_reference.reference_identity) is (
        WorkflowDecisionReferenceIdentity
    )
    assert artifact_reference != decision_reference


def test__workflow_artifact__rejects_identity_tampering() -> None:
    """Constructors reject identities inconsistent with record content."""
    artifact = WorkflowArtifactReference.create(
        artifact_identity=WorkflowExternalReferenceIdentity("artifact:one"),
        artifact_kind="transcript",
        digest_sha256=_DIGEST,
        role="output",
        disposition=WorkflowArtifactDisposition.GENERATED_UNREVIEWED,
        provenance_identity=WorkflowExternalReferenceIdentity("provenance:one"),
    )

    with pytest.raises(ValueError, match="identity is inconsistent"):
        replace(
            artifact,
            identity=WorkflowArtifactReferenceIdentity("artifact-ref:tampered"),
        )


def test__workflow_request__preserves_artifact_reference_order() -> None:
    """Request identity binds caller-owned artifact order exactly."""
    fixture = core_fixture()
    artifacts = tuple(
        sorted(
            (
                WorkflowArtifactReference.create(
                    artifact_identity=WorkflowExternalReferenceIdentity(
                        "artifact:first"
                    ),
                    artifact_kind="transcript",
                    digest_sha256="c" * 64,
                    role="input",
                    disposition=WorkflowArtifactDisposition.OBSERVED,
                    provenance_identity=WorkflowExternalReferenceIdentity(
                        "provenance:first"
                    ),
                ),
                WorkflowArtifactReference.create(
                    artifact_identity=WorkflowExternalReferenceIdentity(
                        "artifact:second"
                    ),
                    artifact_kind="chapter-map",
                    digest_sha256="d" * 64,
                    role="input",
                    disposition=WorkflowArtifactDisposition.OBSERVED,
                    provenance_identity=WorkflowExternalReferenceIdentity(
                        "provenance:second"
                    ),
                ),
            ),
            key=lambda item: item.identity.value,
            reverse=True,
        )
    )

    request = WorkflowTransitionRequest.create(
        run_identity=fixture.run.identity,
        expected_prior_state_identity=fixture.state.identity,
        expected_revision=fixture.run.revision,
        operation_identity=fixture.operation,
        input_references=(),
        artifact_references=artifacts,
        decision_references=(),
        actor_identity=WorkflowActorIdentity("operator:test"),
        authority_reference=fixture.authority,
        idempotency_identity=WorkflowIdempotencyIdentity("request:ordered"),
    )

    assert request.artifact_references == artifacts


def test__workflow_request__rejects_unbounded_collections() -> None:
    """Request construction enforces caller-selected collection bounds."""
    fixture = core_fixture()
    bounds = WorkflowRequestBounds(max_input_references=1)

    with pytest.raises(ValueError, match="input references exceed"):
        WorkflowTransitionRequest.create(
            run_identity=fixture.run.identity,
            expected_prior_state_identity=fixture.state.identity,
            expected_revision=fixture.run.revision,
            operation_identity=fixture.operation,
            input_references=(
                WorkflowTypedReference(
                    "input",
                    WorkflowExternalReferenceIdentity("input:one"),
                ),
                WorkflowTypedReference(
                    "input",
                    WorkflowExternalReferenceIdentity("input:two"),
                ),
            ),
            artifact_references=(),
            decision_references=(),
            actor_identity=WorkflowActorIdentity("operator:test"),
            authority_reference=fixture.authority,
            idempotency_identity=WorkflowIdempotencyIdentity("request:test"),
            bounds=bounds,
        )


def test__workflow_typed_reference__rejects_private_path_payload() -> None:
    """A reference stores identities and digests, not unbounded path fields."""
    fields = set(WorkflowTypedReference.__dataclass_fields__)

    assert fields == {"reference_kind", "reference_identity", "digest_sha256"}
    assert "path" not in fields
    assert "payload" not in fields
