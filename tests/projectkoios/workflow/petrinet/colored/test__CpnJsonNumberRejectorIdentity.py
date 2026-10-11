from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnJsonNumberRejectorIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        CpnJsonNumberRejectorIdentity.__name__
        == "CpnJsonNumberRejectorIdentity"
    )
