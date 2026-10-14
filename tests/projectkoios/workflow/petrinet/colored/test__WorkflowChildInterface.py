"""Direct tests for complete content-identified child interfaces."""

from dataclasses import replace

from test__WorkflowChildDefinitionExport import closure


def test_identity__changes_for_port_and_terminal_requirement_mutations() -> (
    None
):
    interface = closure().interface
    port = interface.terminal_output_ports[0]
    changed_port = replace(port, correlation_descriptor_identities=("other",))
    changed = replace(interface, terminal_output_ports=(changed_port,))
    assert changed.identity != interface.identity
