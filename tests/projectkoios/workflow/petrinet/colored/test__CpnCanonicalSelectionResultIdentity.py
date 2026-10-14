from _canonical_selection_fixtures import canonical_selection_result


def test_identity__is_content_derived() -> None:
    source = canonical_selection_result()
    assert source.identity.value == (
        "projectkoios.workflow.cpn-selection-result:0.1:" + source.sha256
    )
