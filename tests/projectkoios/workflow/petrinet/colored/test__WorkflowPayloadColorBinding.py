"""Direct tests for content-identified payload-color bindings."""

from dataclasses import replace

import pytest

from projectkoios.workflow.petrinet.colored.definitions import (
    CpnDefinitionIdentity,
)
from projectkoios.workflow.petrinet.colored.payloads.bindings import (
    WorkflowPayloadColorBinding,
)
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnValueKind,
)


def binding() -> WorkflowPayloadColorBinding:
    return WorkflowPayloadColorBinding(
        CpnDefinitionIdentity("definition"),
        CpnColorIdentity("payload-reference"),
        CpnValueKind.STRING,
        "owner",
        "schema",
        "codec",
        "application/json",
        4096,
        8,
        True,
        1,
    )


def test_identity__changes_for_every_bounded_payload_policy_mutation() -> None:
    base = binding()
    assert replace(base, maximum_payload_bytes=4097).identity != base.identity
    assert (
        replace(base, maximum_reference_tokens_per_complete_marking=9).identity
        != base.identity
    )
    assert replace(base, codec_identity="other-codec").identity != base.identity


def test_constructor__requires_string_reference_values() -> None:
    with pytest.raises(ValueError, match="STRING"):
        replace(binding(), allowed_value_kind=CpnValueKind.INTEGER)
