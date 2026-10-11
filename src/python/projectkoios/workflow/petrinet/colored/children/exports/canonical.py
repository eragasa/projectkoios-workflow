"""Canonical content identity derivation for child-definition exports."""

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import final

from .definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportClosure,
    WorkflowChildDefinitionExportIdentity,
)


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportIdentityDeriverIdentity:
    """Identity of exact child-export identity derivation semantics."""

    value: str = "projectkoios.workflow.cpn.child-export-identity-deriver:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportIdentityDerivationInput:
    """One exact child-export closure to identify."""

    closure: WorkflowChildDefinitionExportClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowChildDefinitionExportClosure:
            raise TypeError(
                "closure must be WorkflowChildDefinitionExportClosure"
            )


@final
class WorkflowChildDefinitionExportIdentityDeriver:
    """Directly derive child-export identity from all semantic fields."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowChildDefinitionExportIdentityDeriverIdentity:
        """Return exact derivation semantics identity."""
        return WorkflowChildDefinitionExportIdentityDeriverIdentity()

    def execute(
        self,
        derivation_input: WorkflowChildDefinitionExportIdentityDerivationInput,
    ) -> WorkflowChildDefinitionExportIdentity:
        """Hash every child-export closure field without future evidence."""
        if type(derivation_input) is not (
            WorkflowChildDefinitionExportIdentityDerivationInput
        ):
            raise TypeError(
                "derivation_input must be "
                "WorkflowChildDefinitionExportIdentityDerivationInput"
            )
        closure = derivation_input.closure
        input_ports = [
            {
                "color_identity": item.color_identity,
                "contract_version": str(item.contract_version),
                "correlation_descriptor_identities": list(
                    item.correlation_descriptor_identities
                ),
                "direction": item.direction.value,
                "identity": item.identity,
                "maximum_token_count": str(item.maximum_token_count),
                "minimum_token_count": str(item.minimum_token_count),
                "payload_codec_identity": item.payload_codec_identity,
                "payload_schema_identity": item.payload_schema_identity,
                "place_identity": item.place_identity,
                "scalar_value_kind": item.scalar_value_kind,
                "traffic_kind": item.traffic_kind.value,
            }
            for item in closure.interface.input_ports
        ]
        terminal_ports = [
            {
                "color_identity": item.color_identity,
                "contract_version": str(item.contract_version),
                "correlation_descriptor_identities": list(
                    item.correlation_descriptor_identities
                ),
                "direction": item.direction.value,
                "identity": item.identity,
                "maximum_token_count": str(item.maximum_token_count),
                "minimum_token_count": str(item.minimum_token_count),
                "payload_codec_identity": item.payload_codec_identity,
                "payload_schema_identity": item.payload_schema_identity,
                "place_identity": item.place_identity,
                "scalar_value_kind": item.scalar_value_kind,
                "traffic_kind": item.traffic_kind.value,
            }
            for item in closure.interface.terminal_output_ports
        ]
        delivery_requirements = [
            {
                "companion_requirements": [
                    {
                        "codec_identity": companion.codec_identity,
                        "contract_version": str(companion.contract_version),
                        "correlation_predicate_descriptor_identity": (
                            companion.correlation_predicate_descriptor_identity
                        ),
                        "evidence_role_identity": companion.evidence_role_identity,
                        "identity": companion.identity,
                        "maximum_payload_bytes": str(
                            companion.maximum_payload_bytes
                        ),
                        "maximum_reference_count": str(
                            companion.maximum_reference_count
                        ),
                        "media_type_identity": companion.media_type_identity,
                        "minimum_reference_count": str(
                            companion.minimum_reference_count
                        ),
                        "ordinal": str(companion.ordinal),
                        "owner_identity": companion.owner_identity,
                        "payload_schema_identity": (
                            companion.payload_schema_identity
                        ),
                        "production_phase": companion.production_phase.value,
                    }
                    for companion in item.companion_requirements
                ],
                "contract_version": str(item.contract_version),
                "correlation_validation_descriptor_identity": (
                    item.correlation_validation_descriptor_identity
                ),
                "identity": item.identity,
                "mapper_input_ordering_profile_identity": (
                    item.mapper_input_ordering_profile_identity
                ),
                "maximum_total_companion_reference_count": str(
                    item.maximum_total_companion_reference_count
                ),
                "output_mapper_descriptor_identity": (
                    item.output_mapper_descriptor_identity
                ),
                "primary_payload_codec_identity": (
                    item.primary_payload_codec_identity
                ),
                "primary_payload_schema_identity": (
                    item.primary_payload_schema_identity
                ),
                "primary_terminal_port_identity": (
                    item.primary_terminal_port_identity
                ),
                "terminal_classification_identity": (
                    item.terminal_classification_identity
                ),
            }
            for item in closure.interface.terminal_delivery_requirements
        ]
        cancellation = closure.interface.cancellation_capability
        state = {
            "admitted_terminal_classification_identities": list(
                closure.interface.admitted_terminal_classification_identities
            ),
            "cancellation_capability": {
                "cancellation_port_identities": list(
                    cancellation.cancellation_port_identities
                ),
                "cancellation_terminal_classification_identities": list(
                    cancellation.cancellation_terminal_classification_identities
                ),
                "contract_version": str(cancellation.contract_version),
                "identity": cancellation.identity,
                "in_net_cancellation_supported": (
                    cancellation.in_net_cancellation_supported
                ),
                "propagation_policy_identity": (
                    cancellation.propagation_policy_identity
                ),
            },
            "canonical_definition_identity": closure.canonical_definition_identity,
            "canonical_definition_representation_profile_identity": (
                closure.canonical_definition_representation_profile_identity
            ),
            "canonical_definition_sha256": closure.canonical_definition_sha256,
            "child_interface_identity": closure.interface.identity,
            "compiler_implementation_identity": (
                closure.compiler_implementation_identity
            ),
            "compiler_version_identity": closure.compiler_version_identity,
            "contract_version": str(closure.contract_version),
            "cpn_execution_profile_identity": (
                closure.cpn_execution_profile_identity.value
            ),
            "execution_plan_identity": closure.execution_plan_identity.value,
            "execution_plan_sha256": closure.execution_plan_sha256,
            "exporter_implementation_identity": (
                closure.exporter_implementation_identity
            ),
            "exporter_version_identity": closure.exporter_version_identity,
            "initial_marking_constructor_identity": (
                closure.initial_marking_constructor_identity
            ),
            "input_ports": input_ports,
            "nominal_definition_identity": closure.nominal_definition_identity,
            "owner_identity": closure.owner_identity,
            "protected_effect_capability_identities": list(
                closure.interface.protected_effect_capability_identities
            ),
            "reconciliation_capability_identity": (
                closure.interface.reconciliation_capability_identity
            ),
            "source_definition_contract_version": str(
                closure.source_definition_contract_version
            ),
            "source_definition_identity": closure.source_definition_identity,
            "source_revision_identity": closure.source_revision_identity,
            "terminal_delivery_requirements": delivery_requirements,
            "terminal_output_ports": terminal_ports,
            "workflow_family_identity": closure.workflow_family_identity,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return WorkflowChildDefinitionExportIdentity(
            "projectkoios.workflow.child-definition-export:0.1:"
            + sha256(encoded).hexdigest()
        )


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExporterIdentity:
    """Identity of exact immutable child-export assembly semantics."""

    value: str = "projectkoios.workflow.cpn.child-definition-exporter:0.1"


@dataclass(frozen=True, slots=True)
class WorkflowChildDefinitionExportInput:
    """Complete semantic closure to assemble as one child export."""

    closure: WorkflowChildDefinitionExportClosure

    def __post_init__(self) -> None:
        if type(self.closure) is not WorkflowChildDefinitionExportClosure:
            raise TypeError(
                "closure must be WorkflowChildDefinitionExportClosure"
            )


@final
class WorkflowChildDefinitionExporter:
    """Directly assemble a child export with no post-hoc evidence cycle."""

    __slots__ = ()

    @property
    def identity(self) -> WorkflowChildDefinitionExporterIdentity:
        """Return exact exporter semantics identity."""
        return WorkflowChildDefinitionExporterIdentity()

    def execute(
        self, export_input: WorkflowChildDefinitionExportInput
    ) -> WorkflowChildDefinitionExport:
        """Derive and bind the exact content identity to one immutable closure."""
        if type(export_input) is not WorkflowChildDefinitionExportInput:
            raise TypeError(
                "export_input must be WorkflowChildDefinitionExportInput"
            )
        identity = WorkflowChildDefinitionExportIdentityDeriver().execute(
            WorkflowChildDefinitionExportIdentityDerivationInput(
                export_input.closure
            )
        )
        return WorkflowChildDefinitionExport(export_input.closure, identity)
