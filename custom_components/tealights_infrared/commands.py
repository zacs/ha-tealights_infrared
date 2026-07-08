"""IR command definitions for tea light candles."""

from __future__ import annotations

from enum import StrEnum

from infrared_protocols import Command, Timing

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

# Single frame timings for the ON command (one frame, trailing inter-frame gap).
_ON_FRAME: list[Timing] = [
    Timing(_S, _S),
    Timing(_L, _L),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_L, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _L),
    Timing(_S, _GAP),
]

# Single frame timings for the OFF command (one frame, trailing inter-frame gap).
_OFF_FRAME: list[Timing] = [
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_S, _S),
    Timing(_L, _S),
    Timing(_S, _L),
    Timing(_L, _S),
    Timing(_S, _S),
    Timing(_S, _GAP),
]


class RawCommand(Command):
    """IR command built from raw mark/space timings.

    infrared_protocols commands bake their repeats directly into the timings
    returned by ``get_raw_timings`` (the emitter transmits that list once), so
    this command expands ``repeat_count`` into repeated copies of the frame
    rather than relying on the emitter to replay it.
    """

    def __init__(
        self,
        *,
        timings: list[Timing],
        modulation: int = _MODULATION_HZ,
        repeat_count: int = 0,
    ) -> None:
        """Initialize raw IR command."""
        super().__init__(modulation=modulation, repeat_count=repeat_count)
        self._timings = timings

    def get_raw_timings(self) -> list[Timing]:
        """Return the frame timings repeated ``repeat_count`` extra times."""
        return list(self._timings) * (self.repeat_count + 1)


class TeaLightCode(StrEnum):
    """Tea light IR command codes."""

    ON = "on"
    OFF = "off"


def make_command(code: TeaLightCode) -> Command:
    """Create an IR command for a tea light action."""
    if code == TeaLightCode.ON:
        return RawCommand(timings=_ON_FRAME, repeat_count=_ON_REPEATS)
    return RawCommand(timings=_OFF_FRAME, repeat_count=_OFF_REPEATS)
