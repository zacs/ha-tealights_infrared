"""Button platform for Tea Lights Infrared integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .commands import TeaLightCode
from .const import CONF_INFRARED_EMITTER_ENTITY_ID
from .entity import TeaLightIrEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class TeaLightButtonDescription(ButtonEntityDescription):
    """Describes a tea light IR button entity."""

    command_code: TeaLightCode


BUTTON_DESCRIPTIONS: tuple[TeaLightButtonDescription, ...] = (
    TeaLightButtonDescription(
        key="power_on",
        translation_key="power_on",
        command_code=TeaLightCode.ON,
    ),
    TeaLightButtonDescription(
        key="power_off",
        translation_key="power_off",
        command_code=TeaLightCode.OFF,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tea Light IR buttons from config entry."""
    infrared_emitter_entity_id = entry.data[CONF_INFRARED_EMITTER_ENTITY_ID]
    async_add_entities(
        TeaLightIrButton(entry, infrared_emitter_entity_id, description)
        for description in BUTTON_DESCRIPTIONS
    )


class TeaLightIrButton(TeaLightIrEntity, ButtonEntity):
    """Tea light IR button entity."""

    entity_description: TeaLightButtonDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_emitter_entity_id: str,
        description: TeaLightButtonDescription,
    ) -> None:
        """Initialize tea light IR button."""
        super().__init__(
            entry, infrared_emitter_entity_id, unique_id_suffix=description.key
        )
        self.entity_description = description

    async def async_press(self) -> None:
        """Press the button."""
        await self._send_code(self.entity_description.command_code)
