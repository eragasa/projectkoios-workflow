"""Direct tests for public enablement-result identity derivation."""

from _firing_fixtures import predecessor
from _validation_fixtures import valid_definition

from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnablementResultIdentityDerivationInput,
    CpnEnablementResultIdentityDeriver,
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)


def test_execute__replays_exact_success_identity() -> None:
    definition = valid_definition()
    marking = predecessor(definition)
    result = CpnTransitionEnabler().execute(
        CpnTransitionEnablementRequest(definition, marking)
    )
    assert result.enabled_bindings is not None
    derived = CpnEnablementResultIdentityDeriver().execute(
        CpnEnablementResultIdentityDerivationInput(
            definition,
            marking,
            result.expression_evaluator_identity,
            result.ordering_policy_identity,
            result.transition_enabler_identity,
            result.enabled_bindings,
            None,
        )
    )
    assert derived == result.identity
