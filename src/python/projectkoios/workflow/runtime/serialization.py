"""Canonical private wire representation for workflow runtime events."""

from __future__ import annotations

import json
from typing import Any

from projectkoios.workflow.core import (
    WorkflowOperationIdentity,
    WorkflowRunIdentity,
    WorkflowStateIdentity,
    WorkflowTransitionRequestIdentity,
)

from .records import (
    WORKFLOW_RUNTIME_CONTRACT_VERSION,
    WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY,
    WorkflowOccurrenceIdentity,
    WorkflowRuntimeEvent,
    WorkflowRuntimeEventIdentity,
    WorkflowRuntimeEventKind,
    WorkflowRuntimeEvidenceReference,
)

_SCHEMA_IDENTITY = "projectkoios.workflow.runtime-event:1"
_KEYS = {
    "schema",
    "identity",
    "kind",
    "run_identity",
    "ordinal",
    "predecessor_event_identity",
    "core_revision",
    "core_state_identity",
    "occurrence_identity",
    "request_identity",
    "operation_identity",
    "evidence_references",
    "reason_codes",
    "contract_version",
    "producer_implementation",
}


class WorkflowRuntimeEventSerializer:
    """Encode and strictly decode canonical private runtime-event JSON."""

    @property
    def schema_identity(self) -> str:
        """Return the exact private schema identity."""
        return _SCHEMA_IDENTITY

    def encode(self, event: WorkflowRuntimeEvent) -> bytes:
        """Return deterministic UTF-8 bytes for one event."""
        if type(event) is not WorkflowRuntimeEvent:
            raise TypeError("event must be WorkflowRuntimeEvent")
        value = {
            "schema": _SCHEMA_IDENTITY,
            "identity": event.identity.value,
            "kind": event.kind.value,
            "run_identity": event.run_identity.value,
            "ordinal": event.ordinal,
            "predecessor_event_identity": (
                None
                if event.predecessor_event_identity is None
                else event.predecessor_event_identity.value
            ),
            "core_revision": event.core_revision,
            "core_state_identity": event.core_state_identity.value,
            "occurrence_identity": (
                None
                if event.occurrence_identity is None
                else event.occurrence_identity.value
            ),
            "request_identity": (
                None
                if event.request_identity is None
                else event.request_identity.value
            ),
            "operation_identity": (
                None
                if event.operation_identity is None
                else event.operation_identity.value
            ),
            "evidence_references": [
                {
                    "kind": reference.reference_kind,
                    "identity": reference.reference_identity,
                }
                for reference in event.evidence_references
            ],
            "reason_codes": list(event.reason_codes),
            "contract_version": event.contract_version,
            "producer_implementation": event.producer_implementation,
        }
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def decode(self, payload: bytes) -> WorkflowRuntimeEvent:
        """Decode canonical bytes, rejecting malformed or noncanonical data."""
        if type(payload) is not bytes:
            raise TypeError("payload must be built-in bytes")
        if payload.startswith(b"\xef\xbb\xbf"):
            raise ValueError("payload must not contain a UTF-8 BOM")

        def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in values:
                if key in result:
                    raise ValueError(f"duplicate JSON key {key}")
                result[key] = value
            return result

        try:
            value = json.loads(
                payload.decode("utf-8", errors="strict"),
                object_pairs_hook=pairs,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("payload must be one UTF-8 JSON object") from error
        if type(value) is not dict:
            raise TypeError("payload must represent an object")
        if set(value) != _KEYS:
            missing = sorted(_KEYS - set(value))
            unknown = sorted(set(value) - _KEYS)
            if missing:
                raise ValueError(f"missing field {missing[0]}")
            raise ValueError(f"unknown field {unknown[0]}")
        if value["schema"] != _SCHEMA_IDENTITY:
            raise ValueError("unsupported runtime event schema")
        if value["contract_version"] != WORKFLOW_RUNTIME_CONTRACT_VERSION:
            raise ValueError("unsupported runtime contract version")
        if value["producer_implementation"] != (
            WORKFLOW_RUNTIME_IMPLEMENTATION_IDENTITY
        ):
            raise ValueError("unsupported runtime producer implementation")
        evidence_value = value["evidence_references"]
        reasons_value = value["reason_codes"]
        if type(evidence_value) is not list or type(reasons_value) is not list:
            raise TypeError("event collections must be arrays")
        evidence: list[WorkflowRuntimeEvidenceReference] = []
        for item in evidence_value:
            if type(item) is not dict or set(item) != {"kind", "identity"}:
                raise ValueError("evidence reference is invalid")
            evidence.append(
                WorkflowRuntimeEvidenceReference(item["kind"], item["identity"])
            )
        event = WorkflowRuntimeEvent(
            WorkflowRuntimeEventIdentity(value["identity"]),
            WorkflowRuntimeEventKind(value["kind"]),
            WorkflowRunIdentity(value["run_identity"]),
            value["ordinal"],
            None
            if value["predecessor_event_identity"] is None
            else WorkflowRuntimeEventIdentity(
                value["predecessor_event_identity"]
            ),
            value["core_revision"],
            WorkflowStateIdentity(value["core_state_identity"]),
            None
            if value["occurrence_identity"] is None
            else WorkflowOccurrenceIdentity(value["occurrence_identity"]),
            None
            if value["request_identity"] is None
            else WorkflowTransitionRequestIdentity(value["request_identity"]),
            None
            if value["operation_identity"] is None
            else WorkflowOperationIdentity(value["operation_identity"]),
            tuple(evidence),
            tuple(reasons_value),
            value["contract_version"],
            value["producer_implementation"],
        )
        if self.encode(event) != payload:
            raise ValueError("runtime event bytes are noncanonical")
        return event
