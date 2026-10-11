from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResultCodec,
)


def test_identity__names_exact_enablement_transport_semantics() -> None:
    assert CpnCanonicalEnablementResultCodec().identity.value.endswith(":0.1")
