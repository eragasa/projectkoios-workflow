from _canonical_directive_fixtures import canonical_directive
from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirectiveDecodingInput,
)


def test_constructor__retains_document_and_schemas() -> None:
    source = canonical_directive()
    value = CpnCanonicalSelectionDirectiveDecodingInput(source)
    assert value.canonical_directive == source
    assert value.control_record_types == ()
