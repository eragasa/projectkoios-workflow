from _selection_fixtures import selection_definition
from _firing_fixtures import predecessor
from projectkoios.workflow.petrinet.colored.enablement import (
    CpnTransitionEnablementRequest,
)


def test_constructor__retains_complete_enablement_request() -> None:
    definition = selection_definition()
    marking = predecessor(definition)
    request = CpnTransitionEnablementRequest(definition, marking)
    assert request.definition == definition
    assert request.marking == marking
