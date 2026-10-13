"""Identity-closed pure transition firing orchestration."""

from __future__ import annotations
from dataclasses import dataclass
from typing import final
from ..enablement.transitions import (
    CpnTransitionEnablementRequest,
    CpnTransitionEnabler,
)
from ..expressions.evaluation import (
    CpnExpressionEvaluationInput,
    CpnExpressionEvaluator,
)
from ..external_outputs import (
    CpnExternalOutputValidationInput,
    CpnExternalOutputValidator,
)
from ..bindings import CpnBinding
from ..selection import (
    CpnBindingSelectionRequest,
    CpnBindingSelector,
    CpnSelectionOutcomeKind,
)
from ..validation.definitions import (
    CpnDefinitionValidationRequest,
    CpnDefinitionValidator,
)
from ..validation.markings import CpnMarkingValidationInput, CpnMarkingValidator
from ..values import CpnToken, CpnTokenIdentity, CpnValueKind
from .audits import CpnFiringAudit, CpnProducedToken, CpnTransitionFirerIdentity
from .failure_building import (
    CpnFiringFailureBuilder,
    CpnFiringFailureBuildingRequest,
)
from .identity_derivation import (
    CpnFiringFailureState,
    CpnFiringResultIdentityDerivationRequest,
    CpnFiringResultIdentityDeriver,
)
from .inputs import CpnFiringInput
from .occurrence_reconstruction import (
    CpnTokenOccurrenceReconstructionRequest,
    CpnTokenOccurrenceReconstructor,
)
from .results import (
    CpnFiringFailureCode,
    CpnFiringOutcomeKind,
    CpnFiringResult,
)
from .successor_marking import (
    CpnSuccessorMarkingBuilder,
    CpnSuccessorMarkingBuildingRequest,
)


_FIRER_IDENTITY = CpnTransitionFirerIdentity(
    "projectkoios.workflow.cpn.transition-firer:0.1"
)


