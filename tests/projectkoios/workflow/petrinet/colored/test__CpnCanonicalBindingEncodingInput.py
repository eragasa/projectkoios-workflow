from _canonical_binding_fixtures import binding
from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBindingEncodingInput,
)


def test_constructor__retains_binding() -> None:
    source = binding()
    assert CpnCanonicalBindingEncodingInput(source).binding == source
