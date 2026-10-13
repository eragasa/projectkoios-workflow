import pytest
from _payload_reference_fixtures import payload_reference

from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)
from projectkoios.workflow.petrinet.colored.payloads.references.canonical import (
    WorkflowCanonicalDomainPayloadReference,
    WorkflowDomainPayloadReferenceCodec,
    WorkflowDomainPayloadReferenceDecodingInput,
    WorkflowDomainPayloadReferenceEncodingInput,
)
from projectkoios.workflow.petrinet.colored.payloads.references.definition import (
    WorkflowDomainPayloadReferenceIdentity,
)


def test_codec__round_trip_and_substitutions__are_exact() -> None:
    reference = payload_reference()
    document = WorkflowDomainPayloadReferenceCodec().encode(
        WorkflowDomainPayloadReferenceEncodingInput(reference)
    )
    decoded = WorkflowDomainPayloadReferenceCodec().decode(
        WorkflowDomainPayloadReferenceDecodingInput(
            document, reference.identity
        )
    )
    assert decoded.reference == reference
    forged = WorkflowDomainPayloadReferenceIdentity(
        "projectkoios.workflow.payload-reference:1:" + "0" * 64
    )
    with pytest.raises(CpnCanonicalCodecError) as captured:
        WorkflowDomainPayloadReferenceCodec().decode(
            WorkflowDomainPayloadReferenceDecodingInput(document, forged)
        )
    assert captured.value.code is CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH
    noncanonical = WorkflowCanonicalDomainPayloadReference(
        document.canonical_bytes + b" "
    )
    with pytest.raises(CpnCanonicalCodecError) as changed:
        WorkflowDomainPayloadReferenceCodec().decode(
            WorkflowDomainPayloadReferenceDecodingInput(
                noncanonical, noncanonical.identity
            )
        )
    assert changed.value.code is CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES

    duplicate = WorkflowCanonicalDomainPayloadReference(
        b'{"artifact_identity":"artifact:1","artifact_identity":"artifact:2",'
        b'"byte_size":1,"media_type":"application/json",'
        b'"payload_identity":"payload","schema_identity":"schema:1",'
        b'"sha256":"' + b"0" * 64 + b'"}'
    )
    with pytest.raises(CpnCanonicalCodecError) as duplicated:
        WorkflowDomainPayloadReferenceCodec().decode(
            WorkflowDomainPayloadReferenceDecodingInput(
                duplicate,
                duplicate.identity,
            )
        )
    assert duplicated.value.code is CpnCanonicalCodecErrorCode.DUPLICATE_KEY

    boolean_size = WorkflowCanonicalDomainPayloadReference(
        document.canonical_bytes.replace(
            b'"byte_size":19',
            b'"byte_size":true',
        )
    )
    with pytest.raises(CpnCanonicalCodecError) as invalid_type:
        WorkflowDomainPayloadReferenceCodec().decode(
            WorkflowDomainPayloadReferenceDecodingInput(
                boolean_size,
                boolean_size.identity,
            )
        )
    assert invalid_type.value.code is CpnCanonicalCodecErrorCode.INVALID_SHAPE
