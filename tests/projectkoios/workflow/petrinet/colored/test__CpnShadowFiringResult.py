"""Correlation tests for ``CpnShadowFiringResult``."""

from test__CpnShadowFirer import shadow_input

from projectkoios.workflow.petrinet.colored.shadow.firing import CpnShadowFirer


def test_constructor__result_carries_exact_predecessor_correlation() -> None:
    source = shadow_input()
    result = CpnShadowFirer().execute(source)
    assert (
        result.predecessor_marking_identity
        == source.canonical_predecessor_marking.identity
    )
    assert (
        result.canonical_definition_identity
        == source.canonical_definition.identity
    )
