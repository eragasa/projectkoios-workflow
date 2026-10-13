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
INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_ID = (
    "projectkoios.ingestion.reference-claim-candidate"
)
INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_VERSION = "0.1.0"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_RECORD_ID = re.compile(r"reference-evidence-record:sha256:[0-9a-f]{64}")
_BLOB_ID = re.compile(r"blob:sha256:([0-9a-f]{64})")
_CANDIDATE_ID = re.compile(r"reference-claim-candidate:sha256:[0-9a-f]{64}")
_CLAIM_ID = re.compile(r"research-claim:sha256:[0-9a-f]{64}")
_LOCATOR_RESULT_ID = re.compile(
    r"reference-page-locator-result:sha256:[0-9a-f]{64}"
)
_TRANSCRIPT_ID = re.compile(r"clean-transcript-artifact:sha256:[0-9a-f]{64}")
_PAGE_ID = re.compile(r"clean-transcript-page:sha256:[0-9a-f]{64}")
_ANCHOR_ID = re.compile(r"reference-topic-anchor:sha256:[0-9a-f]{64}")
_MAX_SOURCE_BYTES = 128_000_000
_MAX_PAGE_BYTES = 8_000_000
_MAX_ANCHORS = 32
_CANDIDATE_LIMITATIONS = (
    "automated_unreviewed",
    "citation_candidate_only",
    "manual_claim_review_required",
    "not_claim_support",
    "not_human_proofread",
    "not_publication_suitable",
    "not_scientifically_validated",
)
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
class IngestionClaimCandidateIdentity:
    """Content identity for one typed ingestion claim-candidate reference."""

    value: str

    def __post_init__(self) -> None:
        _sha256(self.value, "ingestion claim candidate identity")


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
            or source_byte_length > _MAX_SOURCE_BYTES
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


