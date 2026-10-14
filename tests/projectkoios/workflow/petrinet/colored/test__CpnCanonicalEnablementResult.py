from _canonical_enablement_fixtures import canonical_enablement_result


def test_constructor__derives_exact_byte_correlations() -> None:
    source = canonical_enablement_result()
    assert source.identity.value.endswith(source.sha256)
    assert source.representation_profile_identity.endswith("0.1.0")
