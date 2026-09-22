"""Verification for canonical private runtime-event serialization."""

from __future__ import annotations

import json

import pytest
from _runtime_fixtures import runtime_fixture
from projectkoios.workflow.runtime import (
    WorkflowRuntimeEvent,
    WorkflowRuntimeEventKind,
    WorkflowRuntimeEventSerializer,
    WorkflowRuntimeEvidenceReference,
)


def event() -> WorkflowRuntimeEvent:
    fixture = runtime_fixture()
    return WorkflowRuntimeEvent.create(
        kind=WorkflowRuntimeEventKind.RUN_STARTED,
        run_identity=fixture.started.run.identity,
        ordinal=0,
        predecessor_event_identity=None,
        core_revision=0,
        core_state_identity=fixture.started.state.identity,
        evidence_references=(
            WorkflowRuntimeEvidenceReference(
                "workflow-definition", fixture.definition.identity.value
            ),
        ),
    )


def test__runtime_event_serializer__is_exact_and_round_trips() -> None:
    serializer = WorkflowRuntimeEventSerializer()
    selected = event()

    payload = serializer.encode(selected)

    assert serializer.decode(payload) == selected
    assert serializer.encode(serializer.decode(payload)) == payload
    assert not payload.endswith(b"\n")
    assert b"course material" not in payload


def test__runtime_event_serializer__rejects_malformed_encodings() -> None:
    serializer = WorkflowRuntimeEventSerializer()
    payload = serializer.encode(event())
    value = json.loads(payload)
    value["unknown"] = True
    with pytest.raises(ValueError, match="unknown field"):
        serializer.decode(
            json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        )

    duplicate = (
        payload[:-1] + b',"schema":"projectkoios.workflow.runtime-event:1"}'
    )
    with pytest.raises(ValueError, match="duplicate JSON key"):
        serializer.decode(duplicate)

    with pytest.raises(ValueError, match="noncanonical"):
        serializer.decode(b" " + payload)


@pytest.mark.parametrize(
    "identity",
    (
        "/Users/operator/private/course.pdf",
        "C:\\private\\course.pdf",
        "file:///private/course.pdf",
        "private\nsecret",
    ),
)
def test__runtime_evidence_reference__rejects_paths_and_controls(
    identity: str,
) -> None:
    with pytest.raises(ValueError):
        WorkflowRuntimeEvidenceReference("artifact-reference", identity)


def test__runtime_event_serializer__rejects_identity_tamper() -> None:
    serializer = WorkflowRuntimeEventSerializer()
    value = json.loads(serializer.encode(event()))
    value["reason_codes"] = ["changed"]
    tampered = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()

    with pytest.raises(ValueError, match="identity is inconsistent"):
        serializer.decode(tampered)
