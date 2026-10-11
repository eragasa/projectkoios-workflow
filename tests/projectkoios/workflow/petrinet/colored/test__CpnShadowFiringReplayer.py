"""Direct tests for exact retained shadow replay."""

from dataclasses import replace
from test__CpnShadowFirer import shadow_input

from projectkoios.workflow.petrinet.colored.profiles.definition import (
    WorkflowCpnExecutionProfileIdentity,
)
from projectkoios.workflow.petrinet.colored.shadow.contracts import (
    CpnShadowFiringErrorCode,
)
from projectkoios.workflow.petrinet.colored.shadow.firing import CpnShadowFirer
from projectkoios.workflow.petrinet.colored.shadow.replay import (
    CpnShadowFiringReplayer,
)
from projectkoios.workflow.petrinet.colored.shadow.replay_contracts import (
    CpnShadowFiringReplayInput,
)


def test_execute__reports_exact_match_and_one_field_mutation() -> None:
    source = shadow_input()
    retained = CpnShadowFirer().execute(source)
    matched = CpnShadowFiringReplayer().execute(
        CpnShadowFiringReplayInput(source, retained)
    )
    changed = replace(
        retained,
        execution_profile_identity=WorkflowCpnExecutionProfileIdentity(
            "projectkoios.workflow.cpn-execution-profile:0.1:" + "0" * 64
        ),
    )
    mismatch = CpnShadowFiringReplayer().execute(
        CpnShadowFiringReplayInput(source, changed)
    )
    assert matched.is_match
    assert not mismatch.is_match
    assert (
        mismatch.issue_code is CpnShadowFiringErrorCode.RETAINED_RESULT_MISMATCH
    )