@final
@dataclass(frozen=True, slots=True)
class CpnTransitionFirer:
    """Stateless action producing one pure identity-closed successor marking."""

    @property
    def identity(self) -> CpnTransitionFirerIdentity:
        """Return the identity of the compiled firing semantics."""
        return _FIRER_IDENTITY

    def execute(self, firing_input: CpnFiringInput) -> CpnFiringResult:
        """Validate the complete derivation and return success or structured failure."""
        if type(firing_input) is not CpnFiringInput:
            raise TypeError("firing_input must be CpnFiringInput")
        definition = firing_input.definition
        marking = firing_input.predecessor_marking
        definition_validation = CpnDefinitionValidator().execute(
            CpnDefinitionValidationRequest(definition)
        )
        if not definition_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INVALID_DEFINITION,
                        "definition_validation",
                        "a structurally valid definition",
                        "definition validation returned findings",
                        definition_validation.issues,
                    ),
                )
            )
        marking_validation = CpnMarkingValidator().execute(
            CpnMarkingValidationInput(definition, marking)
        )
        if not marking_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INVALID_PREDECESSOR_MARKING,
                        "marking_validation",
                        "a compatible complete predecessor marking",
                        "marking validation returned findings",
                        marking_validation.issues,
                    ),
                )
            )
        recomputed_enablement = CpnTransitionEnabler().execute(
            CpnTransitionEnablementRequest(definition, marking)
        )
        if recomputed_enablement != firing_input.enablement_result:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.ENABLEMENT_MISMATCH,
                        "enablement_replay",
                        "replay-equal complete enablement",
                        "supplied enablement differs from recomputation",
                    ),
                )
            )
        directive = firing_input.selection_result.directive
        recomputed_selection = CpnBindingSelector().execute(
            CpnBindingSelectionRequest(
                definition, recomputed_enablement, directive
            )
        )
        if recomputed_selection != firing_input.selection_result:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.SELECTION_MISMATCH,
                        "selection_replay",
                        "replay-equal exact selection",
                        "supplied selection differs from recomputation",
                    ),
                )
            )
        if (
            firing_input.selection_result.outcome
            is not (CpnSelectionOutcomeKind.SELECTED)
            or firing_input.selection_result.selected_binding
            != firing_input.selected_binding
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                        "selected_binding_validation",
                        "one exact selected binding",
                        "firing binding is not the selected binding",
                    ),
                )
            )
        if (
            firing_input.directive_identity
            != firing_input.selection_result.directive_identity
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.DIRECTIVE_MISMATCH,
                        "directive_validation",
                        "the exact selection directive identity or absence",
                        "firing directive identity differs from selection",
                    ),
                )
            )
        binding = firing_input.selected_binding
        transition = next(
            (
                item
                for item in definition.transitions
                if item.identity == binding.transition_identity
            ),
            None,
        )
        if (
            transition is None
            or firing_input.transition_identity != binding.transition_identity
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TRANSITION_OR_BINDING_MISMATCH,
                        "transition_validation",
                        "the selected defined transition",
                        "transition identity differs from selected binding",
                    ),
                )
            )
        external = firing_input.external_output_binding
        external_validation = CpnExternalOutputValidator().execute(
            CpnExternalOutputValidationInput(
                definition, transition.identity, external
            )
        )
        if not external_validation.is_valid:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.EXTERNAL_OUTPUT_BINDING_MISMATCH,
                        "external_output_validation",
                        "exact declared external-output assignments in order",
                        "external-output binding is incomplete, extra, reordered, or mismatched",
                    ),
                )
            )
        reconstruction = CpnTokenOccurrenceReconstructor().execute(
            CpnTokenOccurrenceReconstructionRequest(
                definition, marking, binding
            )
        )
        if reconstruction.failure is not None:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.INPUT_OCCURRENCE_RECONSTRUCTION_FAILED,
                        "input_reconstruction",
                        "one canonical feasible occurrence assignment",
                        "selected value binding cannot be reconstructed",
                    ),
                )
            )
        assert reconstruction.success is not None
        consumed = reconstruction.success.consumed
        read = reconstruction.success.read
        inhibitors = reconstruction.success.inhibitors
        combined = CpnBinding(
            transition.identity, binding.assignments + external.assignments
        )
        produced: list[CpnProducedToken] = []
        evaluator = CpnExpressionEvaluator()
        try:
            for arc in definition.arcs:
                if (
                    arc.transition_identity != transition.identity
                    or arc.output_inscription is None
                ):
                    continue
                for index, template in enumerate(
                    arc.output_inscription.templates
                ):
                    value = evaluator.execute(
                        CpnExpressionEvaluationInput(
                            template.value_expression,
                            combined,
                            definition.control_record_types,
                        )
                    ).value
                    identity = None
                    if template.token_identity_expression is not None:
                        identity_value = evaluator.execute(
                            CpnExpressionEvaluationInput(
                                template.token_identity_expression,
                                combined,
                                definition.control_record_types,
                            )
                        ).value
                        if identity_value.kind is not CpnValueKind.STRING:
                            raise TypeError(
                                "token identity expression must produce string"
                            )
                        assert type(identity_value.value) is str
                        identity = CpnTokenIdentity(identity_value.value)
                    token = CpnToken(template.color_identity, value, identity)
                    produced.append(
                        CpnProducedToken(
                            arc.identity, arc.place_identity, index, token
                        )
                    )
        except (KeyError, TypeError, ValueError) as exc:
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.OUTPUT_EVALUATION_FAILED,
                        "output_evaluation",
                        "well-typed total output templates",
                        f"{type(exc).__name__}: {exc}",
                    ),
                )
            )
        consumed_coordinates = {
            (item.place_identity, item.occurrence_ordinal) for item in consumed
        }
        retained_identities = {
            token.token_identity
            for place in marking.places
            for index, token in enumerate(place.tokens)
            if (place.place_identity, index) not in consumed_coordinates
            and token.token_identity is not None
        }
        produced_identities = tuple(
            item.token.token_identity
            for item in produced
            if item.token.token_identity is not None
        )
        if len(set(produced_identities)) != len(produced_identities) or (
            retained_identities & set(produced_identities)
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.TOKEN_IDENTITY_COLLISION,
                        "produced_identity_validation",
                        "new unique identities or identities released by consumption",
                        "produced identity is duplicate or collides with a retained token",
                    ),
                )
            )
        audit = CpnFiringAudit(
            consumed, read, inhibitors, tuple(produced), self.identity
        )
        successor = CpnSuccessorMarkingBuilder().execute(
            CpnSuccessorMarkingBuildingRequest(firing_input, audit)
        )
        if (
            not CpnMarkingValidator()
            .execute(CpnMarkingValidationInput(definition, successor))
            .is_valid
        ):
            return CpnFiringFailureBuilder().execute(
                CpnFiringFailureBuildingRequest(
                    firing_input,
                    CpnFiringFailureState(
                        CpnFiringFailureCode.PRODUCED_TOKEN_INVALID,
                        "successor_validation",
                        "a definition-compatible successor marking",
                        "produced tokens make the successor invalid",
                    ),
                )
            )
        result_identity = CpnFiringResultIdentityDeriver().execute(
            CpnFiringResultIdentityDerivationRequest(
                firing_input, successor=successor, audit=audit
            )
        )
        return CpnFiringResult(
            result_identity,
            firing_input,
            CpnFiringOutcomeKind.SUCCESS,
            successor,
            audit,
        )
