"""Direct tests for strict canonical control-record transport."""

import pytest

from projectkoios.workflow.petrinet.colored.canonical.json import (
    CpnCanonicalCodecError,
)
from projectkoios.workflow.petrinet.colored.control.records.canonical import (
    CpnCanonicalControlRecord,
    CpnControlRecordCanonicalCodec,
    CpnControlRecordCanonicalDecodingInput,
    CpnControlRecordCanonicalEncodingInput,
)

from _control_record_fixtures import record, record_types


def document(raw: bytes) -> CpnCanonicalControlRecord:
    """Correlate arbitrary adversarial bytes so parsing is reached."""
    return CpnCanonicalControlRecord(raw)


def test_encode_decode__round_trips_exact_bytes_and_record() -> None:
    """Decode reconstructs and byte-for-byte re-encodes the exact record."""
    codec = CpnControlRecordCanonicalCodec()
    encoded = codec.encode(
        CpnControlRecordCanonicalEncodingInput(record(), record_types())
    )
    decoded = codec.decode(
        CpnControlRecordCanonicalDecodingInput(encoded, record_types())
    )
    assert decoded.record == record()
    assert (
        codec.encode(
            CpnControlRecordCanonicalEncodingInput(
                decoded.record, record_types()
            )
        )
        == encoded
    )


@pytest.mark.parametrize(
    "raw",
    [
        b'{"profile":"x","profile":"x","record":null}',
        b'{"profile":"x","record":1}',
        b'{"profile":"x","record":NaN}',
        b'{"profile":"x","record":"\\ud800"}',
        b'{"profile":"x","record":' + b"9" * 5000 + b"}",
    ],
)
def test_decode__translates_adversarial_json_without_runtime_leaks(
    raw: bytes,
) -> None:
    """Duplicate, numeric, nonfinite, surrogate, and huge-number inputs close."""
    with pytest.raises(CpnCanonicalCodecError):
        CpnControlRecordCanonicalCodec().decode(
            CpnControlRecordCanonicalDecodingInput(
                document(raw), record_types()
            )
        )
