from _selection_fixtures import selection_enablement
from projectkoios.workflow.petrinet.colored.enablement import (
    CpnEnabledBindingOrderingInput,
)


def test_constructor__retains_definition_and_unique_bindings() -> None:
    definition, enablement = selection_enablement()
    assert enablement.enabled_bindings is not None
    value = CpnEnabledBindingOrderingInput(
        definition, frozenset(enablement.enabled_bindings)
    )
    assert value.definition == definition
