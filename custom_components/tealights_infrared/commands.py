"""IR command definitions for tea light candles."""

from __future__ import annotations

from enum import StrEnum

from infrared_protocols import Command, Timing

# Tea light IR protocol timing values (in microseconds).
# Decoded from captured Tuya Zigbee IR blaster signals.
# The protocol uses simple pulse-width modulation:
#   - Short pulse: ~850us
#   - Long pulse: ~1700us
#   - Inter-frame gap: 65535us
_S = 850  # Short pulse duration (us)
_L = 1700  # Long pulse duration (us)
_GAP = 65535  # Inter-frame gap (us)

# Carrier frequency (standard IR)
_MODULATION_HZ = 38000

# Single frame timings for ON command
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

# Single frame timings for OFF command
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
    """IR command from raw timing data."""

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
        """Return raw mark/space timings."""
        return list(self._timings)


class TeaLightCode(StrEnum):
    """Tea light IR command codes."""

    ON = "on"
    OFF = "off"


def make_command(code: TeaLightCode) -> Command:
    """Create an IR command for a tea light action."""
    if code == TeaLightCode.ON:
        return RawCommand(
            timings=_ON_FRAME,
            modulation=_MODULATION_HZ,
            repeat_count=1,  # Original signal sends 2 frames
        )
    return RawCommand(
        timings=_OFF_FRAME,
        modulation=_MODULATION_HZ,
        repeat_count=2,  # Original signal sends 3 frames
    )
