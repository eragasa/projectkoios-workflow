from _selection_fixtures import selection_enablement
from projectkoios.workflow.petrinet.colored.enablement.ordering import (
    CpnEnabledBindingOrderingInput,
    CpnEnabledBindingOrderingPolicy,
)


def test_execute__reproduces_complete_enablement_order() -> None:
    definition, enablement = selection_enablement(values=(2, 1))
    assert enablement.enabled_bindings is not None
    result = CpnEnabledBindingOrderingPolicy().execute(
        CpnEnabledBindingOrderingInput(
            definition, frozenset(reversed(enablement.enabled_bindings))
        )
    )
    assert result.bindings == enablement.enabled_bindings
    assert CpnEnabledBindingOrderingPolicy().identity.value.endswith("v1")
