from dataclasses import replace

import pytest

from _plan_fixtures import value_mapping_descriptor


def test_constructor__derives_identity_from_complete_mapping() -> None:
    source = value_mapping_descriptor()
    assert source.identity != replace(source, maximum_input_bytes=2048).identity


def test_constructor__rejects_noncanonical_correlations() -> None:
    with pytest.raises(ValueError, match="unique and lexical"):
        replace(
            value_mapping_descriptor(),
            correlation_descriptor_identities=("z", "a"),
        )
