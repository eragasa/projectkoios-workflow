from _canonical_firing_result_fixtures import canonical_firing_result


def test_identity__is_content_derived() -> None:
    source = canonical_firing_result()
    assert source.identity.value == (
        "projectkoios.workflow.cpn-firing-result:0.1:" + source.sha256
    )
