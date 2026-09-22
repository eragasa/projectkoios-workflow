"""Payload-free references for ingestion-owned research evidence."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum

INGESTION_REFERENCE_EVIDENCE_CONTRACT_ID = (
    "projectkoios.ingestion.reference-evidence"
)
INGESTION_REFERENCE_EVIDENCE_CONTRACT_VERSION = "0.1.0"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_RECORD_ID = re.compile(r"reference-evidence-record:sha256:[0-9a-f]{64}")
_BLOB_ID = re.compile(r"blob:sha256:([0-9a-f]{64})")
_MEDIA_TYPE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9!#$&^_.+-]+"
)


def _sha256(value: object, field: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{field} must be 64 lowercase hex")
    return value


class ReferenceReviewStage(StrEnum):
    """Closed review stages; publication is deliberately absent."""

    REFERENCE_EVIDENCE_OBSERVED = "reference_evidence_observed"
    MANUAL_CLAIM_REVIEW_REQUIRED = "manual_claim_review_required"
    REVIEWED_RETAINED = "reviewed_retained"
    REVIEWED_EXCLUDED = "reviewed_excluded"


@dataclass(frozen=True, slots=True)
class IngestionReferenceEvidenceIdentity:
    """Content identity for one typed ingestion-evidence reference."""

    value: str

    def __post_init__(self) -> None:
        _sha256(self.value, "ingestion evidence identity")


@dataclass(frozen=True, slots=True)
class IngestionReferenceEvidenceReference:
    """Bounded ingestion output supplied as review input, never authority."""

    identity: IngestionReferenceEvidenceIdentity
    record_identity: str
    source_blob_identity: str
    source_sha256: str
    source_byte_length: int
    source_media_type: str
    extraction_artifact_sha256: str
    transcript_artifact_sha256: str
    audit_artifact_sha256: str
    contract_id: str = INGESTION_REFERENCE_EVIDENCE_CONTRACT_ID
    contract_version: str = INGESTION_REFERENCE_EVIDENCE_CONTRACT_VERSION
    completeness: str = "complete"
    transcript_status: str = "automated_unreviewed"

    @classmethod
    def create(
        cls,
        *,
        record_identity: str,
        source_blob_identity: str,
        source_sha256: str,
        source_byte_length: int,
        source_media_type: str,
        extraction_artifact_sha256: str,
        transcript_artifact_sha256: str,
        audit_artifact_sha256: str,
    ) -> IngestionReferenceEvidenceReference:
        """Construct a reference from an already verified ingestion record."""
        parts = cls._validated_parts(
            record_identity=record_identity,
            source_blob_identity=source_blob_identity,
            source_sha256=source_sha256,
            source_byte_length=source_byte_length,
            source_media_type=source_media_type,
            extraction_artifact_sha256=extraction_artifact_sha256,
            transcript_artifact_sha256=transcript_artifact_sha256,
            audit_artifact_sha256=audit_artifact_sha256,
        )
        identity = hashlib.sha256(
            json.dumps(
                {
                    "domain": "ingestion-reference-evidence-input:1",
                    "parts": parts,
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        ).hexdigest()
        return cls(
            IngestionReferenceEvidenceIdentity(identity),
            record_identity,
            source_blob_identity,
            source_sha256,
            source_byte_length,
            source_media_type,
            extraction_artifact_sha256,
            transcript_artifact_sha256,
            audit_artifact_sha256,
        )

    @classmethod
    def _validated_parts(
        cls,
        *,
        record_identity: object,
        source_blob_identity: object,
        source_sha256: object,
        source_byte_length: object,
        source_media_type: object,
        extraction_artifact_sha256: object,
        transcript_artifact_sha256: object,
        audit_artifact_sha256: object,
    ) -> list[str | int]:
        if (
            type(record_identity) is not str
            or _RECORD_ID.fullmatch(record_identity) is None
        ):
            raise ValueError("record_identity has an invalid identity grammar")
        digest = _sha256(source_sha256, "source_sha256")
        if type(source_blob_identity) is not str:
            raise TypeError("source_blob_identity must be a built-in str")
        match = _BLOB_ID.fullmatch(source_blob_identity)
        if match is None or match.group(1) != digest:
            raise ValueError("source blob identity must bind source_sha256")
        if (
            type(source_byte_length) is not int
            or source_byte_length < 0
            or source_byte_length > 128_000_000
        ):
            raise ValueError("source_byte_length is outside its bound")
        if (
            type(source_media_type) is not str
            or _MEDIA_TYPE.fullmatch(source_media_type) is None
        ):
            raise ValueError("source_media_type is invalid")
        return [
            record_identity,
            source_blob_identity,
            digest,
            source_byte_length,
            source_media_type,
            _sha256(
                extraction_artifact_sha256,
                "extraction_artifact_sha256",
            ),
            _sha256(
                transcript_artifact_sha256,
                "transcript_artifact_sha256",
            ),
            _sha256(audit_artifact_sha256, "audit_artifact_sha256"),
            INGESTION_REFERENCE_EVIDENCE_CONTRACT_ID,
            INGESTION_REFERENCE_EVIDENCE_CONTRACT_VERSION,
            "complete",
            "automated_unreviewed",
        ]

    def __post_init__(self) -> None:
        if type(self.identity) is not IngestionReferenceEvidenceIdentity:
            raise TypeError(
                "identity must be IngestionReferenceEvidenceIdentity"
            )
        if self.contract_id != INGESTION_REFERENCE_EVIDENCE_CONTRACT_ID:
            raise ValueError("unsupported ingestion evidence contract ID")
        if self.contract_version != (
            INGESTION_REFERENCE_EVIDENCE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported ingestion evidence contract version")
        if self.completeness != "complete":
            raise ValueError("only complete ingestion evidence is reviewable")
        if self.transcript_status != "automated_unreviewed":
            raise ValueError(
                "ingestion transcript must remain automated_unreviewed"
            )
        parts = self._validated_parts(
            record_identity=self.record_identity,
            source_blob_identity=self.source_blob_identity,
            source_sha256=self.source_sha256,
            source_byte_length=self.source_byte_length,
            source_media_type=self.source_media_type,
            extraction_artifact_sha256=self.extraction_artifact_sha256,
            transcript_artifact_sha256=self.transcript_artifact_sha256,
            audit_artifact_sha256=self.audit_artifact_sha256,
        )
        expected = hashlib.sha256(
            json.dumps(
                {
                    "domain": "ingestion-reference-evidence-input:1",
                    "parts": parts,
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        ).hexdigest()
        if self.identity.value != expected:
            raise ValueError("ingestion evidence identity is inconsistent")
