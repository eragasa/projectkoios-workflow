from _selection_fixtures import selection_enablement
from projectkoios.workflow.petrinet.colored.enablement.ordering import (
    CpnEnabledBindingOrderingResult,
)


def test_constructor__retains_unique_ordered_bindings() -> None:
    _, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    assert (
        CpnEnabledBindingOrderingResult(enablement.enabled_bindings).bindings
        == enablement.enabled_bindings
    )
