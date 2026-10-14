"""Closed course-review stages."""

from enum import StrEnum


class CourseReviewStage(StrEnum):
    """Closed review stages; publication is deliberately absent."""

    PROPOSAL_OBSERVED = "proposal_observed"
    COURSE_IDENTITY_CANDIDATE = "course_identity_candidate"
    SANITIZATION_EVIDENCE_REQUIRED = "sanitization_evidence_required"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    REVIEWED_RETAINED = "reviewed_retained"
    REVIEWED_EXCLUDED = "reviewed_excluded"
