"""Canonical replay transport for complete pure CPN firing results."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from ..definitions import CpnTransitionIdentity
from ..firing.inputs import (
    CpnFiringInput,
)
from ..firing.outcomes import (
    CpnFiringOutcomeKind,
    CpnFiringResult,
    CpnFiringResultIdentity,
)
from ..selection import CpnSelectionDirectiveIdentity
from ..profiles.defaults import (
    WorkflowCpnExecutionProfileResolutionRequest,
    WorkflowCpnExecutionProfileResolver,
)
from ..profiles.definition import (
    WorkflowCpnExecutionProfile,
    WorkflowCpnExecutionProfileIdentityDerivationInput,
    WorkflowCpnExecutionProfileIdentityDeriver,
)
from .bindings import (
    CpnCanonicalBinding,
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingDecodingInput,
    CpnCanonicalBindingEncodingInput,
)
from .definitions import (
    CpnCanonicalDefinition,
    CpnCanonicalDefinitionCodec,
    CpnCanonicalDefinitionDecodingInput,
    CpnCanonicalDefinitionEncodingInput,
)
from .enablement import (
    CpnCanonicalEnablementResult,
    CpnCanonicalEnablementResultCodec,
    CpnCanonicalEnablementResultDecodingInput,
    CpnCanonicalEnablementResultEncodingInput,
)
from .firing_contracts import CpnCanonicalFiringResultCodecIdentity
from .json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)
from .markings import (
    CpnCanonicalMarking,
    CpnCanonicalMarkingCodec,
    CpnCanonicalMarkingDecodingInput,
    CpnCanonicalMarkingEncodingInput,
)
from .selections import (
    CpnCanonicalSelectionResult,
    CpnCanonicalSelectionResultCodec,
    CpnCanonicalSelectionResultDecodingInput,
    CpnCanonicalSelectionResultEncodingInput,
)

_FIRING_PROFILE = "projectkoios.workflow.cpn-firing-result-json:0.1.0"
_MAXIMUM_FIRING_BYTES = 67_108_864


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultIdentity:
    """Content-derived identity of exact canonical firing-result bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-firing-result:0.1:"
        if not self.value.startswith(prefix):
            raise ValueError("identity has the wrong domain")
        digest = self.value.removeprefix(prefix)
        if not (
            len(digest) == 64
            and digest == digest.lower()
            and all(item in hexdigits for item in digest)
        ):
            raise ValueError("identity must end in lowercase SHA-256")


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResult:
    """Exact firing-result bytes and constructor-derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalFiringResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_FIRING_BYTES:
            raise ValueError("canonical firing result exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _FIRING_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalFiringResultIdentity(
                "projectkoios.workflow.cpn-firing-result:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultEncodingInput:
    """One exact pure result and the profile governing its replay."""

    result: CpnFiringResult
    execution_profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.result) is not CpnFiringResult:
            raise TypeError("result must be CpnFiringResult")
        if type(self.execution_profile) is not WorkflowCpnExecutionProfile:
            raise TypeError(
                "execution_profile must be WorkflowCpnExecutionProfile"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultDecodingInput:
    """Retained result and the exact retained replay profile."""

    canonical_result: CpnCanonicalFiringResult
    execution_profile: WorkflowCpnExecutionProfile

    def __post_init__(self) -> None:
        if type(self.canonical_result) is not CpnCanonicalFiringResult:
            raise TypeError("canonical_result must be CpnCanonicalFiringResult")
        if type(self.execution_profile) is not WorkflowCpnExecutionProfile:
            raise TypeError(
                "execution_profile must be WorkflowCpnExecutionProfile"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalFiringResultDecodingResult:
    """One pure firing result reconstructed by deterministic replay."""

    result: CpnFiringResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnFiringResult:
            raise TypeError("result must be CpnFiringResult")


@final
class CpnCanonicalFiringResultCodec:
    """Encode complete firing inputs and verify results by pure replay."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalFiringResultCodecIdentity:
        """Return exact firing-result replay transport identity."""
        return CpnCanonicalFiringResultCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalFiringResultEncodingInput
    ) -> CpnCanonicalFiringResult:
        """Encode one complete success or failure and its replay inputs."""
        if type(encoding_input) is not CpnCanonicalFiringResultEncodingInput:
            raise TypeError(
                "encoding_input must be CpnCanonicalFiringResultEncodingInput"
            )
        result = encoding_input.result
        firing_input = result.firing_input
        definition = CpnCanonicalDefinitionCodec().encode(
            CpnCanonicalDefinitionEncodingInput(firing_input.definition)
        )
        predecessor = CpnCanonicalMarkingCodec().encode(
            CpnCanonicalMarkingEncodingInput(firing_input.predecessor_marking)
        )
        enablement = CpnCanonicalEnablementResultCodec().encode(
            CpnCanonicalEnablementResultEncodingInput(
                firing_input.enablement_result,
                firing_input.definition,
                firing_input.predecessor_marking,
            )
        )
        selection = CpnCanonicalSelectionResultCodec().encode(
            CpnCanonicalSelectionResultEncodingInput(
                firing_input.selection_result
            )
        )
        selected_binding = CpnCanonicalBindingCodec().encode(
            CpnCanonicalBindingEncodingInput(firing_input.selected_binding)
        )
        external_binding = CpnCanonicalBindingCodec().encode(
            CpnCanonicalBindingEncodingInput(
                firing_input.external_output_binding
            )
        )
        successor = (
            None
            if result.successor_marking is None
            else CpnCanonicalMarkingCodec().encode(
                CpnCanonicalMarkingEncodingInput(result.successor_marking)
            )
        )
        profile = encoding_input.execution_profile
        profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
            WorkflowCpnExecutionProfileIdentityDerivationInput(profile)
        )
        state = {
            "definition_canonical_bytes_hex": definition.canonical_bytes.hex(),
            "directive_identity": (
                None
                if firing_input.directive_identity is None
                else firing_input.directive_identity.value
            ),
            "enablement_canonical_bytes_hex": (
                enablement.canonical_bytes.hex()
            ),
            "execution_profile": {
                name: getattr(profile, name)
                for name in profile.__dataclass_fields__
            },
            "execution_profile_identity": profile_identity.value,
            "external_output_binding_canonical_bytes_hex": (
                external_binding.canonical_bytes.hex()
            ),
            "outcome": result.outcome.value,
            "predecessor_marking_canonical_bytes_hex": (
                predecessor.canonical_bytes.hex()
            ),
            "profile": _FIRING_PROFILE,
            "result_identity": result.identity.value,
            "selected_binding_canonical_bytes_hex": (
                selected_binding.canonical_bytes.hex()
            ),
            "selection_canonical_bytes_hex": selection.canonical_bytes.hex(),
            "successor_marking_canonical_bytes_hex": (
                None if successor is None else successor.canonical_bytes.hex()
            ),
            "transition_identity": firing_input.transition_identity.value,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_FIRING_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical firing result exceeds byte bound",
            )
        return CpnCanonicalFiringResult(encoded)

    def decode(
        self, decoding_input: CpnCanonicalFiringResultDecodingInput
    ) -> CpnCanonicalFiringResultDecodingResult:
        """Reconstruct all inputs, replay pure firing, and verify correlations."""
        if type(decoding_input) is not CpnCanonicalFiringResultDecodingInput:
            raise TypeError(
                "decoding_input must be CpnCanonicalFiringResultDecodingInput"
            )
        document = decoding_input.canonical_result
        retained_profile = decoding_input.execution_profile
        profile_identity = WorkflowCpnExecutionProfileIdentityDeriver().execute(
            WorkflowCpnExecutionProfileIdentityDerivationInput(retained_profile)
        )
        resolution = WorkflowCpnExecutionProfileResolver().execute(
            WorkflowCpnExecutionProfileResolutionRequest(
                decoding_input.execution_profile
            )
        )
        if (
            resolution.profile_identity != profile_identity
            or not resolution.is_available
            or resolution.transition_firer is None
        ):
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                ("execution_profile_identity",),
                "retained execution profile is not exactly resolved",
            )
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            expected_fields = {
                "definition_canonical_bytes_hex",
                "directive_identity",
                "enablement_canonical_bytes_hex",
                "execution_profile",
                "execution_profile_identity",
                "external_output_binding_canonical_bytes_hex",
                "outcome",
                "predecessor_marking_canonical_bytes_hex",
                "profile",
                "result_identity",
                "selected_binding_canonical_bytes_hex",
                "selection_canonical_bytes_hex",
                "successor_marking_canonical_bytes_hex",
                "transition_identity",
            }
            if type(state) is not dict or set(state) != expected_fields:
                raise TypeError("root shape")
            expected_profile_state = {
                name: getattr(retained_profile, name)
                for name in retained_profile.__dataclass_fields__
            }
            if (
                state["execution_profile"] != expected_profile_state
                or state["execution_profile_identity"] != profile_identity.value
            ):
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    ("execution_profile",),
                    "retained execution profile differs from canonical replay input",
                )
            if state["profile"] != _FIRING_PROFILE:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical firing-result profile",
                )
            required_strings = tuple(
                state[name]
                for name in (
                    "definition_canonical_bytes_hex",
                    "enablement_canonical_bytes_hex",
                    "external_output_binding_canonical_bytes_hex",
                    "outcome",
                    "predecessor_marking_canonical_bytes_hex",
                    "result_identity",
                    "selected_binding_canonical_bytes_hex",
                    "selection_canonical_bytes_hex",
                    "transition_identity",
                )
            )
            if any(type(item) is not str for item in required_strings):
                raise TypeError("firing-result fields")
            definition = (
                CpnCanonicalDefinitionCodec()
                .decode(
                    CpnCanonicalDefinitionDecodingInput(
                        CpnCanonicalDefinition(
                            bytes.fromhex(required_strings[0])
                        )
                    )
                )
                .definition
            )
            predecessor = (
                CpnCanonicalMarkingCodec()
                .decode(
                    CpnCanonicalMarkingDecodingInput(
                        CpnCanonicalMarking(bytes.fromhex(required_strings[4])),
                        definition,
                    )
                )
                .marking
            )
            enablement = (
                CpnCanonicalEnablementResultCodec()
                .decode(
                    CpnCanonicalEnablementResultDecodingInput(
                        CpnCanonicalEnablementResult(
                            bytes.fromhex(required_strings[1])
                        ),
                    )
                )
                .result
            )
            selection = (
                CpnCanonicalSelectionResultCodec()
                .decode(
                    CpnCanonicalSelectionResultDecodingInput(
                        CpnCanonicalSelectionResult(
                            bytes.fromhex(required_strings[7])
                        ),
                        definition.control_record_types,
                    )
                )
                .result
            )
            external_binding = (
                CpnCanonicalBindingCodec()
                .decode(
                    CpnCanonicalBindingDecodingInput(
                        CpnCanonicalBinding(bytes.fromhex(required_strings[2])),
                        definition.control_record_types,
                    )
                )
                .binding
            )
            selected_binding = (
                CpnCanonicalBindingCodec()
                .decode(
                    CpnCanonicalBindingDecodingInput(
                        CpnCanonicalBinding(bytes.fromhex(required_strings[6])),
                        definition.control_record_types,
                    )
                )
                .binding
            )
            directive_identity = state["directive_identity"]
            if (
                directive_identity is not None
                and type(directive_identity) is not str
            ):
                raise TypeError("directive identity")
            firing_input = CpnFiringInput(
                definition,
                CpnTransitionIdentity(required_strings[8]),
                predecessor,
                enablement,
                selection,
                selected_binding,
                (
                    None
                    if directive_identity is None
                    else CpnSelectionDirectiveIdentity(directive_identity)
                ),
                external_binding,
            )
            assert resolution.transition_firer is not None
            result = resolution.transition_firer.execute(firing_input)
            if result.outcome is not CpnFiringOutcomeKind(required_strings[3]):
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    ("outcome",),
                    "firing outcome differs from pure replay",
                )
            if result.identity != CpnFiringResultIdentity(required_strings[5]):
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    ("result_identity",),
                    "firing-result identity differs from pure replay",
                )
            successor_hex = state["successor_marking_canonical_bytes_hex"]
            if successor_hex is None:
                if result.successor_marking is not None:
                    raise CpnCanonicalCodecError(
                        CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                        ("successor_marking_canonical_bytes_hex",),
                        "retained successor is absent but replay produced one",
                    )
            else:
                if type(successor_hex) is not str:
                    raise TypeError("successor marking")
                retained_successor = (
                    CpnCanonicalMarkingCodec()
                    .decode(
                        CpnCanonicalMarkingDecodingInput(
                            CpnCanonicalMarking(bytes.fromhex(successor_hex)),
                            definition,
                        )
                    )
                    .marking
                )
                if retained_successor != result.successor_marking:
                    raise CpnCanonicalCodecError(
                        CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                        ("successor_marking_canonical_bytes_hex",),
                        "retained successor differs from pure replay",
                    )
        except CpnCanonicalCodecError:
            raise
        except (
            KeyError,
            OverflowError,
            RecursionError,
            TypeError,
            UnicodeError,
            ValueError,
        ) as exc:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.INVALID_SHAPE,
                (),
                f"firing-result decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(
            CpnCanonicalFiringResultEncodingInput(result, retained_profile)
        )
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "firing-result bytes differ from exact replay encoding",
            )
        return CpnCanonicalFiringResultDecodingResult(result)
