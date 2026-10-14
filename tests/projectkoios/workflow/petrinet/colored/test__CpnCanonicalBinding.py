from _canonical_binding_fixtures import canonical_binding


def test_constructor__derives_exact_byte_correlations() -> None:
    source = canonical_binding()
    assert source.identity.value.endswith(source.sha256)
    assert source.representation_profile_identity.endswith("0.1.0")
