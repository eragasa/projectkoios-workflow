from dataclasses import replace

import pytest
from _child_export_evidence_fixtures import child_interface

from projectkoios.workflow.petrinet.colored.children.interfaces import (
    WorkflowTerminalCompanionEvidenceRequirement,
)


def test_constructor__enforces_signed_64_bit_representation_bounds() -> None:
    source = (
        child_interface()
        .terminal_delivery_requirements[0]
        .companion_requirements[0]
    )
    maximum = 9_223_372_036_854_775_807
    assert (
        replace(source, maximum_payload_bytes=maximum).maximum_payload_bytes
        == maximum
    )
    with pytest.raises(TypeError, match="signed-64-bit"):
        replace(source, maximum_payload_bytes=maximum + 1)
    with pytest.raises(TypeError, match="signed-64-bit"):
        replace(source, maximum_reference_count=maximum + 1)
    with pytest.raises(TypeError, match="signed-64-bit"):
        replace(source, ordinal=maximum + 1)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        WorkflowTerminalCompanionEvidenceRequirement.__name__
        == "WorkflowTerminalCompanionEvidenceRequirement"
    )
