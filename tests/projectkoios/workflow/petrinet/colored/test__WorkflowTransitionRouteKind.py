from projectkoios.workflow.petrinet.colored.routes.transitions import (
    WorkflowTransitionRouteKind,
)


def test_enum__is_closed_to_declared_route_kinds() -> None:
    assert tuple(WorkflowTransitionRouteKind) == (
        WorkflowTransitionRouteKind.PURE_CPN,
        WorkflowTransitionRouteKind.OWNER_ADAPTER,
        WorkflowTransitionRouteKind.PROTECTED_EFFECT,
        WorkflowTransitionRouteKind.HIERARCHICAL_CHILD,
    )
