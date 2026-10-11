from dataclasses import replace

import pytest

from _plan_fixtures import hierarchical_child_binding


def test_constructor__derives_identity_from_complete_child_binding() -> None:
    source = hierarchical_child_binding()
    assert (
        source.identity != replace(source, quiescence_required=False).identity
    )


def test_constructor__requires_v0_1_single_child() -> None:
    with pytest.raises(ValueError, match="cardinality 1"):
        replace(hierarchical_child_binding(), child_instance_cardinality=2)


def test_constructor__requires_v0_1_ordinal_zero() -> None:
    with pytest.raises(ValueError, match="ordinal 0"):
        replace(hierarchical_child_binding(), child_ordinal=1)
