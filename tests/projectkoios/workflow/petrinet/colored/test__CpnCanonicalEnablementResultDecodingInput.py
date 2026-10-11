from _canonical_enablement_fixtures import canonical_enablement_result
from projectkoios.workflow.petrinet.colored.canonical.enablement import (
    CpnCanonicalEnablementResultDecodingInput,
)


def test_constructor__retains_document_and_schemas() -> None:
    source = canonical_enablement_result()
    value = CpnCanonicalEnablementResultDecodingInput(source)
    assert value.canonical_result == source
