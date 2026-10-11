from projectkoios.workflow.petrinet.colored.markings import (
    CpnTokenOrderingPolicyIdentity,
)


def test_public_contract__is_declared() -> None:
    assert (
        CpnTokenOrderingPolicyIdentity.__name__
        == "CpnTokenOrderingPolicyIdentity"
    )
