"""Payload-free records for the local course-review workflow."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum

_SAFE_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$", re.ASCII)


def _safe_reference(value: object, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a built-in str")
    if _SAFE_REFERENCE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a compact non-path identity")
    return value


def _proposal_identity(parts: list[str]) -> OrganizerTeachingProposalIdentity:
    return OrganizerTeachingProposalIdentity(
        hashlib.sha256(
            json.dumps(
                {
                    "domain": "organizer-teaching-proposal:1",
                    "parts": [*parts, "teaching"],
                },
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
        ).hexdigest()
    )


class CourseReviewStage(StrEnum):
    """Closed review stages; publication is deliberately absent."""

    PROPOSAL_OBSERVED = "proposal_observed"
    COURSE_IDENTITY_CANDIDATE = "course_identity_candidate"
    SANITIZATION_EVIDENCE_REQUIRED = "sanitization_evidence_required"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    REVIEWED_RETAINED = "reviewed_retained"
    REVIEWED_EXCLUDED = "reviewed_excluded"


@dataclass(frozen=True, slots=True)
class OrganizerTeachingProposalIdentity:
    """Content identity of one bounded organizer proposal reference."""

    value: str

    def __post_init__(self) -> None:
        if (
            type(self.value) is not str
            or re.fullmatch(r"[0-9a-f]{64}", self.value) is None
        ):
            raise ValueError("proposal identity must be 64 lowercase hex")


@dataclass(frozen=True, slots=True)
class OrganizerTeachingProposalReference:
    """Organizer metadata supplied as input, never authority."""

    identity: OrganizerTeachingProposalIdentity
    proposal_identity: str
    proposal_set_identity: str
    model_identity: str
    catalog_revision: str
    course_identity: str
    source_metadata_sha256: str
    life_domain: str = "teaching"

    @classmethod
    def create(
        cls,
        *,
        proposal_identity: str,
        proposal_set_identity: str,
        model_identity: str,
        catalog_revision: str,
        course_identity: str,
        source_metadata_sha256: str,
    ) -> OrganizerTeachingProposalReference:
        """Construct a proposal reference from compact metadata identities."""
        parts = [
            _safe_reference(proposal_identity, "proposal_identity"),
            _safe_reference(proposal_set_identity, "proposal_set_identity"),
            _safe_reference(model_identity, "model_identity"),
            _safe_reference(catalog_revision, "catalog_revision"),
            _safe_reference(course_identity, "course_identity"),
        ]
        if (
            type(source_metadata_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", source_metadata_sha256) is None
        ):
            raise ValueError("source_metadata_sha256 must be 64 lowercase hex")
        complete_parts = [*parts, source_metadata_sha256]
        return cls(
            _proposal_identity(complete_parts),
            *complete_parts,
        )

    def __post_init__(self) -> None:
        if type(self.identity) is not OrganizerTeachingProposalIdentity:
            raise TypeError(
                "identity must be OrganizerTeachingProposalIdentity"
            )
        for field in (
            "proposal_identity",
            "proposal_set_identity",
            "model_identity",
            "catalog_revision",
            "course_identity",
        ):
            _safe_reference(getattr(self, field), field)
        if (
            type(self.source_metadata_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", self.source_metadata_sha256)
            is None
        ):
            raise ValueError("source_metadata_sha256 must be 64 lowercase hex")
        if self.life_domain != "teaching":
            raise ValueError("organizer proposal life_domain must be teaching")
        expected = _proposal_identity(
            [
                self.proposal_identity,
                self.proposal_set_identity,
                self.model_identity,
                self.catalog_revision,
                self.course_identity,
                self.source_metadata_sha256,
            ]
        )
        if self.identity != expected:
            raise ValueError("organizer proposal identity is inconsistent")
