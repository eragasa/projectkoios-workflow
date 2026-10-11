r"""Software verification of ``CpnPlaceMarking``.

Evidence profile: routine

Bounded artifact scope: the tuple-backed semantic token multiset at one generic place.

Facet and represented meaning

The class represents marking-owned multiplicity and deterministic in-memory token
ordering for one nominal place.

Intrinsic and cross-object scope

Anonymous repetition, identified-token uniqueness, canonical order, nominal types,
and immutability are intrinsic. Definition completeness is excluded.

VVUQ and scientific exclusions

These synthetic checks establish software multiset behavior only, not numerical
verification, scientific validation, uncertainty quantification, or simulation results.
"""

from dataclasses import FrozenInstanceError

import pytest

from projectkoios.workflow.petrinet.colored.definitions import CpnPlaceIdentity
from projectkoios.workflow.petrinet.colored.markings import CpnPlaceMarking
from projectkoios.workflow.petrinet.colored.values import (
    CpnColorIdentity,
    CpnToken,
    CpnTokenIdentity,
    CpnValue,
    CpnValueKind,
)

pytestmark = pytest.mark.software_verification

SUT = CpnPlaceMarking


def make_token(label: str, identity: str | None = None) -> CpnToken:
    """Evidence ID: Owns no identifier; supports place-marking evidence.

    Requirement: Tests need explicit synthetic tokens with chosen values and identity.

    Acceptance: The helper returns the corresponding public token.
    """
    return CpnToken(
        CpnColorIdentity("color"),
        CpnValue(CpnValueKind.STRING, label),
        None if identity is None else CpnTokenIdentity(identity),
    )


def test_constructor__multiset__preserves_anonymous_multiplicity_and_order() -> (
    None
):
    """Evidence ID: SV-PETRINET-026

    Requirement: Repeated equal anonymous tokens remain present while representation
    order is canonical and caller-order independent.

    Acceptance: Two equal anonymous tokens are retained and reversed constructions
    of unequal tokens produce equal canonical state.
    """
    place = CpnPlaceIdentity("ready")
    anonymous = make_token("a")
    first = SUT(place, (make_token("b"), anonymous, anonymous))
    second = SUT(place, (anonymous, make_token("b"), anonymous))
    assert first == second
    assert first.tokens == (anonymous, anonymous, make_token("b"))


def test_constructor__canonical_order__covers_every_token_key_dimension() -> (
    None
):
    """Evidence ID: SV-PETRINET-038

    Requirement: Canonical token order covers color, value kind/value, anonymity,
    and nominal token identity independently of caller order.

    Acceptance: Reverse construction stores the exact hand-ordered sequence spanning
    every ordering-key dimension.
    """
    color_a = CpnColorIdentity("a")
    color_z = CpnColorIdentity("z")
    integer = CpnValue(CpnValueKind.INTEGER, 1)
    none = CpnValue(CpnValueKind.NONE, None)
    string_a = CpnValue(CpnValueKind.STRING, "a")
    string_b = CpnValue(CpnValueKind.STRING, "b")
    ordered = (
        CpnToken(color_a, string_b),
        CpnToken(color_z, integer),
        CpnToken(color_z, none),
        CpnToken(color_z, string_a),
        CpnToken(color_z, string_a, CpnTokenIdentity("a")),
        CpnToken(color_z, string_a, CpnTokenIdentity("b")),
        CpnToken(color_z, string_b),
    )
    place = SUT(CpnPlaceIdentity("ready"), tuple(reversed(ordered)))
    assert place.tokens == ordered


def test_constructor__immutability__produces_frozen_record() -> None:
    """Evidence ID: SV-PETRINET-039

    Requirement: A place marking is operationally immutable.

    Acceptance: Assigning its token tuple raises ``FrozenInstanceError``.
    """
    place = SUT(CpnPlaceIdentity("ready"), ())
    with pytest.raises(FrozenInstanceError):
        place.tokens = ()  # type: ignore[misc]


def test_constructor__identified_tokens__rejects_duplicate_identity() -> None:
    """Evidence ID: SV-PETRINET-027

    Requirement: One individually correlated token identity cannot occur twice at a
    place, even with different carried values.

    Acceptance: Repeated equal and conflicting uses of one identity raise
    ``ValueError`` exactly.
    """
    place = CpnPlaceIdentity("ready")
    with pytest.raises(ValueError):
        SUT(place, (make_token("a", "token"), make_token("a", "token")))
    with pytest.raises(ValueError):
        SUT(place, (make_token("a", "token"), make_token("b", "token")))


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(("ready", ()), id="lexical_place_identity"),
        pytest.param(
            (CpnPlaceIdentity("ready"), []),
            id="mutable_token_collection",
        ),
        pytest.param(
            (CpnPlaceIdentity("ready"), ("token",)),
            id="non_token_member",
        ),
    ],
)
def test_constructor__nominal_types__rejects_wrong_types(
    arguments: tuple[object, object],
) -> None:
    """Evidence ID: SV-PETRINET-028

    Requirement: Place markings accept exact nominal identities and immutable token
    tuples only.

    Acceptance: Every named wrong-type partition raises ``TypeError`` exactly.
    """
    with pytest.raises(TypeError):
        SUT(*arguments)  # type: ignore[arg-type]
