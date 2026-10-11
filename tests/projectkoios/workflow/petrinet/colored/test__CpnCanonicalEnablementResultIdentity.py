from _canonical_enablement_fixtures import canonical_enablement_result


def test_identity__is_content_derived() -> None:
    source = canonical_enablement_result()
    assert source.identity.value == (
        "projectkoios.workflow.cpn-enablement-result:0.1:" + source.sha256
    )
