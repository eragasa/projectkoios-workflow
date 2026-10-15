"""Canonical compact-event serialization for committed pure actions."""

from __future__ import annotations

import json
from typing import final

from projectkoios.workflow.compilation import (
    ExperimentalWorkflowPureActionCpnPlanIdentity,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowFiringRequestIdentity,
    WorkflowFiringResultIdentity,
    WorkflowMarkingIdentity,
    WorkflowNetInstanceIdentity,
)

from .pure_action_input_authority import (
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputSourceAuthority,
    ExperimentalWorkflowPureActionInputSourceAuthorityIdentity,
)
from .pure_action_inputs import (
    ExperimentalWorkflowPureActionInputSourceEvidenceIdentity,
)
from .pure_action_reservation import (
    ExperimentalWorkflowPureActionCommitIdentity,
    ExperimentalWorkflowPureActionCommitRecord,
    ExperimentalWorkflowPureActionReservationIdentity,
)
from .pure_action_source_repository import (
    ExperimentalWorkflowPureActionInputSourceReferenceIdentity,
    ExperimentalWorkflowPureActionInputSourceRevisionIdentity,
)

_SCHEMA = "projectkoios.workflow.experimental-pure-action-commit-event:0"
_MAX_EVENT_BYTES = 1_048_576


@final
class ExperimentalWorkflowPureActionCommitEventJsonCodec:
    """Encode and decode one strict canonical identity-only commit event."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        raise TypeError(
            "ExperimentalWorkflowPureActionCommitEventJsonCodec "
            "is not subclassable"
        )

    def encode(
        self, value: ExperimentalWorkflowPureActionCommitRecord
    ) -> bytes:
        """Return bounded canonical UTF-8 JSON for one compact commit."""
        record = _reconstruct_record(value)
        payload = json.dumps(
            {
                "commit": {
                    "commit_identity": record.commit_identity.value,
                    "cpn_firing_result_identity": (
                        record.cpn_firing_result_identity
                    ),
                    "cpn_plan_identity": record.cpn_plan_identity.value,
                    "firing_outcome_identity": record.firing_outcome_identity,
                    "input_authorization_identity": (
                        record.input_authorization_identity.value
                    ),
                    "invocation_outcome_identity": (
                        record.invocation_outcome_identity
                    ),
                    "mapped_result_identity": record.mapped_result_identity,
                    "net_instance_identity": record.net_instance_identity.value,
                    "owner_result_identity": record.owner_result_identity.value,
                    "predecessor_marking_identity": (
                        record.predecessor_marking_identity.value
                    ),
                    "predecessor_revision": record.predecessor_revision,
                    "request_identity": record.request_identity.value,
                    "reservation_identity": record.reservation_identity.value,
                    "source_authorities": [
                        {
                            "authority_identity": authority.identity.value,
                            "evidence_identity": (
                                authority.evidence_identity.value
                            ),
                            "reference_identity": (
                                authority.reference_identity.value
                            ),
                            "revision_identity": (
                                authority.revision_identity.value
                            ),
                        }
                        for authority in record.source_authorities
                    ],
                    "successor_marking_identity": (
                        record.successor_marking_identity.value
                    ),
                    "successor_revision": record.successor_revision,
                },
                "schema": _SCHEMA,
            },
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(payload) > _MAX_EVENT_BYTES:
            raise ValueError("commit event exceeds its byte bound")
        return payload

    def decode(
        self, value: bytes
    ) -> ExperimentalWorkflowPureActionCommitRecord:
        """Decode only the exact canonical v0 compact commit schema."""
        if type(value) is not bytes:
            raise TypeError("commit event must be bytes")
        if not value or len(value) > _MAX_EVENT_BYTES:
            raise ValueError("commit event must be nonempty and bounded")
        try:
            parsed = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("commit event must be valid UTF-8 JSON") from error
        canonical = json.dumps(
            parsed,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if canonical != value:
            raise ValueError("commit event must use canonical JSON")
        root = _object(parsed, {"commit", "schema"}, "commit event")
        if root["schema"] != _SCHEMA:
            raise ValueError("commit event schema is unsupported")
        commit = _object(
            root["commit"],
            {
                "commit_identity",
                "cpn_firing_result_identity",
                "cpn_plan_identity",
                "firing_outcome_identity",
                "input_authorization_identity",
                "invocation_outcome_identity",
                "mapped_result_identity",
                "net_instance_identity",
                "owner_result_identity",
                "predecessor_marking_identity",
                "predecessor_revision",
                "request_identity",
                "reservation_identity",
                "source_authorities",
                "successor_marking_identity",
                "successor_revision",
            },
            "commit",
        )
        authorities_value = commit["source_authorities"]
        if type(authorities_value) is not list:
            raise TypeError("source_authorities must be a list")
        authorities = tuple(
            _decode_authority(item, index)
            for index, item in enumerate(authorities_value)
        )
        try:
            return ExperimentalWorkflowPureActionCommitRecord(
                commit_identity=ExperimentalWorkflowPureActionCommitIdentity(
                    _text(commit["commit_identity"], "commit_identity")
                ),
                cpn_plan_identity=ExperimentalWorkflowPureActionCpnPlanIdentity(
                    _text(commit["cpn_plan_identity"], "cpn_plan_identity")
                ),
                reservation_identity=ExperimentalWorkflowPureActionReservationIdentity(
                    _text(
                        commit["reservation_identity"], "reservation_identity"
                    )
                ),
                net_instance_identity=WorkflowNetInstanceIdentity(
                    _text(
                        commit["net_instance_identity"],
                        "net_instance_identity",
                    )
                ),
                input_authorization_identity=ExperimentalWorkflowPureActionAuthorizedInputsIdentity(
                    _text(
                        commit["input_authorization_identity"],
                        "input_authorization_identity",
                    )
                ),
                source_authorities=authorities,
                invocation_outcome_identity=_text(
                    commit["invocation_outcome_identity"],
                    "invocation_outcome_identity",
                ),
                request_identity=WorkflowFiringRequestIdentity(
                    _text(commit["request_identity"], "request_identity")
                ),
                owner_result_identity=WorkflowFiringResultIdentity(
                    _text(
                        commit["owner_result_identity"], "owner_result_identity"
                    )
                ),
                mapped_result_identity=_text(
                    commit["mapped_result_identity"],
                    "mapped_result_identity",
                ),
                firing_outcome_identity=_text(
                    commit["firing_outcome_identity"],
                    "firing_outcome_identity",
                ),
                cpn_firing_result_identity=_text(
                    commit["cpn_firing_result_identity"],
                    "cpn_firing_result_identity",
                ),
                predecessor_marking_identity=WorkflowMarkingIdentity(
                    _text(
                        commit["predecessor_marking_identity"],
                        "predecessor_marking_identity",
                    )
                ),
                predecessor_revision=_integer(
                    commit["predecessor_revision"],
                    "predecessor_revision",
                ),
                successor_marking_identity=WorkflowMarkingIdentity(
                    _text(
                        commit["successor_marking_identity"],
                        "successor_marking_identity",
                    )
                ),
                successor_revision=_integer(
                    commit["successor_revision"],
                    "successor_revision",
                ),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "commit event contains invalid identities"
            ) from error


def _decode_authority(
    value: object,
    index: int,
) -> ExperimentalWorkflowPureActionInputSourceAuthority:
    authority = _object(
        value,
        {
            "authority_identity",
            "evidence_identity",
            "reference_identity",
            "revision_identity",
        },
        f"source_authorities[{index}]",
    )
    try:
        result = ExperimentalWorkflowPureActionInputSourceAuthority(
            reference_identity=ExperimentalWorkflowPureActionInputSourceReferenceIdentity(
                _text(authority["reference_identity"], "reference_identity")
            ),
            revision_identity=ExperimentalWorkflowPureActionInputSourceRevisionIdentity(
                _text(authority["revision_identity"], "revision_identity")
            ),
            evidence_identity=ExperimentalWorkflowPureActionInputSourceEvidenceIdentity(
                _text(authority["evidence_identity"], "evidence_identity")
            ),
        )
        retained_identity = (
            ExperimentalWorkflowPureActionInputSourceAuthorityIdentity(
                _text(authority["authority_identity"], "authority_identity")
            )
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "commit event contains invalid source authority"
        ) from error
    if result.identity != retained_identity:
        raise ValueError("source authority identity differs from its fields")
    return result


def _reconstruct_record(
    value: ExperimentalWorkflowPureActionCommitRecord,
) -> ExperimentalWorkflowPureActionCommitRecord:
    if type(value) is not ExperimentalWorkflowPureActionCommitRecord:
        raise TypeError(
            "value must be ExperimentalWorkflowPureActionCommitRecord"
        )
    reconstructed = ExperimentalWorkflowPureActionCommitRecord(
        commit_identity=value.commit_identity,
        cpn_plan_identity=value.cpn_plan_identity,
        reservation_identity=value.reservation_identity,
        net_instance_identity=value.net_instance_identity,
        input_authorization_identity=value.input_authorization_identity,
        source_authorities=value.source_authorities,
        invocation_outcome_identity=value.invocation_outcome_identity,
        request_identity=value.request_identity,
        owner_result_identity=value.owner_result_identity,
        mapped_result_identity=value.mapped_result_identity,
        firing_outcome_identity=value.firing_outcome_identity,
        cpn_firing_result_identity=value.cpn_firing_result_identity,
        predecessor_marking_identity=value.predecessor_marking_identity,
        predecessor_revision=value.predecessor_revision,
        successor_marking_identity=value.successor_marking_identity,
        successor_revision=value.successor_revision,
    )
    if reconstructed != value:
        raise ValueError("commit record differs after validation")
    return reconstructed


def _object(
    value: object,
    keys: set[str],
    label: str,
) -> dict[str, object]:
    if type(value) is not dict or set(value) != keys:
        raise ValueError(f"{label} must use the exact closed schema")
    return value


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise TypeError(f"{label} must be a nonempty string")
    return value


def _integer(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise TypeError(f"{label} must be a nonnegative integer")
    return value


__all__ = ["ExperimentalWorkflowPureActionCommitEventJsonCodec"]
