from dataclasses import replace

from _child_plan_graph_fixtures import child_reference, plan_identity


def test_constructor__derives_identity_from_parent_and_child() -> None:
    source = child_reference("a", "b")
    assert (
        source.identity
        != replace(
            source, child_execution_plan_identity=plan_identity("c")
        ).identity
    )
