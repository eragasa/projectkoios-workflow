# CPN control-record owner components

Status: implementation candidate; not a provider-consumption or migration gate.

This inventory maps contract vectors 42–48 to directly callable, identity-bearing
Workflow operations. It does not authorize provider execution, migration, or
scientific acceptance.

## Public operation graph

| Operation | Typed input/result | Closed failure surface | Direct test |
|---|---|---|---|
| `CpnControlRecordTypeGraphValidator` | `CpnControlRecordTypeGraphValidationInput` → `CpnControlRecordValidationResult` | `CpnControlRecordValidationIssueCode` | `test__CpnControlRecordTypeGraphValidator.py` |
| `CpnControlRecordSchemaValidator` | `CpnControlRecordSchemaValidationInput` → `CpnControlRecordValidationResult` | `CpnControlRecordValidationIssueCode` | `test__CpnControlRecordSchemaValidator.py` |
| `CpnValueCanonicalizer` / `CpnValueCanonicalDecoder` | tagged value input → immutable canonical state / admitted value | `TypeError` or translated `ValueError`; cycles, depth, and nodes are bounded | `test__CpnValueCanonicalizer.py`, mirrored decoder tests |
| `CpnValueOrderingPolicy` | `CpnValueOrderingInput` → `CpnValueOrderingResult` | translated `TypeError` or `ValueError` | `test__CpnValueOrderingPolicy.py` |
| `CpnFieldProjector` | `CpnFieldProjectionInput` → `CpnFieldProjectionResult` | `CpnExpressionOperationErrorCode` | `test__CpnFieldProjector.py` |
| `CpnControlRecordConstructor` | `CpnControlRecordConstructionInput` → `CpnControlRecordConstructionResult` | `CpnExpressionOperationErrorCode` | `test__CpnControlRecordConstructor.py` |
| `CpnExpressionStructureValidator` | `CpnExpressionStructureValidationInput` → `CpnExpressionStructureValidationResult` | `CpnExpressionOperationErrorCode` findings | `test__CpnExpressionStructureValidator.py` |
| `CpnExpressionVariableCollector` | `CpnExpressionVariableCollectionInput` → `CpnExpressionVariableCollectionResult` | bounded `CpnExpressionOperationError` | mirrored collector test |
| `CpnGuardExpressionCollector` / `CpnGuardVariableCollector` | bounded guard input → exact ordered expression/variable tuples | bounded `CpnExpressionOperationError` | `test__CpnGuardExpressionCollector.py`, mirrored variable-collector test |
| `CpnExpressionEvaluator` | `CpnExpressionEvaluationInput` → `CpnExpressionEvaluationResult` | `CpnExpressionOperationErrorCode` | `test__CpnExpressionEvaluator.py` |
| `CpnDuplicateRejectingObjectPairsHook` / `CpnJsonNumberRejector` | JSON parser callback input → closed parsed state or rejection | `CpnCanonicalCodecErrorCode` | mirrored callable tests plus adversarial codec tests |
| `CpnCanonicalJsonParser` | `CpnCanonicalJsonParsingInput` → `CpnCanonicalJsonParsingResult` | `CpnCanonicalCodecErrorCode` | mirrored parser test plus adversarial codec tests |
| `CpnControlRecordCanonicalCodec` | canonical encoding/decoding inputs → exact document/admitted record | `CpnCanonicalCodecErrorCode` | `test__CpnControlRecordCanonicalCodec.py` |
| `CpnValueExpressionCanonicalizer` / decoder | expression canonicalization/decoding inputs → exact state/expression | `CpnExpressionCanonicalCodecErrorCode` | `test__CpnValueExpressionCanonicalizer.py` |
| `CpnGuardCanonicalizer` / decoder | guard canonicalization/decoding inputs → exact state/guard | `CpnExpressionCanonicalCodecErrorCode` | mirrored action tests |
| `CpnCanonicalDefinitionCodec` | definition encoding/decoding inputs → content-derived document/definition | `CpnCanonicalDefinitionCodecErrorCode` | `test__CpnCanonicalDefinitionCodec.py` |
| `CpnExternalOutputValidator` | `CpnExternalOutputValidationInput` → `CpnExternalOutputValidationResult` | `CpnExternalOutputValidationIssueCode` | `test__CpnExternalOutputValidator.py` |
| `WorkflowCpnExecutionProfileBuilder` and identity deriver | no ambient input / exact profile → content identity | closed constructor failures | `test__WorkflowCpnExecutionProfile.py` |
| plan/export identity derivers and closure correlator | immutable closure inputs → content identities/correlation findings | typed constructor failures and `WorkflowCpnClosureCorrelationIssueCode` | `test__WorkflowCpnExecutionProfile.py` |

Every public `Cpn*` record, enum, identity, input, result, error, and operation has
a mirrored `test__ClassName__.py`. Meaningful operations additionally have the
direct behavioral tests named above.

## Package ownership

The implementation follows semantic ownership rather than flat utility buckets:

- `control/records/` owns type-graph validation, schema admission, validation
  findings, value canonicalization, value ordering, and record canonical
  transport as separate modules.
- `definitions.py` owns definition, place, transition, and arc identities;
  `bindings.py` owns ordered transition bindings; `markings.py` owns only
  marking and place-multiset state. Binding-variable identity belongs to the
  expression grammar that declares variable meaning.
- `expressions/` owns the closed grammar and its projection, construction,
  validation, collection, and evaluation operations.
- `canonical/` owns strict JSON parsing plus definition, marking, and expression
  transports; value-expression and guard transports have separate modules under
  `canonical/expressions/`.
- `validation/` separates definition validation, marking validation, and shared
  immutable findings.
- `shadow/` separates firing from replay correlation.
- `children/interfaces.py` and `children/exports/` retain child interface and
  export ownership without treating an export as an execution plan.

The aggregate `projectkoios.workflow.petrinet.colored` initializer exports no
facade names. Candidate types are imported directly from their semantic owner
modules; deleted flat modules are not retained as compatibility shims.

## Vector mapping

| Contract vector | Implemented owner evidence | External or review boundary |
|---|---|---|
| 42 | exact control-record type/value bounds; iterative depth/node/cycle handling; UTF-8/string/sequence/field/byte bounds; canonical round trips and bound rejection | independent review must assess sufficiency; it is not encoded as a missing implementation promise |
| 43 | duplicate, missing/extra, kind, order, nested-type, cyclic graph/value, over-depth, noncanonical-byte, and substitution failures | provider-owned payload mutations remain provider evidence |
| 44 | record schemas, color/type admission, expressions, canonical definition, every profile field, plan fields, interfaces, exports, and deployment descriptors are identity inputs | independent review remains required |
| 45 | exact projection and constructor actions preserve values and identities | simulations SCF constructor mapping requires a provider-owned export artifact |
| 46 | kernel retains one `CONTROL_RECORD` as one topology-visible token | exact simulations parity requires the separately supplied provider artifact |
| 47 | canonical record/expression/definition/marking/enablement/selection/firing replay and profile/plan correlations reject retained-state substitutions | provider execution and scientific acceptance remain outside Workflow authority |
| 48 | grammar has four closed variants; action gates reject private, static, class, module-level, anonymous, multi-request, and configuration-injected callable semantics | fresh independent review remains required |

## Non-gates

The current candidate does **not** make `WorkflowChildDefinitionExport`, complete
plan construction, SNAKES export, `CpnShadowFiringResult`, nested execution,
persistence, terminal delivery, or replay provider-ready. Simulations must keep
using its merged source-conformance gate only until a later reviewed owner commit
reports stable import paths and exact identities.
