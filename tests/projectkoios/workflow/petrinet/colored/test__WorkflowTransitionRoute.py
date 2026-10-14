from dataclasses import replace

import pytest

from _plan_fixtures import execution_plan_closure, value_mapping_descriptor
from projectkoios.workflow.petrinet.colored.routes.transitions import (
    WorkflowTransitionRouteKind,
)


def test_constructor__derives_identity_from_route_semantics() -> None:
    source = execution_plan_closure().transition_routes[0]
    assert source.identity != replace(source, contract_version=2).identity


def test_constructor__rejects_mapping_on_pure_route() -> None:
    source = execution_plan_closure().transition_routes[0]
    with pytest.raises(ValueError, match="pure CPN routes"):
        replace(source, mapping_descriptors=(value_mapping_descriptor(),))


def test_constructor__requires_capability_for_protected_effect() -> None:
    source = execution_plan_closure().transition_routes[0]
    with pytest.raises(ValueError, match="require mappings"):
        replace(
            source,
            kind=WorkflowTransitionRouteKind.PROTECTED_EFFECT,
            mapping_descriptors=(value_mapping_descriptor(),),
        )
