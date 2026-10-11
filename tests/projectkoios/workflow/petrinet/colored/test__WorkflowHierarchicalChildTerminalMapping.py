from dataclasses import replace

from _plan_fixtures import hierarchical_child_binding, value_mapping_descriptor


def test_constructor__derives_identity_from_output_mapping() -> None:
    source = hierarchical_child_binding().terminal_mappings[0]
    changed = replace(
        source,
        parent_external_output_mapping_descriptor=value_mapping_descriptor(
            adapter_identity="different-output"
        ),
    )
    assert source.identity != changed.identity
