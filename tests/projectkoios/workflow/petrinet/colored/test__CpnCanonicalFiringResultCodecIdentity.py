from projectkoios.workflow.petrinet.colored.canonical.firing_results.codec import (
    CpnCanonicalFiringResultCodec,
)


def test_identity__names_exact_firing_replay_transport() -> None:
    assert CpnCanonicalFiringResultCodec().identity.value.endswith(":0.1")
