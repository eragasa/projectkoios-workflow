"""Nominal tests for ``CpnEnablementFailureState``."""

from projectkoios.workflow.petrinet.colored.enablement.outcomes import (
    CpnEnablementFailureCode,
)
from projectkoios.workflow.petrinet.colored.enablement.identity_derivation import (
    CpnEnablementFailureState,
)


def test_constructor__retains_closed_failure_state() -> None:
    state = CpnEnablementFailureState(
        CpnEnablementFailureCode.INVALID_MARKING,
        "validation",
        "valid marking",
        "invalid marking",
        "rejected",
    )
    assert state.code is CpnEnablementFailureCode.INVALID_MARKING
