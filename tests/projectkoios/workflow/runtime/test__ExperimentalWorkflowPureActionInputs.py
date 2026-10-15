"""Verification of pure-action input admission and authority."""

from dataclasses import replace

import pytest
from _pure_action_fixtures import (
    _admitted,
    _authorized,
    _bindings,
    _coordinates,
    _evidence,
    _FixtureSourceRepository,
    _input,
    _input_bindings,
    _payload_for_contract,
    _reference,
    _service,
    _source,
    _two_input_bindings,
)
from projectkoios.workflow.actions import (
    ExperimentalWorkflowInputSourceProfileIdentity,
    ExperimentalWorkflowPureActionInputMappingDescriptor,
)
from projectkoios.workflow.runtime import (
    ExperimentalWorkflowPureActionAdmittedInputsIdentity,
    ExperimentalWorkflowPureActionAuthorizedInputs,
    ExperimentalWorkflowPureActionAuthorizedInputsIdentity,
    ExperimentalWorkflowPureActionInputAdmissionFactory,
    ExperimentalWorkflowPureActionInputAuthorizationService,
    ExperimentalWorkflowPureActionInputAuthorizationStatus,
    ExperimentalWorkflowPureActionInputSourceEvidence,
    ExperimentalWorkflowPureActionInputSourceLoadStatus,
    ExperimentalWorkflowPureActionInputSourceReference,
    ExperimentalWorkflowPureActionReserveStatus,
)
from projectkoios.workflow_sdk.identities import (
    WorkflowPayloadCodecIdentity,
)


def test_authorization_loads_owner_source_and_reservation_revalidates_it() -> (
    None
):
    source = _source(payload=b'{"retained":true}')
    source_repository = _FixtureSourceRepository((source,))
    authorization = ExperimentalWorkflowPureActionInputAuthorizationService(
        source_repository
    ).execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(source),),
    )

    assert authorization.status is (
        ExperimentalWorkflowPureActionInputAuthorizationStatus.AUTHORIZED
    )
    assert authorization.authorized_inputs is not None
    assert (
        authorization.authorized_inputs.admitted_inputs.request.inputs[0]
        == source.payload
    )
    reservation_service, _ = _service(source)
    reserved = reservation_service.reserve(
        authorized_inputs=authorization.authorized_inputs
    )
    assert reserved.status is (
        ExperimentalWorkflowPureActionReserveStatus.RESERVED
    )
    assert reserved.reservation is not None
    assert reserved.reservation.input_authorization_identity == (
        authorization.authorized_inputs.identity
    )


def test_authorization_fails_closed_for_absent_or_changed_reference() -> None:
    service = ExperimentalWorkflowPureActionInputAuthorizationService(
        _FixtureSourceRepository(())
    )
    absent = service.execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(),),
    )

    assert absent.status is (
        ExperimentalWorkflowPureActionInputAuthorizationStatus.ABSENT
    )
    assert absent.authorized_inputs is None
    with pytest.raises(ValueError, match="kind differs from mapping"):
        service.execute(
            input_bindings=_input_bindings(),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_references=(
                ExperimentalWorkflowPureActionInputSourceReference(
                    source_kind="caller-supplied-payload",
                    source_profile_identity=(
                        ExperimentalWorkflowInputSourceProfileIdentity(
                            "fixture.retained-payload:1"
                        )
                    ),
                    source_identity="fixture.source-evidence",
                ),
            ),
        )


@pytest.mark.parametrize(
    ("source_status", "authorization_status"),
    (
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.INCOMPATIBLE,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INCOMPATIBLE,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.CORRUPT,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.CORRUPT,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.INDETERMINATE,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.INDETERMINATE,
        ),
        (
            ExperimentalWorkflowPureActionInputSourceLoadStatus.ERROR,
            ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR,
        ),
    ),
)
def test_authorization_preserves_owner_source_failure_status(
    source_status: ExperimentalWorkflowPureActionInputSourceLoadStatus,
    authorization_status: (
        ExperimentalWorkflowPureActionInputAuthorizationStatus
    ),
) -> None:
    repository = _FixtureSourceRepository(
        (),
        failure_status=source_status,
    )
    authorization = ExperimentalWorkflowPureActionInputAuthorizationService(
        repository
    ).execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(),),
    )

    assert authorization.status is authorization_status
    assert authorization.authorized_inputs is None


def test_authorization_contains_source_repository_exception() -> None:
    authorization = ExperimentalWorkflowPureActionInputAuthorizationService(
        _FixtureSourceRepository((), raise_error=True)
    ).execute(
        input_bindings=_input_bindings(),
        selected_binding_evidence=_evidence(),
        coordinates=_coordinates(),
        source_references=(_reference(),),
    )

    assert authorization.status is (
        ExperimentalWorkflowPureActionInputAuthorizationStatus.ERROR
    )
    assert authorization.authorized_inputs is None
    assert authorization.diagnostics == ("source_repository_error",)


def test_reservation_contains_source_repository_exception() -> None:
    source = _source()
    authorized = _authorized(_admitted(source=source))
    service, _ = _service(
        source,
        source_repository=_FixtureSourceRepository((), raise_error=True),
    )

    result = service.reserve(authorized_inputs=authorized)

    assert (
        result.status
        is ExperimentalWorkflowPureActionReserveStatus.SOURCE_ERROR
    )
    assert result.reservation is None
    assert result.request is None


