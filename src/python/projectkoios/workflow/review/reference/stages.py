"""Closed reference-review stages."""

from enum import StrEnum


class ReferenceReviewStage(StrEnum):
    """Closed review stages; publication is deliberately absent."""

    REFERENCE_EVIDENCE_OBSERVED = "reference_evidence_observed"
    MANUAL_CLAIM_REVIEW_REQUIRED = "manual_claim_review_required"
    REVIEWED_RETAINED = "reviewed_retained"
    REVIEWED_EXCLUDED = "reviewed_excluded"