@dataclass(frozen=True, slots=True)
class IngestionClaimCandidateReference:
    """Payload-free ingestion claim candidate supplied for manual review."""

    identity: IngestionClaimCandidateIdentity
    candidate_identity: str
    claim_identity: str
    reference_evidence_record_identity: str
    locator_result_identity: str
    source_blob_identity: str
    source_sha256: str
    transcript_identity: str
    page_identity: str
    page_index: int
    page_text_sha256: str
    page_text_utf8_byte_length: int
    matched_topic_anchor_identities: tuple[str, ...]
    contract_id: str = INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_ID
    contract_version: str = INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_VERSION
    status: str = "manual_review_required"
    limitations: tuple[str, ...] = _CANDIDATE_LIMITATIONS

    @classmethod
    def create(
        cls,
        *,
        candidate_identity: str,
        claim_identity: str,
        reference_evidence_record_identity: str,
        locator_result_identity: str,
        source_blob_identity: str,
        source_sha256: str,
        transcript_identity: str,
        page_identity: str,
        page_index: int,
        page_text_sha256: str,
        page_text_utf8_byte_length: int,
        matched_topic_anchor_identities: tuple[str, ...],
    ) -> IngestionClaimCandidateReference:
        """Construct a reference from an already verified candidate."""
        parts = cls._validated_parts(
            candidate_identity=candidate_identity,
            claim_identity=claim_identity,
            reference_evidence_record_identity=(
                reference_evidence_record_identity
            ),
            locator_result_identity=locator_result_identity,
            source_blob_identity=source_blob_identity,
            source_sha256=source_sha256,
            transcript_identity=transcript_identity,
            page_identity=page_identity,
            page_index=page_index,
            page_text_sha256=page_text_sha256,
            page_text_utf8_byte_length=page_text_utf8_byte_length,
            matched_topic_anchor_identities=(matched_topic_anchor_identities),
        )
        identity = hashlib.sha256(
            json.dumps(
                {
                    "domain": "ingestion-reference-claim-candidate-input:1",
                    "parts": parts,
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        ).hexdigest()
        return cls(
            IngestionClaimCandidateIdentity(identity),
            candidate_identity,
            claim_identity,
            reference_evidence_record_identity,
            locator_result_identity,
            source_blob_identity,
            source_sha256,
            transcript_identity,
            page_identity,
            page_index,
            page_text_sha256,
            page_text_utf8_byte_length,
            matched_topic_anchor_identities,
        )

    @classmethod
    def _validated_parts(
        cls,
        *,
        candidate_identity: object,
        claim_identity: object,
        reference_evidence_record_identity: object,
        locator_result_identity: object,
        source_blob_identity: object,
        source_sha256: object,
        transcript_identity: object,
        page_identity: object,
        page_index: object,
        page_text_sha256: object,
        page_text_utf8_byte_length: object,
        matched_topic_anchor_identities: object,
    ) -> list[object]:
        for value, pattern, name in (
            (candidate_identity, _CANDIDATE_ID, "candidate_identity"),
            (claim_identity, _CLAIM_ID, "claim_identity"),
            (
                reference_evidence_record_identity,
                _RECORD_ID,
                "reference_evidence_record_identity",
            ),
            (
                locator_result_identity,
                _LOCATOR_RESULT_ID,
                "locator_result_identity",
            ),
            (transcript_identity, _TRANSCRIPT_ID, "transcript_identity"),
            (page_identity, _PAGE_ID, "page_identity"),
        ):
            if type(value) is not str or pattern.fullmatch(value) is None:
                raise ValueError(f"{name} has an invalid identity grammar")
        source_digest = _sha256(source_sha256, "source_sha256")
        if type(source_blob_identity) is not str:
            raise TypeError("source_blob_identity must be a built-in str")
        blob_match = _BLOB_ID.fullmatch(source_blob_identity)
        if blob_match is None or blob_match.group(1) != source_digest:
            raise ValueError("source blob identity must bind source_sha256")
        if type(page_index) is not int or page_index < 0:
            raise ValueError("page_index must be a nonnegative built-in int")
        page_digest = _sha256(page_text_sha256, "page_text_sha256")
        if (
            type(page_text_utf8_byte_length) is not int
            or page_text_utf8_byte_length < 0
            or page_text_utf8_byte_length > _MAX_PAGE_BYTES
        ):
            raise ValueError("page text byte length is outside its bound")
        anchors = matched_topic_anchor_identities
        if (
            type(anchors) is not tuple
            or not anchors
            or anchors != tuple(sorted(anchors))
            or len(anchors) != len(set(anchors))
            or len(anchors) > _MAX_ANCHORS
            or any(
                type(anchor) is not str or _ANCHOR_ID.fullmatch(anchor) is None
                for anchor in anchors
            )
        ):
            raise ValueError(
                "matched topic anchors must be a bounded identity tuple"
            )
        return [
            candidate_identity,
            claim_identity,
            reference_evidence_record_identity,
            locator_result_identity,
            source_blob_identity,
            source_digest,
            transcript_identity,
            page_identity,
            page_index,
            page_digest,
            page_text_utf8_byte_length,
            list(anchors),
            INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_ID,
            INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_VERSION,
            "manual_review_required",
            list(_CANDIDATE_LIMITATIONS),
        ]

    def __post_init__(self) -> None:
        if type(self.identity) is not IngestionClaimCandidateIdentity:
            raise TypeError("identity must be IngestionClaimCandidateIdentity")
        if self.contract_id != (
            INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_ID
        ):
            raise ValueError("unsupported ingestion candidate contract ID")
        if self.contract_version != (
            INGESTION_REFERENCE_CLAIM_CANDIDATE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported ingestion candidate contract version")
        if self.status != "manual_review_required":
            raise ValueError("ingestion candidate must require manual review")
        if self.limitations != _CANDIDATE_LIMITATIONS:
            raise ValueError("ingestion candidate limitations are incomplete")
        parts = self._validated_parts(
            candidate_identity=self.candidate_identity,
            claim_identity=self.claim_identity,
            reference_evidence_record_identity=(
                self.reference_evidence_record_identity
            ),
            locator_result_identity=self.locator_result_identity,
            source_blob_identity=self.source_blob_identity,
            source_sha256=self.source_sha256,
            transcript_identity=self.transcript_identity,
            page_identity=self.page_identity,
            page_index=self.page_index,
            page_text_sha256=self.page_text_sha256,
            page_text_utf8_byte_length=self.page_text_utf8_byte_length,
            matched_topic_anchor_identities=(
                self.matched_topic_anchor_identities
            ),
        )
        expected = hashlib.sha256(
            json.dumps(
                {
                    "domain": "ingestion-reference-claim-candidate-input:1",
                    "parts": parts,
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        ).hexdigest()
        if self.identity.value != expected:
            raise ValueError("ingestion candidate identity is inconsistent")