def test_input_mapping_tokens_are_bounded() -> None:
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowInputSourceProfileIdentity("x" * 513)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowPureActionInputMappingDescriptor(
            input_role="projection_request",
            source_kind="x" * 513,
            source_profile_identity=(
                ExperimentalWorkflowInputSourceProfileIdentity(
                    "fixture.retained-payload:1"
                )
            ),
            mapping_version="fixture.input-mapping:1",
        )

    forged_profile = ExperimentalWorkflowInputSourceProfileIdentity(
        "fixture.retained-payload:1"
    )
    object.__setattr__(forged_profile, "value", "x" * 513)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        ExperimentalWorkflowPureActionInputMappingDescriptor(
            input_role="projection_request",
            source_kind="retained-inline-payload",
            source_profile_identity=forged_profile,
            mapping_version="fixture.input-mapping:1",
        )


def test_input_plan_and_bindings_content_identify_mapping_semantics() -> None:
    execution_bindings = _bindings()
    first = _input_bindings(bindings=execution_bindings)
    replay = _input_bindings(bindings=execution_bindings)
    changed = _input_bindings(
        bindings=execution_bindings,
        mapping_version="fixture.input-mapping:2",
    )

    assert first == replay
    assert first.identity == replay.identity
    assert first.identity != changed.identity
    assert first.input_plan.identity != changed.input_plan.identity
    assert first.execution_bindings == execution_bindings


def test_admission_binds_source_evidence_and_invocation_coordinates() -> None:
    first = _admitted(source=_source(source_identity="fixture.source-a"))
    changed_source = _admitted(
        source=_source(source_identity="fixture.source-b")
    )
    changed_attempt = _admitted(
        coordinates=_coordinates(attempt="fixture.other-attempt"),
        source=_source(source_identity="fixture.source-a"),
    )

    assert first.request == changed_source.request
    assert first.identity != changed_source.identity
    assert first.request.identity != changed_attempt.request.identity
    assert first.identity != changed_attempt.identity


def test_admission_rejects_source_mapping_and_contract_substitution() -> None:
    with pytest.raises(ValueError, match="kind differs from mapping"):
        _admitted(source=_source(source_kind="caller-supplied-payload"))
    with pytest.raises(ValueError, match="profile differs from mapping"):
        _admitted(source=_source(source_profile="fixture.other-profile:1"))
    with pytest.raises(ValueError, match="exactly satisfy retained contracts"):
        ExperimentalWorkflowPureActionInputAdmissionFactory().execute(
            input_bindings=_input_bindings(),
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=(),
        )

    changed_codec = replace(
        _input(),
        codec_identity=WorkflowPayloadCodecIdentity("fixture.other-codec:1"),
    )
    source = ExperimentalWorkflowPureActionInputSourceEvidence(
        source_kind="retained-inline-payload",
        source_profile_identity=ExperimentalWorkflowInputSourceProfileIdentity(
            "fixture.retained-payload:1"
        ),
        source_identity="fixture.source-evidence",
        payload=changed_codec,
    )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        _admitted(source=source)


def test_admission_rejects_missing_duplicate_and_reordered_inputs() -> None:
    bindings = _two_input_bindings()
    output_mapping = (
        bindings.input_plan.execution_plan.output_mapping_descriptor
    )
    contracts = output_mapping.firer_descriptor.input_contracts
    sources = tuple(
        ExperimentalWorkflowPureActionInputSourceEvidence(
            source_kind="retained-inline-payload",
            source_profile_identity=(
                ExperimentalWorkflowInputSourceProfileIdentity(
                    "fixture.retained-payload:1"
                )
            ),
            source_identity=f"fixture.source-{index}",
            payload=_payload_for_contract(contract),
        )
        for index, contract in enumerate(contracts)
    )
    factory = ExperimentalWorkflowPureActionInputAdmissionFactory()

    with pytest.raises(ValueError, match="exactly satisfy retained contracts"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=sources[:1],
        )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=(sources[0], sources[0]),
        )
    with pytest.raises(ValueError, match="metadata differs from contract"):
        factory.execute(
            input_bindings=bindings,
            selected_binding_evidence=_evidence(),
            coordinates=_coordinates(),
            source_evidence=tuple(reversed(sources)),
        )


def test_admission_rejects_machine_paths_and_direct_identity_forgery() -> None:
    with pytest.raises(ValueError, match="machine path"):
        _source(source_identity="/private/tmp/payload.json")

    admitted = _admitted()
    object.__setattr__(
        admitted,
        "identity",
        ExperimentalWorkflowPureActionAdmittedInputsIdentity("0" * 64),
    )
    with pytest.raises(ValueError, match="admitted inputs differ"):
        _authorized(admitted)

    authorized = _authorized()
    forged_authority = replace(
        authorized.source_authorities[0],
        reference_identity=_reference(
            _source(source_identity="fixture.other-source")
        ).identity,
    )
    with pytest.raises(ValueError, match="differs from admitted source"):
        ExperimentalWorkflowPureActionAuthorizedInputs(
            admitted_inputs=authorized.admitted_inputs,
            source_authorities=(forged_authority,),
        )

    object.__setattr__(
        authorized,
        "identity",
        ExperimentalWorkflowPureActionAuthorizedInputsIdentity("0" * 64),
    )
    reservation_service, _ = _service()
    with pytest.raises(ValueError, match="authorized inputs differ"):
        reservation_service.reserve(authorized_inputs=authorized)
