"""Identity-closed canonical shadow firing and correlation."""

import json
from dataclasses import replace
from hashlib import sha256
from typing import final

from ..canonical.definitions import (
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionDecodingInput,
    CpnCanonicalDefinitionEncodingInput,
)
from ..canonical.markings import (
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingDecodingInput,
    CpnCanonicalMarkingEncodingInput,
)
from ..profiles.defaults import (
    WorkflowCpnExecutionProfileResolutionRequest,
    WorkflowCpnExecutionProfileResolver,
)
from .contracts import (
    _SHADOW_RESULT_DOMAIN,
    CpnShadowFirerIdentity,
    CpnShadowFiringError,
    CpnShadowFiringErrorCode,
    CpnShadowFiringInput,
    CpnShadowFiringResult,
    CpnShadowFiringResultIdentity,
)


@final
class CpnShadowFirer:
    """Validate canonical correlations and execute one pure generic firing."""

    __slots__ = ()

    @property
    def identity(self) -> CpnShadowFirerIdentity:
        """Return exact shadow-firing semantics identity."""
        return CpnShadowFirerIdentity()

    def execute(
        self, firing_input: CpnShadowFiringInput
    ) -> CpnShadowFiringResult:
        """Fire only after exact definition and predecessor-byte correlation."""
        if type(firing_input) is not CpnShadowFiringInput:
            raise CpnShadowFiringError(
                CpnShadowFiringErrorCode.INVALID_ARGUMENT,
                (),
                "input must be CpnShadowFiringInput",
            )
        profile_resolution = WorkflowCpnExecutionProfileResolver().execute(
            WorkflowCpnExecutionProfileResolutionRequest(
                firing_input.execution_profile
            )
        )
        if not profile_resolution.is_available:
            unavailable = ",".join(
                item.component_name for item in profile_resolution.issues
            )
            raise CpnShadowFiringError(
                CpnShadowFiringErrorCode.EXECUTION_PROFILE_UNAVAILABLE,
                ("execution_profile",),
                "unavailable retained profile components: " + unavailable,
            )
        execution_profile_identity = profile_resolution.profile_identity
        decoded_definition = (
            CpnCanonicalDefinitionCodec()
            .decode(
                CpnCanonicalDefinitionDecodingInput(
                    firing_input.canonical_definition
                )
            )
            .definition
        )
        if decoded_definition != firing_input.firing_input.definition:
            raise CpnShadowFiringError(
                CpnShadowFiringErrorCode.DEFINITION_MISMATCH,
                ("canonical_definition",),
                "decoded canonical definition differs from the firing definition",
            )
        reencoded_definition = CpnCanonicalDefinitionCodec().encode(
            CpnCanonicalDefinitionEncodingInput(decoded_definition)
        )
        if reencoded_definition != firing_input.canonical_definition:
            raise CpnShadowFiringError(
                CpnShadowFiringErrorCode.DEFINITION_MISMATCH,
                ("canonical_definition",),
                "canonical definition does not replay byte-for-byte",
            )
        predecessor_decoding = CpnCanonicalMarkingCodec().decode(
            CpnCanonicalMarkingDecodingInput(
                firing_input.canonical_predecessor_marking,
                decoded_definition,
            )
        )
        predecessor = predecessor_decoding.document
        if (
            predecessor_decoding.marking
            != firing_input.firing_input.predecessor_marking
        ):
            raise CpnShadowFiringError(
                CpnShadowFiringErrorCode.PREDECESSOR_MARKING_MISMATCH,
                ("canonical_predecessor_marking",),
                "canonical predecessor differs from the firing predecessor",
            )
        canonical_firing_input = replace(
            firing_input.firing_input,
            definition=decoded_definition,
            predecessor_marking=predecessor_decoding.marking,
        )
        assert profile_resolution.transition_firer is not None
        result = profile_resolution.transition_firer.execute(
            canonical_firing_input
        )
        successor = (
            None
            if result.successor_marking is None
            else CpnCanonicalMarkingCodec().encode(
                CpnCanonicalMarkingEncodingInput(result.successor_marking)
            )
        )
        state = {
            "canonical_definition_identity": reencoded_definition.identity.value,
            "canonical_definition_sha256": reencoded_definition.sha256,
            "execution_profile_identity": execution_profile_identity.value,
            "firing_result_identity": result.identity.value,
            "firer_identity": self.identity.value,
            "outcome": result.outcome.value,
            "predecessor_marking_identity": predecessor.identity.value,
            "predecessor_marking_sha256": predecessor.sha256,
            "successor_marking_identity": (
                None if successor is None else successor.identity.value
            ),
            "successor_marking_sha256": None
            if successor is None
            else successor.sha256,
        }
        digest = sha256(
            json.dumps(
                state,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return CpnShadowFiringResult(
            CpnShadowFiringResultIdentity(_SHADOW_RESULT_DOMAIN + digest),
            reencoded_definition.identity,
            reencoded_definition.sha256,
            execution_profile_identity,
            predecessor.identity,
            predecessor.sha256,
            result.identity,
            None if successor is None else successor.identity,
            None if successor is None else successor.sha256,
            result,
        )
