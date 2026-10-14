from dataclasses import replace

import pytest

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
)

from _plan_fixtures import execution_plan_closure, hierarchical_child_binding


def test_constructor__closes_exact_hierarchical_route_and_mappings() -> None:
    child = hierarchical_child_binding()
    descriptors = tuple(
        sorted(
            (
                child.input_mapping.mapping_descriptor,
                child.terminal_mappings[
                    0
                ].parent_external_output_mapping_descriptor,
            ),
            key=lambda item: item.identity,
        )
    )
    plan = replace(
        execution_plan_closure(),
        transition_routes=(child.transition_route,),
        child_bindings=(child,),
        owner_mapping_descriptors=descriptors,
    )
    assert plan.child_bindings == (child,)


def test_constructor__rejects_nominal_canonical_definition_mismatch() -> None:
    with pytest.raises(ValueError, match="encode the nominal"):
        replace(
            execution_plan_closure(),
            nominal_definition_identity=CpnDefinitionIdentity("other"),
        )


def test_constructor__rejects_unbound_hierarchical_route() -> None:
    child = hierarchical_child_binding()
    with pytest.raises(ValueError, match="exactly one child binding"):
        replace(
            execution_plan_closure(),
            transition_routes=(child.transition_route,),
        )


def test_constructor__rejects_unreferenced_mapping_descriptor() -> None:
    child = hierarchical_child_binding()
    with pytest.raises(ValueError, match="exactly equal"):
        replace(
            execution_plan_closure(),
            owner_mapping_descriptors=(child.input_mapping.mapping_descriptor,),
        )
