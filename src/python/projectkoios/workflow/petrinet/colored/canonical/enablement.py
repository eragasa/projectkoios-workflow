"""Canonical transport for complete CPN enablement results."""

import json
from dataclasses import dataclass, field
from hashlib import sha256
from string import hexdigits
from typing import final

from ..definitions import (
    CpnDefinition,
    CpnDefinitionIdentity,
    CpnSelectionPolicy,
)
from ..enablement import (
    CpnEnablementFailure,
    CpnEnablementFailureCode,
    CpnEnablementFailureIdentity,
    CpnEnablementResult,
    CpnEnablementResultIdentity,
    CpnOrderingPolicyIdentity,
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
    CpnTransitionEnablerIdentity,
)
from ..expressions.evaluation import CpnExpressionEvaluatorIdentity
from ..markings import CpnMarking, CpnMarkingIdentity
from ..validation.findings import CpnValidationIssue, CpnValidationIssueCode
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

_ENABLEMENT_PROFILE = "projectkoios.workflow.cpn-enablement-result-json:0.1.0"
_MAXIMUM_ENABLEMENT_BYTES = 33_554_432


@dataclass(frozen=True, slots=True)
class CpnCanonicalEnablementResultIdentity:
    """Content-derived identity of exact canonical enablement-result bytes."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("identity must be a string")
        prefix = "projectkoios.workflow.cpn-enablement-result:0.1:"
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
class CpnCanonicalEnablementResult:
    """Exact enablement-result bytes and derived correlations."""

    canonical_bytes: bytes
    representation_profile_identity: str = field(init=False)
    sha256: str = field(init=False)
    identity: CpnCanonicalEnablementResultIdentity = field(init=False)

    def __post_init__(self) -> None:
        if type(self.canonical_bytes) is not bytes:
            raise TypeError("canonical_bytes must be bytes")
        if not self.canonical_bytes:
            raise ValueError("canonical_bytes must not be empty")
        if len(self.canonical_bytes) > _MAXIMUM_ENABLEMENT_BYTES:
            raise ValueError("canonical enablement result exceeds byte bound")
        digest = sha256(self.canonical_bytes).hexdigest()
        object.__setattr__(
            self, "representation_profile_identity", _ENABLEMENT_PROFILE
        )
        object.__setattr__(self, "sha256", digest)
        object.__setattr__(
            self,
            "identity",
            CpnCanonicalEnablementResultIdentity(
                "projectkoios.workflow.cpn-enablement-result:0.1:" + digest
            ),
        )


@dataclass(frozen=True, slots=True)
class CpnCanonicalEnablementResultEncodingInput:
    """One exact enablement result requested for canonical encoding."""

    result: CpnEnablementResult
    definition: CpnDefinition
    marking: CpnMarking

    def __post_init__(self) -> None:
        if type(self.result) is not CpnEnablementResult:
            raise TypeError("result must be CpnEnablementResult")
        if type(self.definition) is not CpnDefinition:
            raise TypeError("definition must be CpnDefinition")
        if type(self.marking) is not CpnMarking:
            raise TypeError("marking must be CpnMarking")


@dataclass(frozen=True, slots=True)
class CpnCanonicalEnablementResultDecodingInput:
    """One self-contained canonical enablement result."""

    canonical_result: CpnCanonicalEnablementResult

    def __post_init__(self) -> None:
        if type(self.canonical_result) is not CpnCanonicalEnablementResult:
            raise TypeError(
                "canonical_result must be CpnCanonicalEnablementResult"
            )


@dataclass(frozen=True, slots=True)
class CpnCanonicalEnablementResultDecodingResult:
    """One enablement result reconstructed from canonical bytes."""

    result: CpnEnablementResult

    def __post_init__(self) -> None:
        if type(self.result) is not CpnEnablementResult:
            raise TypeError("result must be CpnEnablementResult")


@dataclass(frozen=True, slots=True)
class CpnCanonicalEnablementResultCodecIdentity:
    """Identity of exact enablement-result transport semantics."""

    value: str = (
        "projectkoios.workflow.cpn.canonical-enablement-result-codec:0.1"
    )


@final
class CpnCanonicalEnablementResultCodec:
    """Encode and strictly reconstruct complete enablement outcomes."""

    __slots__ = ()

    @property
    def identity(self) -> CpnCanonicalEnablementResultCodecIdentity:
        """Return exact enablement-result transport semantics identity."""
        return CpnCanonicalEnablementResultCodecIdentity()

    def encode(
        self, encoding_input: CpnCanonicalEnablementResultEncodingInput
    ) -> CpnCanonicalEnablementResult:
        """Encode one complete success or structured failure outcome."""
        if (
            type(encoding_input)
            is not CpnCanonicalEnablementResultEncodingInput
        ):
            raise TypeError(
                "encoding_input must be CpnCanonicalEnablementResultEncodingInput"
            )
        result = encoding_input.result
        replayed = CpnTransitionEnabler().execute(
            CpnTransitionEnablementRequest(
                encoding_input.definition,
                encoding_input.marking,
                result.expression_evaluator_identity,
                result.ordering_policy_identity,
            )
        )
        if replayed != result:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                (),
                "enablement result differs from exact pure replay",
            )
        definition_document = CpnCanonicalDefinitionCodec().encode(
            CpnCanonicalDefinitionEncodingInput(encoding_input.definition)
        )
        marking_document = CpnCanonicalMarkingCodec().encode(
            CpnCanonicalMarkingEncodingInput(encoding_input.marking)
        )
        bindings = None
        if result.enabled_bindings is not None:
            bindings = [
                CpnCanonicalBindingCodec()
                .encode(CpnCanonicalBindingEncodingInput(item))
                .canonical_bytes.hex()
                for item in result.enabled_bindings
            ]
        failure = None
        if result.failure is not None:
            failure = {
                "claim_boundary": list(result.failure.claim_boundary),
                "code": result.failure.code.value,
                "diagnostic": result.failure.diagnostic,
                "expected_condition": result.failure.expected_condition,
                "observed_condition": result.failure.observed_condition,
                "operation_phase": result.failure.operation_phase,
                "validation_issues": [
                    {
                        "code": item.code.value,
                        "message": item.message,
                        "path": list(item.path),
                        "related_identities": list(item.related_identities),
                    }
                    for item in result.failure.validation_issues
                ],
            }
        state = {
            "definition_canonical_bytes_hex": (
                definition_document.canonical_bytes.hex()
            ),
            "definition_identity": result.definition_identity.value,
            "enabled_binding_canonical_bytes_hex": bindings,
            "expression_evaluator_identity": (
                result.expression_evaluator_identity.value
            ),
            "failure": failure,
            "marking_canonical_bytes_hex": marking_document.canonical_bytes.hex(),
            "marking_identity": result.marking_identity.value,
            "ordering_policy_identity": result.ordering_policy_identity.value,
            "profile": _ENABLEMENT_PROFILE,
            "result_identity": result.identity.value,
            "selection_policy": result.selection_policy.value,
            "transition_enabler_identity": (
                result.transition_enabler_identity.value
            ),
        }
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        if len(encoded) > _MAXIMUM_ENABLEMENT_BYTES:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.DOCUMENT_TOO_LARGE,
                (),
                "canonical enablement result exceeds byte bound",
            )
        return CpnCanonicalEnablementResult(encoded)

    def decode(
        self, decoding_input: CpnCanonicalEnablementResultDecodingInput
    ) -> CpnCanonicalEnablementResultDecodingResult:
        """Parse, reconstruct, and exactly re-encode one enablement result."""
        if (
            type(decoding_input)
            is not CpnCanonicalEnablementResultDecodingInput
        ):
            raise TypeError(
                "decoding_input must be CpnCanonicalEnablementResultDecodingInput"
            )
        document = decoding_input.canonical_result
        try:
            state = json.loads(
                CpnCanonicalJsonParser()
                .execute(CpnCanonicalJsonParsingInput(document.canonical_bytes))
                .canonical_bytes
            )
            expected_fields = {
                "definition_canonical_bytes_hex",
                "definition_identity",
                "enabled_binding_canonical_bytes_hex",
                "expression_evaluator_identity",
                "failure",
                "marking_canonical_bytes_hex",
                "marking_identity",
                "ordering_policy_identity",
                "profile",
                "result_identity",
                "selection_policy",
                "transition_enabler_identity",
            }
            if type(state) is not dict or set(state) != expected_fields:
                raise TypeError("root shape")
            if state["profile"] != _ENABLEMENT_PROFILE:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.UNSUPPORTED_PROFILE,
                    ("profile",),
                    "unsupported canonical enablement-result profile",
                )
            string_fields = tuple(
                state[name]
                for name in (
                    "definition_identity",
                    "expression_evaluator_identity",
                    "marking_identity",
                    "ordering_policy_identity",
                    "result_identity",
                    "selection_policy",
                    "transition_enabler_identity",
                )
            )
            if any(type(item) is not str for item in string_fields):
                raise TypeError("identity fields")
            definition_hex = state["definition_canonical_bytes_hex"]
            marking_hex = state["marking_canonical_bytes_hex"]
            if type(definition_hex) is not str or type(marking_hex) is not str:
                raise TypeError("canonical input documents")
            definition = (
                CpnCanonicalDefinitionCodec()
                .decode(
                    CpnCanonicalDefinitionDecodingInput(
                        CpnCanonicalDefinition(bytes.fromhex(definition_hex))
                    )
                )
                .definition
            )
            marking = (
                CpnCanonicalMarkingCodec()
                .decode(
                    CpnCanonicalMarkingDecodingInput(
                        CpnCanonicalMarking(bytes.fromhex(marking_hex)),
                        definition,
                    )
                )
                .marking
            )
            result_identity = CpnEnablementResultIdentity(string_fields[4])
            bindings_state = state["enabled_binding_canonical_bytes_hex"]
            bindings = None
            if bindings_state is not None:
                if type(bindings_state) is not list or any(
                    type(item) is not str for item in bindings_state
                ):
                    raise TypeError("enabled bindings")
                bindings = tuple(
                    CpnCanonicalBindingCodec()
                    .decode(
                        CpnCanonicalBindingDecodingInput(
                            CpnCanonicalBinding(bytes.fromhex(item)),
                            definition.control_record_types,
                        )
                    )
                    .binding
                    for item in bindings_state
                )
            failure_state = state["failure"]
            failure = None
            if failure_state is not None:
                if type(failure_state) is not dict or set(failure_state) != {
                    "claim_boundary",
                    "code",
                    "diagnostic",
                    "expected_condition",
                    "observed_condition",
                    "operation_phase",
                    "validation_issues",
                }:
                    raise TypeError("failure shape")
                claim_boundary = failure_state["claim_boundary"]
                issues_state = failure_state["validation_issues"]
                textual = tuple(
                    failure_state[name]
                    for name in (
                        "code",
                        "diagnostic",
                        "expected_condition",
                        "observed_condition",
                        "operation_phase",
                    )
                )
                if (
                    any(type(item) is not str for item in textual)
                    or type(claim_boundary) is not list
                    or any(type(item) is not str for item in claim_boundary)
                    or type(issues_state) is not list
                ):
                    raise TypeError("failure fields")
                decoded_issues: list[CpnValidationIssue] = []
                for issue_state in issues_state:
                    if type(issue_state) is not dict or set(issue_state) != {
                        "code",
                        "message",
                        "path",
                        "related_identities",
                    }:
                        raise TypeError("validation issue shape")
                    issue_code = issue_state["code"]
                    issue_message = issue_state["message"]
                    issue_path = issue_state["path"]
                    issue_related = issue_state["related_identities"]
                    if (
                        type(issue_code) is not str
                        or type(issue_message) is not str
                        or type(issue_path) is not list
                        or any(type(item) is not str for item in issue_path)
                        or type(issue_related) is not list
                        or any(type(item) is not str for item in issue_related)
                    ):
                        raise TypeError("validation issue fields")
                    decoded_issues.append(
                        CpnValidationIssue(
                            CpnValidationIssueCode(issue_code),
                            tuple(issue_path),
                            tuple(issue_related),
                            issue_message,
                        )
                    )
                failure = CpnEnablementFailure(
                    CpnEnablementFailureIdentity(result_identity),
                    CpnEnablementFailureCode(textual[0]),
                    textual[4],
                    textual[2],
                    textual[3],
                    textual[1],
                    tuple(decoded_issues),
                    tuple(claim_boundary),
                )
            result = CpnEnablementResult(
                result_identity,
                CpnDefinitionIdentity(string_fields[0]),
                CpnSelectionPolicy(string_fields[5]),
                CpnMarkingIdentity(string_fields[2]),
                CpnExpressionEvaluatorIdentity(string_fields[1]),
                CpnOrderingPolicyIdentity(string_fields[3]),
                CpnTransitionEnablerIdentity(string_fields[6]),
                enabled_bindings=bindings,
                failure=failure,
            )
            replayed = CpnTransitionEnabler().execute(
                CpnTransitionEnablementRequest(
                    definition,
                    marking,
                    result.expression_evaluator_identity,
                    result.ordering_policy_identity,
                )
            )
            if replayed != result:
                raise CpnCanonicalCodecError(
                    CpnCanonicalCodecErrorCode.IDENTITY_MISMATCH,
                    (),
                    "enablement result differs from exact pure replay",
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
                f"enablement-result decoding failed: {type(exc).__name__}",
            ) from exc
        reencoded = self.encode(
            CpnCanonicalEnablementResultEncodingInput(
                replayed, definition, marking
            )
        )
        if reencoded.canonical_bytes != document.canonical_bytes:
            raise CpnCanonicalCodecError(
                CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES,
                (),
                "enablement-result bytes differ from exact re-encoding",
            )
        return CpnCanonicalEnablementResultDecodingResult(replayed)
