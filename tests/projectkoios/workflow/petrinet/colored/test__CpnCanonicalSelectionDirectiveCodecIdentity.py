from projectkoios.workflow.petrinet.colored.canonical.directives import (
    CpnCanonicalSelectionDirectiveCodec,
)


def test_identity__names_exact_directive_transport_semantics() -> None:
    assert CpnCanonicalSelectionDirectiveCodec().identity.value.endswith(":0.1")
