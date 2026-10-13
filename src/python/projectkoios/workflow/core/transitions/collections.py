"""Canonical merging for transition-owned reference collections."""

from ..records.references import (
    WorkflowArtifactReference,
    WorkflowDecisionReference,
)


def _merge_artifacts(
    *collections: tuple[WorkflowArtifactReference, ...],
) -> tuple[WorkflowArtifactReference, ...]:
    by_identity: dict[str, WorkflowArtifactReference] = {}
    for item in (item for values in collections for item in values):
        existing = by_identity.get(item.identity.value)
        if existing is not None and existing != item:
            raise ValueError("artifact identity collision")
        by_identity[item.identity.value] = item
    return tuple(by_identity[key] for key in sorted(by_identity))


def _merge_decisions(
    *collections: tuple[WorkflowDecisionReference, ...],
) -> tuple[WorkflowDecisionReference, ...]:
    by_identity: dict[str, WorkflowDecisionReference] = {}
    for item in (item for values in collections for item in values):
        existing = by_identity.get(item.identity.value)
        if existing is not None and existing != item:
            raise ValueError("decision identity collision")
        by_identity[item.identity.value] = item
    return tuple(by_identity[key] for key in sorted(by_identity))
