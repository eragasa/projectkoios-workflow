import pytest

from _canonical_binding_fixtures import binding, canonical_binding
from projectkoios.workflow.petrinet.colored.canonical.bindings import (
    CpnCanonicalBinding,
    CpnCanonicalBindingCodec,
    CpnCanonicalBindingDecodingInput,
)
from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
    CpnCanonicalCodecErrorCode,
)


def test_decode__round_trips_exact_ordered_binding() -> None:
    result = CpnCanonicalBindingCodec().decode(
        CpnCanonicalBindingDecodingInput(canonical_binding())
    )
    assert result.binding == binding()


def test_decode__rejects_noncanonical_bytes() -> None:
    document = CpnCanonicalBinding(
        canonical_binding().canonical_bytes.replace(b'":', b'": ')
    )
    with pytest.raises(CpnCanonicalCodecError) as caught:
        CpnCanonicalBindingCodec().decode(
            CpnCanonicalBindingDecodingInput(document)
        )
    assert caught.value.code is CpnCanonicalCodecErrorCode.NONCANONICAL_BYTES
