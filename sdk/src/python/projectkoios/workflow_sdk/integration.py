"""Immutable integration manifests and worker-loaded nominal boundaries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from . import WORKFLOW_SDK_VERSION
from ._validation import (
    MAX_CONTRACTS,
    MAX_TEXT_BYTES,
    semantic_sha256,
    validate_ascii_text,
    validate_sdk_version,
    validate_sha256,
)
from .firing import Firer, WorkflowFirerDescriptor, descriptor_state
from .identities import (
    WorkflowIntegrationIdentity,
    WorkflowIntegrationManifestIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowIntegrationManifest:
    """Advertise one exact installed integration without live objects."""

    identity: WorkflowIntegrationManifestIdentity = field(init=False)
    integration_identity: WorkflowIntegrationIdentity
    package_name: str
    package_version: str
    distribution_sha256: str
    sdk_contract_version: str
    firer_descriptors: tuple[WorkflowFirerDescriptor, ...]

    def __post_init__(self) -> None:
        if type(self.integration_identity) is not WorkflowIntegrationIdentity:
            raise TypeError("integration_identity must be WorkflowIntegrationIdentity")
        validate_ascii_text(self.package_name, "package_name", MAX_TEXT_BYTES)
        validate_ascii_text(self.package_version, "package_version", MAX_TEXT_BYTES)
        validate_sha256(self.distribution_sha256, "distribution_sha256")
        validate_sdk_version(self.sdk_contract_version, WORKFLOW_SDK_VERSION)
        if type(self.firer_descriptors) is not tuple:
            raise TypeError("firer_descriptors must be a tuple")
        if len(self.firer_descriptors) > MAX_CONTRACTS:
            raise ValueError(f"firer_descriptors exceeds {MAX_CONTRACTS} entries")
        if any(
            type(value) is not WorkflowFirerDescriptor
            for value in self.firer_descriptors
        ):
            raise TypeError("firer_descriptors must contain WorkflowFirerDescriptor")
        identities = tuple(value.identity.value for value in self.firer_descriptors)
        if len(identities) != len(set(identities)):
            raise ValueError("firer descriptor identities must be unique")
        if identities != tuple(sorted(identities)):
            raise ValueError("firer descriptors must be sorted by firer identity")
        object.__setattr__(
            self,
            "identity",
            WorkflowIntegrationManifestIdentity(
                semantic_sha256(
                    "workflow-sdk-integration-manifest:1",
                    manifest_state(self),
                )
            ),
        )


class WorkflowIntegrationManifestProvider(ABC):
    """Nominal side-effect-free source of one immutable integration manifest."""

    __slots__ = ()

    @abstractmethod
    def manifest(self) -> WorkflowIntegrationManifest:
        """Return the exact immutable integration manifest."""


class WorkflowWorkerIntegration(ABC):
    """Nominal composition root for firers loaded in an isolated worker."""

    __slots__ = ()

    @property
    @abstractmethod
    def manifest_identity(self) -> WorkflowIntegrationManifestIdentity:
        """Return the exact manifest implemented by this worker integration."""

    @abstractmethod
    def firers(self) -> tuple[Firer, ...]:
        """Return the exact firers advertised by the retained manifest."""


def manifest_state(value: WorkflowIntegrationManifest) -> list[object]:
    """Return manifest semantic state excluding its derived identity."""
    return [
        value.integration_identity.value,
        value.package_name,
        value.package_version,
        value.distribution_sha256,
        value.sdk_contract_version,
        [descriptor_state(item) for item in value.firer_descriptors],
    ]


__all__ = [
    "WorkflowIntegrationManifest",
    "WorkflowIntegrationManifestProvider",
    "WorkflowWorkerIntegration",
]
