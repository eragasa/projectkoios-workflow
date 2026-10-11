from dataclasses import replace

from _plan_fixtures import hierarchical_child_binding


def test_constructor__derives_identity_from_mapping_content() -> None:
    source = hierarchical_child_binding().input_mapping
    assert (
        source.identity
        != replace(source, child_input_port_identity="other").identity
    )
