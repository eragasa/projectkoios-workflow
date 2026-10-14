from _selection_fixtures import selection_enablement
from projectkoios.workflow.petrinet.colored.selection import (
    CpnBindingSelectionRequest,
)


def test_constructor__retains_complete_selection_request() -> None:
    definition, enablement = selection_enablement(values=(1,))
    request = CpnBindingSelectionRequest(definition, enablement)
    assert request.definition == definition
    assert request.enablement == enablement
    assert request.directive is None
