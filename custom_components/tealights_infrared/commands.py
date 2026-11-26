"""IR command definitions for tea light candles."""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import override

from homeassistant.components.infrared import InfraredCommand

# Tea light IR protocol timing values (in microseconds).
# Decoded from captured Tuya Zigbee IR blaster signals (FastLZ-compressed
# base64 -> uint16 little-endian mark/space pairs).
# The protocol uses simple pulse-width modulation:
#   - Short pulse: ~850us
#   - Long pulse: ~1700us
#   - Inter-frame gap: 65535us (max encodable, i.e. "idle until next frame")
_S = 850  # Short pulse duration (us)
_L = 1700  # Long pulse duration (us)
_GAP = 65535  # Inter-frame gap (us)

# Carrier frequency. Tuya codes store only mark/space timings, so the carrier
# is assumed to be the near-universal 38kHz.
_MODULATION_HZ = 38000

# Number of *extra* times each frame is repeated on top of the first
# transmission. The captured remote sends the ON frame twice and the OFF frame
# three times. ON/OFF are discrete (not toggle) codes, so re-sending a frame is
# idempotent -- raise these if the emitter is unreliable and commands are missed.
_ON_REPEATS = 1
_OFF_REPEATS = 2

# Single frame of the ON command as (mark, space) pairs, ending with the
# inter-frame gap.
_ON_FRAME: tuple[tuple[int, int], ...] = (
    (_S, _S),
    (_L, _L),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_L, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _L),
    (_S, _GAP),
)

# Single frame of the OFF command as (mark, space) pairs, ending with the
# inter-frame gap.
_OFF_FRAME: tuple[tuple[int, int], ...] = (
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_S, _S),
    (_L, _S),
    (_S, _L),
    (_L, _S),
    (_S, _S),
    (_S, _GAP),
)


class RawCommand(InfraredCommand):
    """IR command built from raw (mark, space) pairs.

    The infrared platform's emitters transmit the list returned by
    ``get_raw_timings`` exactly once, as signed microseconds: positive values
    are marks (carrier on), negative values are spaces (carrier off). Repeats
    are therefore baked into that list rather than left to the emitter.
    """

    def __init__(
        self,
        *,
        frame: Sequence[tuple[int, int]],
        modulation: int = _MODULATION_HZ,
        repeat_count: int = 0,
    ) -> None:
        """Initialize raw IR command."""
        super().__init__(modulation=modulation, repeat_count=repeat_count)
        self._frame = [t for mark, space in frame for t in (mark, -space)]

    @override
    def get_raw_timings(self) -> list[int]:
        """Return the frame timings repeated ``repeat_count`` extra times."""
        return self._frame * (self.repeat_count + 1)


class TeaLightCode(StrEnum):
    """Tea light IR command codes."""

    ON = "on"
    OFF = "off"


def make_command(code: TeaLightCode) -> InfraredCommand:
    """Create an IR command for a tea light action."""
    if code is TeaLightCode.ON:
        return RawCommand(frame=_ON_FRAME, repeat_count=_ON_REPEATS)
    return RawCommand(frame=_OFF_FRAME, repeat_count=_OFF_REPEATS)
