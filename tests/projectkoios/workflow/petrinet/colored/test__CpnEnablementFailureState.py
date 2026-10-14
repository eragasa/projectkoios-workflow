"""Nominal tests for ``CpnEnablementFailureState``."""

from projectkoios.workflow.petrinet.colored.enablement.results.definition import (
    CpnEnablementFailureCode,
)
from projectkoios.workflow.petrinet.colored.enablement.results.identity import (
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
