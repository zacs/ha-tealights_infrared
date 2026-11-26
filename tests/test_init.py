"""Tests for Tea Lights Infrared setup, entities and IR output."""

from __future__ import annotations

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    ATTR_ASSUMED_STATE,
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tealights_infrared.commands import TeaLightCode, make_command

from .conftest import FakeEmitter

LIGHT_ENTITY_ID = "light.tea_lights"
BUTTON_ON_ENTITY_ID = "button.tea_lights_turn_on"
BUTTON_OFF_ENTITY_ID = "button.tea_lights_turn_off"

S, L, GAP = 850, 1700, 65535

ON_FRAME = [
    S, -S, L, -L, S, -S, S, -S, S, -S, S, -S,
    L, -S, S, -S, S, -S, S, -S, S, -L, S, -GAP,
]  # fmt: skip
OFF_FRAME = [
    S, -S, S, -S, S, -S, S, -S, S, -S, S, -S,
    S, -S, L, -S, S, -L, L, -S, S, -S, S, -GAP,
]  # fmt: skip


def test_command_timings() -> None:
    """Commands emit signed mark/space timings with repeats baked in."""
    on = make_command(TeaLightCode.ON)
    assert on.modulation == 38000
    assert on.get_raw_timings() == ON_FRAME * 2

    off = make_command(TeaLightCode.OFF)
    assert off.modulation == 38000
    assert off.get_raw_timings() == OFF_FRAME * 3


async def test_setup_and_unload(
    hass: HomeAssistant, tealights_entry: MockConfigEntry
) -> None:
    """The entry loads its light and buttons, and unloads cleanly."""
    assert tealights_entry.state is ConfigEntryState.LOADED
    state = hass.states.get(LIGHT_ENTITY_ID)
    assert state is not None
    assert state.state == STATE_OFF
    assert state.attributes[ATTR_ASSUMED_STATE] is True
    assert hass.states.get(BUTTON_ON_ENTITY_ID) is not None
    assert hass.states.get(BUTTON_OFF_ENTITY_ID) is not None

    assert await hass.config_entries.async_unload(tealights_entry.entry_id)
    await hass.async_block_till_done()
    assert tealights_entry.state is ConfigEntryState.NOT_LOADED


async def test_light_sends_ir(
    hass: HomeAssistant, emitter: FakeEmitter, tealights_entry: MockConfigEntry
) -> None:
    """Turning the light on and off sends the matching IR code."""
    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: LIGHT_ENTITY_ID}, blocking=True
    )
    assert hass.states.get(LIGHT_ENTITY_ID).state == STATE_ON
    assert len(emitter.sent) == 1
    assert emitter.sent[0].get_raw_timings() == ON_FRAME * 2

    await hass.services.async_call(
        LIGHT_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: LIGHT_ENTITY_ID}, blocking=True
    )
    assert hass.states.get(LIGHT_ENTITY_ID).state == STATE_OFF
    assert len(emitter.sent) == 2
    assert emitter.sent[1].get_raw_timings() == OFF_FRAME * 3


async def test_buttons_send_ir(
    hass: HomeAssistant, emitter: FakeEmitter, tealights_entry: MockConfigEntry
) -> None:
    """The on/off buttons send the matching IR code."""
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: BUTTON_ON_ENTITY_ID},
        blocking=True,
    )
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: BUTTON_OFF_ENTITY_ID},
        blocking=True,
    )
    assert [cmd.get_raw_timings() for cmd in emitter.sent] == [
        ON_FRAME * 2,
        OFF_FRAME * 3,
    ]


async def test_follows_emitter_availability(
    hass: HomeAssistant, emitter: FakeEmitter, tealights_entry: MockConfigEntry
) -> None:
    """Entities go unavailable with the emitter and come back with it."""
    emitter._attr_available = False
    emitter.async_write_ha_state()
    await hass.async_block_till_done()
    assert hass.states.get(LIGHT_ENTITY_ID).state == STATE_UNAVAILABLE
    assert hass.states.get(BUTTON_ON_ENTITY_ID).state == STATE_UNAVAILABLE

    emitter._attr_available = True
    emitter.async_write_ha_state()
    await hass.async_block_till_done()
    assert hass.states.get(LIGHT_ENTITY_ID).state == STATE_OFF
