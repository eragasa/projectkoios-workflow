from _canonical_directive_fixtures import canonical_directive


def test_identity__is_content_derived() -> None:
    source = canonical_directive()
    assert source.identity.value == (
        "projectkoios.workflow.cpn-selection-directive:0.1:" + source.sha256
    )
