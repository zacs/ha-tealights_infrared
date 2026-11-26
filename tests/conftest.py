"""Fixtures for Tea Lights Infrared tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator

import pytest

from homeassistant.components.infrared import (
    InfraredCommand,
    InfraredEmitterEntity,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    MockPlatform,
    mock_config_flow,
    mock_integration,
    mock_platform,
)

from custom_components.tealights_infrared.const import (
    CONF_INFRARED_EMITTER_ENTITY_ID,
    DOMAIN,
)

EMITTER_DOMAIN = "test_ir"
EMITTER_ENTITY_ID = "infrared.test_emitter"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable loading custom integrations in all tests."""
    yield


class FakeEmitter(InfraredEmitterEntity):
    """Infrared emitter that records the commands it is asked to send."""

    _attr_name = "Test emitter"
    _attr_unique_id = "test_emitter"

    def __init__(self) -> None:
        """Initialize the fake emitter."""
        self.sent: list[InfraredCommand] = []

    async def async_send_command(self, command: InfraredCommand) -> None:
        """Record the command instead of transmitting it."""
        self.sent.append(command)


class _EmitterFlow(ConfigFlow):
    """Config flow placeholder for the mock emitter integration."""


@pytest.fixture
async def emitter(hass: HomeAssistant) -> AsyncGenerator[FakeEmitter]:
    """Set up a fake infrared emitter entity provided by a mock integration."""
    assert await async_setup_component(hass, "infrared", {})
    fake = FakeEmitter()

    async def _setup_platform(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
        async_add_entities([fake])

    async def _setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        await hass.config_entries.async_forward_entry_setups(entry, [Platform.INFRARED])
        return True

    mock_integration(hass, MockModule(EMITTER_DOMAIN, async_setup_entry=_setup_entry))
    mock_platform(hass, f"{EMITTER_DOMAIN}.config_flow")
    mock_platform(
        hass,
        f"{EMITTER_DOMAIN}.infrared",
        MockPlatform(async_setup_entry=_setup_platform),
    )
    with mock_config_flow(EMITTER_DOMAIN, _EmitterFlow):
        entry = MockConfigEntry(domain=EMITTER_DOMAIN)
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert fake.entity_id == EMITTER_ENTITY_ID
        yield fake


async def async_setup_tealights(hass: HomeAssistant) -> MockConfigEntry:
    """Set up a Tea Lights config entry bound to the fake emitter."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Tea Lights via Test emitter",
        data={CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.fixture
async def tealights_entry(hass: HomeAssistant, emitter: FakeEmitter) -> MockConfigEntry:
    """Set up a Tea Lights config entry bound to the fake emitter."""
    return await async_setup_tealights(hass)
