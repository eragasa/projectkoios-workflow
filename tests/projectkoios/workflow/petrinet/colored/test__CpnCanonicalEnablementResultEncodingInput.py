from _canonical_enablement_fixtures import enablement_context
from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResultEncodingInput,
)


def test_constructor__retains_result() -> None:
    definition, marking, source = enablement_context()
    value = CpnCanonicalEnablementResultEncodingInput(
        source, definition, marking
    )
    assert value.result == source
    assert value.definition == definition
    assert value.marking == marking
