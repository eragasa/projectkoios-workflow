from projectkoios.workflow.petrinet.colored.deployments.linking.graph import (
    WorkflowChildPlanGraphValidator,
)


def test_identity__names_exact_static_reference_semantics() -> None:
    assert WorkflowChildPlanGraphValidator().identity.value == (
        "projectkoios.workflow.child-plan-graph-validator:0.1"
    )
