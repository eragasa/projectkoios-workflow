"""Nominal tests for ``CpnShadowFiringError``."""

from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringError,
    CpnShadowFiringErrorCode,
)


def test_constructor__retains_closed_diagnostic() -> None:
    error = CpnShadowFiringError(
        CpnShadowFiringErrorCode.DEFINITION_MISMATCH, ("definition",), "differs"
    )
    assert error.path == ("definition",)
