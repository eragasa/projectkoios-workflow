from dataclasses import replace

import pytest
from _child_export_evidence_fixtures import child_execution_plan, child_export

from projectkoios.workflow.petrinet.colored.canonical.definitions import (
    CpnCanonicalDefinitionIdentity,
)
from projectkoios.workflow.petrinet.colored.children.exports.canonical.identity import (
    WorkflowChildDefinitionExportIdentityDerivationInput,
    WorkflowChildDefinitionExportIdentityDeriver,
)
from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExport,
)
from projectkoios.workflow.petrinet.colored.deployments.linking.correlation import (
    WorkflowChildPlanExportCorrelationRequest,
    WorkflowChildPlanExportCorrelator,
)
from projectkoios.workflow.petrinet.colored.plans.identities import (
    WorkflowExecutionPlanIdentity,
)
from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentity,
)


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    (
        ("nominal_definition_identity", "other-definition"),
        (
            "canonical_definition_identity",
            CpnCanonicalDefinitionIdentity(
                "projectkoios.workflow.cpn-definition:0.1:" + "0" * 64
            ).value,
        ),
        (
            "canonical_definition_representation_profile_identity",
            "other-representation",
        ),
        ("canonical_definition_sha256", "0" * 64),
        (
            "cpn_execution_profile_identity",
            WorkflowCpnExecutionProfileIdentity(
                "projectkoios.workflow.cpn-execution-profile:0.1:" + "0" * 64
            ),
        ),
        ("initial_marking_constructor_identity", "other-marking-constructor"),
        ("compiler_implementation_identity", "other-compiler"),
        ("compiler_version_identity", "other-compiler-version"),
    ),
)
def test_execute__reports_each_substituted_export_field(
    field_name: str, changed_value: object
) -> None:
    source = child_export()
    changed_closure = replace(source.closure, **{field_name: changed_value})
    changed_export = WorkflowChildDefinitionExport(
        changed_closure,
        WorkflowChildDefinitionExportIdentityDeriver().execute(
            WorkflowChildDefinitionExportIdentityDerivationInput(
                changed_closure
            )
        ),
    )
    result = WorkflowChildPlanExportCorrelator().execute(
        WorkflowChildPlanExportCorrelationRequest(
            child_execution_plan(), changed_export
        )
    )
    assert field_name in result.mismatched_field_names


def test_execute__reports_paired_execution_identity_and_digest_substitution() -> (
    None
):
    source = child_export()
    changed_closure = replace(
        source.closure,
        execution_plan_identity=WorkflowExecutionPlanIdentity(
            "projectkoios.workflow.execution-plan:0.1:" + "0" * 64
        ),
        execution_plan_sha256="0" * 64,
    )
    changed_export = WorkflowChildDefinitionExport(
        changed_closure,
        WorkflowChildDefinitionExportIdentityDeriver().execute(
            WorkflowChildDefinitionExportIdentityDerivationInput(
                changed_closure
            )
        ),
    )
    result = WorkflowChildPlanExportCorrelator().execute(
        WorkflowChildPlanExportCorrelationRequest(
            child_execution_plan(), changed_export
        )
    )
    assert result.mismatched_field_names == (
        "execution_plan_identity",
        "execution_plan_sha256",
    )


def test_execute__reports_interface_substitution() -> None:
    source = child_export()
    changed_closure = replace(
        source.closure,
        interface=replace(source.closure.interface, contract_version=2),
    )
    changed_export = WorkflowChildDefinitionExport(
        changed_closure,
        WorkflowChildDefinitionExportIdentityDeriver().execute(
            WorkflowChildDefinitionExportIdentityDerivationInput(
                changed_closure
            )
        ),
    )
    result = WorkflowChildPlanExportCorrelator().execute(
        WorkflowChildPlanExportCorrelationRequest(
            child_execution_plan(), changed_export
        )
    )
    assert result.mismatched_field_names == ("interface",)
