from _canonical_selection_fixtures import selection_result
from projectkoios.workflow.petrinet.colored.canonical.selections import (
    CpnCanonicalSelectionResultDecodingResult,
)


def test_constructor__retains_result() -> None:
    source = selection_result()
    assert CpnCanonicalSelectionResultDecodingResult(source).result == source
