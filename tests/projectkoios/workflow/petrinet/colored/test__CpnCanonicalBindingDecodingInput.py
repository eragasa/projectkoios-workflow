from _canonical_binding_fixtures import canonical_binding
from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBindingDecodingInput,
)


def test_constructor__retains_document_and_schemas() -> None:
    source = canonical_binding()
    value = CpnCanonicalBindingDecodingInput(source)
    assert value.canonical_binding == source
    assert value.control_record_types == ()
