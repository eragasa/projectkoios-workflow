from _canonical_selection_fixtures import canonical_selection_result
from projectkoios.workflow.petrinet.colored.canonical.selections import (
    CpnCanonicalSelectionResultDecodingInput,
)


def test_constructor__retains_document_and_schemas() -> None:
    source = canonical_selection_result()
    value = CpnCanonicalSelectionResultDecodingInput(source)
    assert value.canonical_result == source
    assert value.control_record_types == ()
