"""Admission of SDK worker integrations against retained manifests."""

from __future__ import annotations

from typing import final

from projectkoios.workflow_sdk.firing import Firer, WorkflowFirerDescriptor
from projectkoios.workflow_sdk.identities import (
    WorkflowIntegrationManifestIdentity,
)
from projectkoios.workflow_sdk.integration import (
    WorkflowIntegrationManifest,
    WorkflowWorkerIntegration,
)


@final
class WorkflowWorkerIntegrationValidator:
    """Validate one process-local integration as an exact manifest set."""

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Prevent subclasses from weakening worker admission."""
        raise TypeError(
            "WorkflowWorkerIntegrationValidator does not support subclasses"
        )

    def execute(
        self,
        *,
        manifest: WorkflowIntegrationManifest,
        integration: WorkflowWorkerIntegration,
    ) -> tuple[Firer, ...]:
        """Return the admitted live firers or fail closed on any mismatch."""
        if type(manifest) is not WorkflowIntegrationManifest:
            raise TypeError("manifest must be WorkflowIntegrationManifest")
        if not isinstance(integration, WorkflowWorkerIntegration):
            raise TypeError("integration must extend WorkflowWorkerIntegration")
        manifest_identity = integration.manifest_identity
        if type(manifest_identity) is not WorkflowIntegrationManifestIdentity:
            raise TypeError(
                "integration manifest_identity must be "
                "WorkflowIntegrationManifestIdentity"
            )
        if manifest_identity != manifest.identity:
            raise ValueError(
                "integration manifest identity differs from manifest"
            )

        firers = integration.firers()
        if type(firers) is not tuple:
            raise TypeError("integration firers must be a tuple")
        if any(not isinstance(firer, Firer) for firer in firers):
            raise TypeError(
                "integration firers must contain concrete Firer objects"
            )

        descriptors = tuple(firer.descriptor for firer in firers)
        if any(
            type(descriptor) is not WorkflowFirerDescriptor
            for descriptor in descriptors
        ):
            raise TypeError(
                "live firer descriptors must be WorkflowFirerDescriptor"
            )
        identities = tuple(descriptor.identity for descriptor in descriptors)
        if len(identities) != len(set(identities)):
            raise ValueError("live firer descriptor identities must be unique")
        if descriptors != manifest.firer_descriptors:
            raise ValueError(
                "live firers must exactly match retained manifest descriptors"
            )
        return firers


__all__ = ["WorkflowWorkerIntegrationValidator"]
