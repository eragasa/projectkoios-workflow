from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBindingCodec,
)


def test_identity__names_exact_binding_transport_semantics() -> None:
    assert CpnCanonicalBindingCodec().identity.value.endswith(":0.1")
