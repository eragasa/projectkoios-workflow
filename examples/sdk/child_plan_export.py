"""Compile, export, correlate, and statically link one child plan."""

from dataclasses import replace

from _support import flat_plan_closure
from projectkoios.workflow.petrinet.colored.children.exports.canonical.exporting import (
    WorkflowChildDefinitionExporter,
    WorkflowChildDefinitionExportInput,
)
from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportClosure,
)
from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowChildCancellationCapability,
    WorkflowChildInterface,
)
from projectkoios.workflow.petrinet.colored.deployments.linking.correlation import (
    WorkflowChildPlanExportCorrelationRequest,
    WorkflowChildPlanExportCorrelator,
)
from projectkoios.workflow.petrinet.colored.deployments.linking.graph import (
    WorkflowChildPlanGraphValidationInput,
    WorkflowChildPlanGraphValidator,
    WorkflowChildPlanReference,
)
from projectkoios.workflow.petrinet.colored.plans.compilation import (
    WorkflowExecutionPlanCompilationInput,
    WorkflowExecutionPlanCompiler,
)


def main() -> None:
    """Keep the child plan separate while validating its parent reference."""
    interface = WorkflowChildInterface(
        input_ports=(),
        terminal_output_ports=(),
        admitted_terminal_classification_identities=(),
        terminal_delivery_requirements=(),
        cancellation_capability=WorkflowChildCancellationCapability(
            "example.no-cancellation",
            False,
            (),
            (),
            "example.propagate-none",
            1,
        ),
        reconciliation_capability_identity="example.reconciliation:1",
        execution_protocol_requirement_identity="example.protocol:1",
        protected_effect_capability_identities=(),
        contract_version=1,
    )
    compiler = WorkflowExecutionPlanCompiler()
    child_plan = compiler.execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                flat_plan_closure(),
                child_interface=interface,
                compiler_identity="example.child-plan-compiler",
            )
        )
    )
    child_closure = child_plan.closure
    exported = WorkflowChildDefinitionExporter().execute(
        WorkflowChildDefinitionExportInput(
            WorkflowChildDefinitionExportClosure(
                owner_identity="example.child-owner",
                workflow_family_identity="example.child-workflow",
                source_definition_identity="example.child-source",
                source_definition_contract_version=1,
                execution_plan_identity=child_plan.identity,
                execution_plan_sha256=child_plan.identity.value.rsplit(":", 1)[
                    -1
                ],
                nominal_definition_identity=(
                    child_closure.nominal_definition_identity.value
                ),
                canonical_definition_identity=(
                    child_closure.canonical_definition.identity.value
                ),
                canonical_definition_representation_profile_identity=(
                    child_closure.canonical_definition.representation_profile_identity
                ),
                canonical_definition_sha256=(
                    child_closure.canonical_definition.sha256
                ),
                cpn_execution_profile_identity=(
                    child_closure.cpn_execution_profile_identity
                ),
                initial_marking_constructor_identity=(
                    child_closure.initial_marking_contract_identity
                ),
                interface=interface,
                compiler_implementation_identity=(
                    child_closure.compiler_identity
                ),
                compiler_version_identity=child_closure.compiler_version,
                exporter_implementation_identity="example.child-exporter",
                exporter_version_identity="1",
                source_revision_identity="example.revision:1",
                contract_version=1,
            )
        )
    )
    correlation = WorkflowChildPlanExportCorrelator().execute(
        WorkflowChildPlanExportCorrelationRequest(child_plan, exported)
    )
    if not correlation.is_correlated:
        raise RuntimeError(f"export mismatches: {correlation!r}")

    root_plan = compiler.execute(
        WorkflowExecutionPlanCompilationInput(
            replace(
                flat_plan_closure(),
                compiler_identity="example.root-plan-compiler",
            )
        )
    )
    reference = WorkflowChildPlanReference(
        root_plan.identity,
        child_plan.identity,
        exported.identity,
        1,
    )
    graph = WorkflowChildPlanGraphValidator().execute(
        WorkflowChildPlanGraphValidationInput(
            root_plan.identity,
            (reference,),
        )
    )
    if not graph.is_valid:
        raise RuntimeError(f"child-plan graph findings: {graph.issues!r}")
    print(reference.identity)


if __name__ == "__main__":
    main()
