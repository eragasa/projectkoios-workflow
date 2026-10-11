"""Private synthetic child-plan reference graph constructors."""

from projectkoios.workflow.petrinet.colored.children.exports.definition import (
    WorkflowChildDefinitionExportIdentity,
)
from projectkoios.workflow.petrinet.colored.deployments.linking import (
    WorkflowChildPlanGraphValidationInput,
    WorkflowChildPlanReference,
)
from projectkoios.workflow.petrinet.colored.plans.identities import (
    WorkflowExecutionPlanIdentity,
)


def plan_identity(character: str) -> WorkflowExecutionPlanIdentity:
    """Return one valid synthetic content identity."""
    return WorkflowExecutionPlanIdentity(
        "projectkoios.workflow.execution-plan:0.1:" + character * 64
    )


def child_reference(parent: str, child: str) -> WorkflowChildPlanReference:
    """Return one exact parent-to-child reference."""
    return WorkflowChildPlanReference(
        plan_identity(parent),
        plan_identity(child),
        WorkflowChildDefinitionExportIdentity(
            "projectkoios.workflow.child-definition-export:0.1:" + child * 64
        ),
        1,
    )


def validation_input(
    references: tuple[WorkflowChildPlanReference, ...],
) -> WorkflowChildPlanGraphValidationInput:
    """Return a graph rooted at synthetic plan ``a``."""
    return WorkflowChildPlanGraphValidationInput(
        plan_identity("a"),
        tuple(sorted(references, key=lambda item: item.identity)),
    )
