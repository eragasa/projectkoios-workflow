from _canonical_enablement_fixtures import enablement_result
from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResultDecodingResult,
)


def test_constructor__retains_result() -> None:
    source = enablement_result()
    assert CpnCanonicalEnablementResultDecodingResult(source).result == source
