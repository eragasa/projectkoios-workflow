from __future__ import annotations

import pytest
from projectkoios.workflow.worker import WorkflowWorkerIntegrationValidator
from projectkoios.workflow_sdk import WORKFLOW_SDK_VERSION
from projectkoios.workflow_sdk.firing import (
    Firer,
    WorkflowFirerDescriptor,
    WorkflowFiringBounds,
    WorkflowFiringRequest,
    WorkflowFiringResult,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowFirerIdentity,
    WorkflowFirerImplementationIdentity,
    WorkflowIntegrationIdentity,
    WorkflowIntegrationManifestIdentity,
)
from projectkoios.workflow_sdk.integration import (
    WorkflowIntegrationManifest,
    WorkflowWorkerIntegration,
)


def _descriptor(identity: str = "fixture.firer") -> WorkflowFirerDescriptor:
    return WorkflowFirerDescriptor(
        identity=WorkflowFirerIdentity(identity),
        implementation_identity=WorkflowFirerImplementationIdentity(
            f"{identity}:1"
        ),
        input_contracts=(),
        output_contracts=(),
        evidence_contracts=(),
        bounds=WorkflowFiringBounds(
            maximum_input_count=0,
            maximum_output_count=0,
            maximum_evidence_count=0,
            maximum_input_bytes=0,
            maximum_output_bytes=0,
            maximum_total_bytes=0,
            maximum_reason_count=0,
        ),
    )


def _manifest(
    descriptor: WorkflowFirerDescriptor,
    *,
    distribution_sha256: str = "a" * 64,
) -> WorkflowIntegrationManifest:
    return WorkflowIntegrationManifest(
        integration_identity=WorkflowIntegrationIdentity("fixture.integration"),
        package_name="fixture-integration",
        package_version="1.0.0",
        distribution_sha256=distribution_sha256,
        sdk_contract_version=WORKFLOW_SDK_VERSION,
        firer_descriptors=(descriptor,),
    )


class _Firer(Firer):
    def __init__(self, descriptor: WorkflowFirerDescriptor) -> None:
        self._descriptor = descriptor

    @property
    def descriptor(self) -> WorkflowFirerDescriptor:
        return self._descriptor

    def _fire(self, *, request: WorkflowFiringRequest) -> WorkflowFiringResult:
        raise AssertionError("admission must not invoke the integration")


class _Integration(WorkflowWorkerIntegration):
    def __init__(
        self,
        manifest_identity: WorkflowIntegrationManifestIdentity,
        firers: tuple[Firer, ...],
    ) -> None:
        self._manifest_identity = manifest_identity
        self._firers = firers

    @property
    def manifest_identity(self) -> WorkflowIntegrationManifestIdentity:
        return self._manifest_identity

    def firers(self) -> tuple[Firer, ...]:
        return self._firers


def test_validator_admits_the_exact_manifest_firer_set() -> None:
    descriptor = _descriptor()
    manifest = _manifest(descriptor)
    firer = _Firer(descriptor)
    integration = _Integration(manifest.identity, (firer,))

    admitted = WorkflowWorkerIntegrationValidator().execute(
        manifest=manifest,
        integration=integration,
    )

    assert admitted == (firer,)


def test_validator_rejects_manifest_identity_and_descriptor_mismatch() -> None:
    descriptor = _descriptor()
    manifest = _manifest(descriptor)
    other_manifest = _manifest(descriptor, distribution_sha256="b" * 64)

    with pytest.raises(ValueError, match="manifest identity differs"):
        WorkflowWorkerIntegrationValidator().execute(
            manifest=manifest,
            integration=_Integration(
                other_manifest.identity,
                (_Firer(descriptor),),
            ),
        )

    with pytest.raises(ValueError, match="exactly match"):
        WorkflowWorkerIntegrationValidator().execute(
            manifest=manifest,
            integration=_Integration(
                manifest.identity,
                (_Firer(_descriptor("fixture.other")),),
            ),
        )


def test_validator_rejects_duplicate_or_non_firer_live_objects() -> None:
    descriptor = _descriptor()
    manifest = _manifest(descriptor)
    firer = _Firer(descriptor)

    with pytest.raises(ValueError, match="identities must be unique"):
        WorkflowWorkerIntegrationValidator().execute(
            manifest=manifest,
            integration=_Integration(manifest.identity, (firer, firer)),
        )

    class _InvalidIntegration(WorkflowWorkerIntegration):
        @property
        def manifest_identity(self) -> WorkflowIntegrationManifestIdentity:
            return manifest.identity

        def firers(self) -> tuple[Firer, ...]:
            return (object(),)  # type: ignore[return-value]

    with pytest.raises(TypeError, match="concrete Firer"):
        WorkflowWorkerIntegrationValidator().execute(
            manifest=manifest,
            integration=_InvalidIntegration(),
        )


def test_validator_is_non_subclassable() -> None:
    with pytest.raises(TypeError, match="does not support subclasses"):

        class _InvalidValidator(WorkflowWorkerIntegrationValidator):
            pass
