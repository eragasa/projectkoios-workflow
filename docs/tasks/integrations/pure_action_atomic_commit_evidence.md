# Experimental pure-action atomic commit evidence

## Scope

This record covers the bounded v0 atomic transition from one current successful
pure-firing candidate to a consumed reservation and advanced authoritative
marking coordinate. The supplied in-memory repository is software evidence, not
a durable production persistence implementation.

## Implemented boundary

- `ExperimentalWorkflowPureActionCommit` content-identifies the exact CPN plan,
  reservation, source-authority observations, mapped invocation, SDK request and
  owner-result identities, mapped-result identity, CPN firing outcome and result,
  and predecessor/successor marking coordinates.
- The commit record contains compact identities only. It contains no inline SDK
  request/result payload bodies, private owner locators, owner objects, live
  repositories, or CPN definitions.
- `ExperimentalWorkflowPureActionCommitService` reconstructs and correlates the
  authorized inputs, CPN-plan-bound reservation, mapped invocation, and current
  successful pure-firing candidate before constructing commit evidence.
- Source observations are reloaded immediately before entering the atomic
  reservation repository boundary. A changed or uncertain source fails closed
  without consuming the reservation.
- The nominal reservation repository exposes one `commit` operation. Under one
  lock, the in-memory implementation verifies the exact active reservation,
  retains the compact commit identity and coordinates, consumes the reservation,
  and advances the current marking and monotonic revision.
- The repository returns closed `COMMITTED`, `IDEMPOTENT`, `STALE`, or
  `CONFLICT` outcomes. There is no standalone consume operation.
- Exact replay is idempotent even after source observations later change.
  Concurrent exact commits have one `COMMITTED` winner and idempotent followers;
  distinct commits for one reservation have one winner and one conflict.
- State changes are prepared on copies and installed only after a single private
  commit-point function returns. Injected failure before that swap leaves the
  active reservation, current predecessor, consumed set, and retained commit set
  unchanged.

All records remain experimental v0 prerelease records.

## Adversarial evidence

Focused tests cover successful commit, current-marking advancement, reservation
consumption, exact replay after source change, concurrent exact commits,
concurrent conflicting commits, source change before commit, and injected
failure immediately before the atomic state swap.

Validation from the uncommitted candidate on base Workflow revision `d4a8f11`:

- focused authority/admission/reservation/invocation/plan/firing/commit tests:
  `47 passed`;
- full Workflow suite: `367 passed`;
- standalone SDK suite: `13 passed`;
- strict mypy: no issues in `51` source files;
- Ruff, formatting of changed sources, architecture, runtime dependency,
  shadow-provenance, documentation-link, and diff checks: passed;
- atomic-commit source SHA-256:
  `c736d46a771ed2f5841f8f0875b7bf7c44e0211e259cd77dcf0a1e76371d41ff`;
- evolved reservation-repository source SHA-256:
  `6be6c916843c763cc3a422c74341c4ddc6ba59831806684b921e7af777620cec`;
- focused test source SHA-256:
  `2c9901a2f7bf752ae575cf6f76496bb66729456e856c8113f3ea616ce88ee504`;
- two Workflow wheels built with `SOURCE_DATE_EPOCH=315532800` were
  byte-identical, SHA-256
  `aed17dd8c8bb1d83d7ccafe6ce2c89fd7f1dde6f5a556b706e5bc13f228a72c6`.

Deterministic successful fixture identities:

- CPN-plan-bound reservation:
  `e187f49155f936daef44e5a22025a00e522aff689b9c39daff1b315ff2f64c7c`;
- pure CPN successor marking:
  `e01c016b26b52d70afbc7c7a481ed591e221f924ea45298243e3fc130f9ecf5f`;
- compact atomic commit:
  `b58cbaf0c02fabf51c9d635bfbc8d6ecbcec6c1358e7e09580eb2544cf40e626`;
- committed successor revision: `8`.

## Remaining gaps

The in-memory repository is non-durable and retains only the compact commit
identity and marking coordinates. A durable implementation must atomically
retain the canonical compact commit record and the separately admitted evidence
references needed for replay. It must not persist private inline owner payloads
or locators.

Source revalidation and predecessor commit are sequential operations across two
nominal repositories, not one distributed transaction. The commit binds the
exact previously authorized source observations and fails closed when they
change before commit, but a production owner source boundary must provide the
immutability/version guarantees needed to close the remaining observation race.

Canonical committed-event serialization, durable rollback/crash recovery,
complete evidence-reference retention, successor reconstruction, and committed
replay remain future work.
