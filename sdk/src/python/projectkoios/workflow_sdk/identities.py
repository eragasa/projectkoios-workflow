"""Nominal identities for the Workflow SDK pure-firing boundary."""

from __future__ import annotations

from dataclasses import dataclass

from ._validation import validate_identity, validate_sha256


@dataclass(frozen=True, slots=True)
class _LexicalIdentity:
    value: str

    def __post_init__(self) -> None:
        validate_identity(self.value, type(self).__name__)


@dataclass(frozen=True, slots=True)
class _ContentIdentity:
    value: str

    def __post_init__(self) -> None:
        validate_sha256(self.value, type(self).__name__)


@dataclass(frozen=True, slots=True)
class WorkflowFirerIdentity(_LexicalIdentity):
    """Identify one stable Workflow integration operation."""


@dataclass(frozen=True, slots=True)
class WorkflowFirerImplementationIdentity(_LexicalIdentity):
    """Identify one exact firer implementation revision."""


@dataclass(frozen=True, slots=True)
class WorkflowTransitionBindingIdentity(_ContentIdentity):
    """Identify one exact immutable transition-to-firer binding."""


@dataclass(frozen=True, slots=True)
class WorkflowDefinitionIdentity(_LexicalIdentity):
    """Identify one immutable Workflow definition."""


@dataclass(frozen=True, slots=True)
class WorkflowNetInstanceIdentity(_LexicalIdentity):
    """Identify one Workflow CPN instance."""


@dataclass(frozen=True, slots=True)
class WorkflowTransitionIdentity(_LexicalIdentity):
    """Identify one transition in an immutable Workflow definition."""


@dataclass(frozen=True, slots=True)
class WorkflowMarkingIdentity(_LexicalIdentity):
    """Identify one exact predecessor marking."""


@dataclass(frozen=True, slots=True)
class WorkflowOccurrenceIdentity(_LexicalIdentity):
    """Identify one logical occurrence of one selected binding."""


@dataclass(frozen=True, slots=True)
class WorkflowAttemptIdentity(_LexicalIdentity):
    """Identify one attempt under a logical occurrence."""


@dataclass(frozen=True, slots=True)
class WorkflowFiringRequestIdentity(_ContentIdentity):
    """Identify one exact SDK firing request."""


@dataclass(frozen=True, slots=True)
class WorkflowFiringResultIdentity(_ContentIdentity):
    """Identify one exact SDK firing result."""


@dataclass(frozen=True, slots=True)
class WorkflowIntegrationIdentity(_LexicalIdentity):
    """Identify one owner integration contract."""


@dataclass(frozen=True, slots=True)
class WorkflowIntegrationManifestIdentity(_ContentIdentity):
    """Identify one exact integration manifest."""


@dataclass(frozen=True, slots=True)
class WorkflowPayloadOwnerIdentity(_LexicalIdentity):
    """Reference the owner of one encoded payload contract."""


@dataclass(frozen=True, slots=True)
class WorkflowPayloadTypeIdentity(_LexicalIdentity):
    """Reference one owner-defined payload type."""


@dataclass(frozen=True, slots=True)
class WorkflowPayloadSchemaIdentity(_LexicalIdentity):
    """Reference one owner-defined payload schema."""


@dataclass(frozen=True, slots=True)
class WorkflowPayloadCodecIdentity(_LexicalIdentity):
    """Reference one owner-defined canonical payload codec."""


@dataclass(frozen=True, slots=True)
class WorkflowPayloadRepresentationIdentity(_LexicalIdentity):
    """Reference one owner-defined payload representation."""


__all__ = [
    "WorkflowAttemptIdentity",
    "WorkflowDefinitionIdentity",
    "WorkflowFirerIdentity",
    "WorkflowFirerImplementationIdentity",
    "WorkflowFiringRequestIdentity",
    "WorkflowFiringResultIdentity",
    "WorkflowIntegrationIdentity",
    "WorkflowIntegrationManifestIdentity",
    "WorkflowMarkingIdentity",
    "WorkflowNetInstanceIdentity",
    "WorkflowOccurrenceIdentity",
    "WorkflowPayloadCodecIdentity",
    "WorkflowPayloadOwnerIdentity",
    "WorkflowPayloadRepresentationIdentity",
    "WorkflowPayloadSchemaIdentity",
    "WorkflowPayloadTypeIdentity",
    "WorkflowTransitionBindingIdentity",
    "WorkflowTransitionIdentity",
]
