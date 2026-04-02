"""Light platform for Tea Lights Infrared integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .commands import TeaLightCode
from .const import CONF_INFRARED_ENTITY_ID
from .entity import TeaLightIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tea Light IR light from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities([TeaLightIrLight(entry, infrared_entity_id)])


class TeaLightIrLight(TeaLightIrEntity, LightEntity):
    """IR-controlled tea light entity."""

    _attr_name = None
    _attr_assumed_state = True
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize tea light."""
        super().__init__(entry, infrared_entity_id, unique_id_suffix="light")
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the tea lights on."""
        await self._send_command(TeaLightCode.ON)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the tea lights off."""
        await self._send_command(TeaLightCode.OFF)
        self._attr_is_on = False
        self.async_write_ha_state()
