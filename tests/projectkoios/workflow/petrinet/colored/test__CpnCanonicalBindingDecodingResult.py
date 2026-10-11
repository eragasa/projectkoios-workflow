from _canonical_binding_fixtures import binding
from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBindingDecodingResult,
)


def test_constructor__retains_binding() -> None:
    source = binding()
    assert CpnCanonicalBindingDecodingResult(source).binding == source
