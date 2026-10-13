"""Canonical transport for complete CPN selection results."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from ..enablement.outcomes import (
    CpnEnablementResultIdentity,
    CpnOrderingPolicyIdentity,
)
from ..selection import (
    CpnBindingSelectorIdentity,
    CpnSelectionFailureCode,
    CpnSelectionOutcomeKind,
    CpnSelectionResult,
    CpnSelectionResultIdentity,
)
from ..values import CpnControlRecordTypeDefinition
from .bindings import (
    CpnCanonicalBinding,
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingDecodingInput,
    CpnCanonicalBindingEncodingInput,
)
from .directives import (
    CpnCanonicalSelectionDirective,
    CpnCanonicalSelectionDirectiveCodec,
    CpnCanonicalSelectionDirectiveDecodingInput,
    CpnCanonicalSelectionDirectiveEncodingInput,
)
from .json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
    CpnCanonicalJsonParser,
    CpnCanonicalJsonParsingInput,
)

_SELECTION_PROFILE = "projectkoios.workflow.cpn-selection-result-json:0.1.0"
_MAXIMUM_SELECTION_BYTES = 6_500_000


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionResultIdentity:
    """Content-derived identity of exact canonical selection-result bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-selection-result:0.1:"
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
class CpnCanonicalSelectionResult:
    """Exact selection-result bytes and derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalSelectionResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_SELECTION_BYTES:
            raise ValueError("canonical selection result exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _SELECTION_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalSelectionResultIdentity(
                "projectkoios.workflow.cpn-selection-result:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionResultEncodingInput:
    """One exact selection result requested for canonical encoding."""

    result: CpnSelectionResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnSelectionResult:
            raise TypeError("result must be CpnSelectionResult")


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionResultDecodingInput:
    """One canonical result and exact retained record schemas."""

    canonical_result: CpnCanonicalSelectionResult
    control_record_types: tuple[CpnControlRecordTypeDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.canonical_result) is not CpnCanonicalSelectionResult:
            raise TypeError(
                "canonical_result must be CpnCanonicalSelectionResult"
            )
        if type(self.control_record_types) is not tuple or any(
            type(item) is not CpnControlRecordTypeDefinition
            for item in self.control_record_types
        ):
            raise TypeError(
                "control_record_types must contain exact type definitions"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionResultDecodingResult:
    """One selection result reconstructed from canonical bytes."""

    result: CpnSelectionResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnSelectionResult:
            raise TypeError("result must be CpnSelectionResult")


@dataclass(frozen=True, slots=True)
class CpnCanonicalSelectionResultCodecIdentity:
    """Identity of exact selection-result transport semantics."""

    value: str = (
        "projectkoios.workflow.cpn.canonical-selection-result-codec:0.1"
    )


@final
class CpnCanonicalSelectionResultCodec:
    """Encode and strictly reconstruct complete selection outcomes."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalSelectionResultCodecIdentity:
        """Return exact selection-result transport semantics identity."""
        return CpnCanonicalSelectionResultCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalSelectionResultEncodingInput
    ) -> CpnCanonicalSelectionResult:
        """Encode one selected, empty, no-match, or failure outcome."""
        if type(encoding_input) is not CpnCanonicalSelectionResultEncodingInput:
            raise TypeError(
                "encoding_input must be CpnCanonicalSelectionResultEncodingInput"
            )
        result = encoding_input.result
        binding_hex = None
        if result.selected_binding is not None:
            binding_hex = (
                CpnCanonicalBindingCodec()
                .encode(
                    CpnCanonicalBindingEncodingInput(result.selected_binding)
                )
                .canonical_bytes.hex()
            )
        directive_hex = None
        if result.directive is not None:
            directive_hex = (
                CpnCanonicalSelectionDirectiveCodec()
                .encode(
                    CpnCanonicalSelectionDirectiveEncodingInput(
                        result.directive
                    )
                )
                .canonical_bytes.hex()
            )
        state = {
            "directive_canonical_bytes_hex": directive_hex,
            "enablement_result_identity": (
                result.enablement_result_identity.value
            ),
            "failure_code": (
                None
                if result.failure_code is None
                else result.failure_code.value
            ),
            "ordering_policy_identity": result.ordering_policy_identity.value,
            "outcome": result.outcome.value,
            "profile": _SELECTION_PROFILE,
            "result_identity": result.identity.value,
            "selected_binding_canonical_bytes_hex": binding_hex,
            "selector_identity": result.selector_identity.value,
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_SELECTION_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical selection result exceeds byte bound",
            )
        return CpnCanonicalSelectionResult(encoded)

    def decode(
        self, decoding_input: CpnCanonicalSelectionResultDecodingInput
    ) -> CpnCanonicalSelectionResultDecodingResult:
        """Parse, reconstruct, correlate, and exactly re-encode a result."""
        if type(decoding_input) is not CpnCanonicalSelectionResultDecodingInput:
            raise TypeError(
                "decoding_input must be CpnCanonicalSelectionResultDecodingInput"
            )
        document = decoding_input.canonical_result
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            expected_fields = {
                "directive_canonical_bytes_hex",
                "enablement_result_identity",
                "failure_code",
                "ordering_policy_identity",
                "outcome",
                "profile",
                "result_identity",
                "selected_binding_canonical_bytes_hex",
                "selector_identity",
            }
            if type(state) is not dict or set(state) != expected_fields:
                raise TypeError("root shape")
            if state["profile"] != _SELECTION_PROFILE:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical selection-result profile",
                )
            for name in (
                "enablement_result_identity",
                "ordering_policy_identity",
                "outcome",
                "result_identity",
                "selector_identity",
            ):
                if type(state[name]) is not str:
                    raise TypeError(name)
            binding = None
            binding_hex = state["selected_binding_canonical_bytes_hex"]
            if binding_hex is not None:
                if type(binding_hex) is not str:
                    raise TypeError("selected binding")
                binding = (
                    CpnCanonicalBindingCodec()
                    .decode(
                        CpnCanonicalBindingDecodingInput(
                            CpnCanonicalBinding(bytes.fromhex(binding_hex)),
                            decoding_input.control_record_types,
                        )
                    )
                    .binding
                )
            directive = None
            directive_hex = state["directive_canonical_bytes_hex"]
            if directive_hex is not None:
                if type(directive_hex) is not str:
                    raise TypeError("directive")
                directive = (
                    CpnCanonicalSelectionDirectiveCodec()
                    .decode(
                        CpnCanonicalSelectionDirectiveDecodingInput(
                            CpnCanonicalSelectionDirective(
                                bytes.fromhex(directive_hex)
                            ),
                            decoding_input.control_record_types,
                        )
                    )
                    .directive
                )
            failure_code = state["failure_code"]
            if failure_code is not None and type(failure_code) is not str:
                raise TypeError("failure code")
            result = CpnSelectionResult(
                CpnEnablementResultIdentity(
                    state["enablement_result_identity"]
                ),
                CpnBindingSelectorIdentity(state["selector_identity"]),
                CpnOrderingPolicyIdentity(state["ordering_policy_identity"]),
                CpnSelectionOutcomeKind(state["outcome"]),
                selected_binding=binding,
                directive=directive,
                failure_code=(
                    None
                    if failure_code is None
                    else CpnSelectionFailureCode(failure_code)
                ),
            )
            if result.identity != CpnSelectionResultIdentity(
                state["result_identity"]
            ):
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    ("result_identity",),
                    "selection-result identity differs from reconstructed content",
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
                f"selection-result decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(
            CpnCanonicalSelectionResultEncodingInput(result)
        )
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "selection-result bytes differ from exact re-encoding",
            )
        return CpnCanonicalSelectionResultDecodingResult(result)
