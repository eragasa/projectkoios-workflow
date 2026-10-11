"""Nominal tests for ``CpnShadowFiringErrorCode``."""

from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringErrorCode,
)


def test_members__are_closed() -> None:
    assert CpnShadowFiringErrorCode.RETAINED_RESULT_MISMATCH.value == (
        "retained_result_mismatch"
    )
