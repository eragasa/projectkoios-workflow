from _canonical_directive_fixtures import directive
from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirectiveDecodingResult,
)


def test_constructor__retains_directive() -> None:
    source = directive()
    assert (
        CpnCanonicalSelectionDirectiveDecodingResult(source).directive == source
    )
