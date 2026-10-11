from _canonical_directive_fixtures import directive
from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirectiveEncodingInput,
)


def test_constructor__retains_directive() -> None:
    source = directive()
    assert (
        CpnCanonicalSelectionDirectiveEncodingInput(source).directive == source
    )
