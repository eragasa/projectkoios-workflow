from _child_plan_graph_fixtures import child_reference, validation_input
from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanGraphValidationIssueCode,
    WorkflowChildPlanGraphValidator,
)


def test_execute__accepts_finite_acyclic_static_references() -> None:
    source = validation_input(
        (child_reference("a", "b"), child_reference("b", "c"))
    )
    assert WorkflowChildPlanGraphValidator().execute(source).is_valid


def test_execute__rejects_static_child_plan_cycle() -> None:
    source = validation_input(
        (child_reference("a", "b"), child_reference("b", "a"))
    )
    result = WorkflowChildPlanGraphValidator().execute(source)
    assert tuple(item.code for item in result.issues) == (
        WorkflowChildPlanGraphValidationIssueCode.CYCLE,
    )


def test_execute__does_not_inspect_cpn_transition_topology() -> None:
    source = validation_input(())
    assert WorkflowChildPlanGraphValidator().execute(source).is_valid
