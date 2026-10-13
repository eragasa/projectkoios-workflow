from _canonical_firing_result_fixtures import (
    canonical_firing_result,
    execution_profile,
)
from projectkoios.workflow.petrinet.colored.canonical.firing_results.documents import (
    CpnCanonicalFiringResultDecodingInput,
)


def test_constructor__retains_document() -> None:
    source = canonical_firing_result()
    value = CpnCanonicalFiringResultDecodingInput(source, execution_profile())
    assert value.canonical_result == source
    assert value.execution_profile == execution_profile()
