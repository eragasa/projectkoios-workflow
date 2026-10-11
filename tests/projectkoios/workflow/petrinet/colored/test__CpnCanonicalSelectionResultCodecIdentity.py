from projectkoios.workflow.petrinet.colored.canonical.selections import (
    CpnCanonicalSelectionResultCodec,
)


def test_identity__names_exact_selection_transport_semantics() -> None:
    assert CpnCanonicalSelectionResultCodec().identity.value.endswith(":0.1")
