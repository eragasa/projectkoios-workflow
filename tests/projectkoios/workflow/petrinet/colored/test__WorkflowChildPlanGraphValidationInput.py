import pytest

from _child_plan_graph_fixtures import child_reference, plan_identity
from projectkoios.workflow.petrinet.colored.deployments.linking.graph import (
    WorkflowChildPlanGraphValidationInput,
)


def test_constructor__requires_identity_ordered_references() -> None:
    first = child_reference("a", "b")
    second = child_reference("a", "c")
    ordered = tuple(sorted((first, second), key=lambda item: item.identity))
    with pytest.raises(ValueError, match="identity-ordered"):
        WorkflowChildPlanGraphValidationInput(
            plan_identity("a"), tuple(reversed(ordered))
        )
