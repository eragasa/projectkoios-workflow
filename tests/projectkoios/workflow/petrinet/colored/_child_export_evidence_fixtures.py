"""Private typed child-export and conformance-evidence fixtures."""

from dataclasses import replace
from hashlib import sha256

from _plan_fixtures import execution_plan_closure
from _selection_fixtures import selection_enablement

from projectkoios.workflow.petrinet.colored.children.exports.canonical import (
    WorkflowChildDefinitionExportInput,
    WorkflowChildDefinitionExporter,
)
from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExport,
    WorkflowChildDefinitionExportClosure,
)
from projectkoios.workflow.petrinet.colored.children.exports.evidence import (
    WorkflowChildExportConformanceEvidenceReference,
    WorkflowChildExportEvidenceBinding,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildCancellationCapability,
    WorkflowCompanionProductionPhase,
    WorkflowChildInterface,
    WorkflowChildPortDefinition,
    WorkflowChildPortDirection,
    WorkflowChildPortTrafficKind,
    WorkflowTerminalCompanionEvidenceRequirement,
    WorkflowTerminalDeliveryRequirement,
)
from projectkoios.workflow.petrinet.colored.plans.definition import (
    WorkflowExecutionPlan,
    WorkflowExecutionPlanCompilationInput,
    WorkflowExecutionPlanCompiler,
)


def child_interface() -> WorkflowChildInterface:
    """Return one exact initial-input/success-terminal child interface."""
    definition, _ = selection_enablement(values=(1,))
    input_port = WorkflowChildPortDefinition(
        "child-input-port",
        WorkflowChildPortDirection.INPUT,
        definition.places[0].identity.value,
        definition.colors[0].identity.value,
        None,
        None,
        "integer",
        1,
        1,
        ("run-correlation",),
        WorkflowChildPortTrafficKind.INITIAL,
        1,
    )
    terminal_port = WorkflowChildPortDefinition(
        "terminal-port",
        WorkflowChildPortDirection.OUTPUT,
        definition.places[0].identity.value,
        definition.colors[0].identity.value,
        "primary-schema",
        "primary-codec",
        None,
        1,
        1,
        ("run-correlation",),
        WorkflowChildPortTrafficKind.TERMINAL,
        1,
    )
    companion = WorkflowTerminalCompanionEvidenceRequirement(
        0,
        "synthetic-companion-reference",
        "synthetic-owner",
        "synthetic-companion-schema",
        "synthetic-companion-codec",
        "application/vnd.projectkoios.synthetic-companion+json",
        4096,
        1,
        1,
        WorkflowCompanionProductionPhase.POST_TERMINAL_PRE_DELIVERY_RETAINED,
        "synthetic-companion-correlation",
        1,
    )
    delivery = WorkflowTerminalDeliveryRequirement(
        "success",
        terminal_port.identity,
        "primary-schema",
        "primary-codec",
        (companion,),
        1,
        "primary-then-companions",
        "terminal-correlation",
        "parent-output-mapper",
        1,
    )
    return WorkflowChildInterface(
        input_ports=(input_port,),
        terminal_output_ports=(terminal_port,),
        admitted_terminal_classification_identities=("success",),
        terminal_delivery_requirements=(delivery,),
        cancellation_capability=WorkflowChildCancellationCapability(
            "no-in-net-cancellation",
            False,
            (),
            (),
            "propagate-none",
            1,
        ),
        reconciliation_capability_identity="runtime-reconciliation",
        execution_protocol_requirement_identity="protocol:1",
        protected_effect_capability_identities=("synthetic-calculation",),
        contract_version=1,
    )


def child_execution_plan() -> WorkflowExecutionPlan:
    """Return the exact child plan retained by deployment linking."""
    interface = child_interface()
    return WorkflowExecutionPlanCompiler().execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                execution_plan_closure(),
                child_interface=interface,
                terminal_delivery_requirements=(
                    interface.terminal_delivery_requirements
                ),
            )
        )
    )


def child_export() -> WorkflowChildDefinitionExport:
    """Return one content-identified child export with an exact plan."""
    interface = child_interface()
    plan = child_execution_plan()
    closure = plan.closure
    export_closure = WorkflowChildDefinitionExportClosure(
        owner_identity="child-owner",
        workflow_family_identity="synthetic-child",
        source_definition_identity="synthetic-child-source",
        source_definition_contract_version=1,
        execution_plan_identity=plan.identity,
        execution_plan_sha256=plan.identity.value.rsplit(":", 1)[-1],
        nominal_definition_identity=closure.nominal_definition_identity.value,
        canonical_definition_identity=(
            closure.canonical_definition_identity.value
        ),
        canonical_definition_representation_profile_identity=(
            closure.canonical_definition_representation_profile_identity
        ),
        canonical_definition_sha256=closure.canonical_definition_sha256,
        cpn_execution_profile_identity=closure.cpn_execution_profile_identity,
        initial_marking_constructor_identity=(
            closure.initial_marking_contract_identity
        ),
        interface=interface,
        compiler_implementation_identity=closure.compiler_identity,
        compiler_version_identity=closure.compiler_version,
        exporter_implementation_identity="synthetic-child-exporter",
        exporter_version_identity="1",
        source_revision_identity="synthetic-revision",
        contract_version=1,
    )
    return WorkflowChildDefinitionExporter().execute(
        WorkflowChildDefinitionExportInput(export_closure)
    )


def evidence_reference(
    *, role_identity: str = "definition-parity"
) -> WorkflowChildExportConformanceEvidenceReference:
    """Return one exact canonical conformance-evidence reference."""
    payload = b"synthetic canonical parity evidence"
    return WorkflowChildExportConformanceEvidenceReference(
        role_identity,
        "artifact:synthetic-parity",
        "projectkoios.workflow.child-export-evidence-json:0.1",
        "application/vnd.projectkoios.child-export-evidence+json",
        sha256(payload).hexdigest(),
        1,
    )


def child_export_evidence_binding() -> WorkflowChildExportEvidenceBinding:
    """Return one typed binding from the child export to canonical evidence."""
    return WorkflowChildExportEvidenceBinding(
        child_export(), (evidence_reference(),), 1
    )
