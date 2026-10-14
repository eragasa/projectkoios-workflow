from _validation_fixtures import valid_definition
from projectkoios.workflow.petrinet.colored.markings import (
    CpnMarking,
    CpnMarkingIdentity,
)
from projectkoios.workflow.petrinet.colored.validation.markings import (
    CpnMarkingValidationInput,
)


def test_constructor__retains_definition_and_marking() -> None:
    definition = valid_definition()
    marking = CpnMarking(CpnMarkingIdentity("marking"), definition.identity, ())
    value = CpnMarkingValidationInput(definition, marking)
    assert value.definition == definition
    assert value.marking == marking
