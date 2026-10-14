from _canonical_directive_fixtures import canonical_directive


def test_constructor__derives_exact_byte_correlations() -> None:
    source = canonical_directive()
    assert source.identity.value.endswith(source.sha256)
    assert source.representation_profile_identity.endswith("0.1.0")
