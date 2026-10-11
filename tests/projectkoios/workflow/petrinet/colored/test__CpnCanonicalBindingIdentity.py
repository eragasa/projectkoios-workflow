from _canonical_binding_fixtures import canonical_binding


def test_identity__is_content_derived() -> None:
    source = canonical_binding()
    assert source.identity.value == (
        "projectkoios.workflow.cpn-binding:0.1:" + source.sha256
    )
