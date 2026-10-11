from dataclasses import replace

import pytest
from _child_export_evidence_fixtures import child_interface

from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowTerminalDeliveryRequirement,
)


def test_constructor__enforces_collection_and_signed_64_bit_bounds() -> None:
    source = child_interface().terminal_delivery_requirements[0]
    companion = source.companion_requirements[0]
    excessive = tuple(
        replace(
            companion,
            ordinal=index,
            evidence_role_identity=f"synthetic-role-{index}",
        )
        for index in range(65)
    )
    with pytest.raises(ValueError, match="at most 64"):
        replace(
            source,
            companion_requirements=excessive,
            maximum_total_companion_reference_count=65,
        )
    with pytest.raises(TypeError, match="nonnegative"):
        replace(
            source,
            companion_requirements=(),
            maximum_total_companion_reference_count=9_223_372_036_854_775_808,
        )


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowTerminalDeliveryRequirement.__name__
        == "WorkflowTerminalDeliveryRequirement"
    )
