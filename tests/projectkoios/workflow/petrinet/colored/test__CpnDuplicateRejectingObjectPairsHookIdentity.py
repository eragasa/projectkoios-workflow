from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnDuplicateRejectingObjectPairsHookIdentity,
)


def test_candidate_direct_module_contract__is_declared() -> None:
    assert (
        CpnDuplicateRejectingObjectPairsHookIdentity.__name__
        == "CpnDuplicateRejectingObjectPairsHookIdentity"
    )
