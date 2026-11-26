"""Light platform for Tea Lights Infrared integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import ExtraStoredData, RestoreEntity

from .commands import TeaLightCode
from .const import CONF_INFRARED_EMITTER_ENTITY_ID, SIGNAL_CODE_SENT
from .entity import TeaLightIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tea Light IR light from config entry."""
    infrared_emitter_entity_id = entry.data[CONF_INFRARED_EMITTER_ENTITY_ID]
    async_add_entities([TeaLightIrLight(entry, infrared_emitter_entity_id)])


@dataclass
class TeaLightExtraStoredData(ExtraStoredData):
    """Assumed on/off state, stored independently of entity availability."""

    is_on: bool

    def as_dict(self) -> dict[str, Any]:
        """Return a dict representation of the stored data."""
        return {"is_on": self.is_on}

    @classmethod
    def from_dict(cls, restored: dict[str, Any]) -> Self | None:
        """Initialize the stored data from a dict, or None if it is invalid."""
        is_on = restored.get("is_on")
        if not isinstance(is_on, bool):
            return None
        return cls(is_on)


class TeaLightIrLight(TeaLightIrEntity, LightEntity, RestoreEntity):
    """IR-controlled tea light entity.

    IR is one-way with no feedback, so the state is assumed: it reflects the
    last command sent for this entry (by the light or the buttons), restored
    across restarts, not the physical lights.
    """

    _attr_name = None
    _attr_assumed_state = True
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(
        self, entry: ConfigEntry, infrared_emitter_entity_id: str
    ) -> None:
        """Initialize tea light."""
        super().__init__(entry, infrared_emitter_entity_id, unique_id_suffix="light")
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Restore the last assumed state and follow codes sent for the entry."""
        await super().async_added_to_hass()
        self._attr_is_on = await self._async_restore_is_on()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_CODE_SENT.format(self._entry_id),
                self._async_code_sent,
            )
        )

    async def _async_restore_is_on(self) -> bool:
        """Return the assumed on/off state saved before the last shutdown.

        The saved entity state is "unavailable" whenever the emitter was
        unavailable at save time, so the on/off value is stored separately as
        extra data. States saved by older versions only have the entity state.
        """
        if (extra := await self.async_get_last_extra_data()) is not None and (
            data := TeaLightExtraStoredData.from_dict(extra.as_dict())
        ) is not None:
            return data.is_on
        if (last_state := await self.async_get_last_state()) is not None and (
            last_state.state in (STATE_ON, STATE_OFF)
        ):
            return last_state.state == STATE_ON
        return False

    @property
    def extra_restore_state_data(self) -> TeaLightExtraStoredData:
        """Return the assumed on/off state to store for the next restart."""
        return TeaLightExtraStoredData(bool(self._attr_is_on))

    @callback
    def _async_code_sent(self, code: TeaLightCode) -> None:
        """Update the assumed state after a code was sent for this entry."""
        self._attr_is_on = code is TeaLightCode.ON
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the tea lights on."""
        await self._send_code(TeaLightCode.ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the tea lights off."""
        await self._send_code(TeaLightCode.OFF)
