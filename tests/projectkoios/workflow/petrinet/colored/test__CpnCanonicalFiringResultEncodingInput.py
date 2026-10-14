from _canonical_firing_result_fixtures import execution_profile, firing_result
from projectkoios.workflow.petrinet.colored.canonical.firing.results.documents import (
    CpnCanonicalFiringResultEncodingInput,
)


def test_constructor__retains_result() -> None:
    source = firing_result()
    value = CpnCanonicalFiringResultEncodingInput(source, execution_profile())
    assert value.result == source
    assert value.execution_profile == execution_profile()
