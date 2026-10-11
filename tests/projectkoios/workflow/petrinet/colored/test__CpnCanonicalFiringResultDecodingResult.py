from _canonical_firing_result_fixtures import firing_result
from projectkoios.workflow.petrinet.colored.canonical.firings import (
    CpnCanonicalFiringResultDecodingResult,
)


def test_constructor__retains_result() -> None:
    source = firing_result()
    assert CpnCanonicalFiringResultDecodingResult(source).result == source
