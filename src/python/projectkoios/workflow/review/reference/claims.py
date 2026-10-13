"""Ingestion-owned claims references admitted by review."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

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


def _sha256(value: object, field: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{field} must be 64 lowercase hex")
    return value


@dataclass(frozen=True, slots=True)
class IngestionClaimCandidateIdentity:
    """Content identity for one typed ingestion claim-candidate reference."""

    value: str

    def __post_init__(self) -> None:
        _sha256(self.value, "ingestion claim candidate identity")


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
