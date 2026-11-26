"""Common entity for Tea Lights Infrared integration."""

from __future__ import annotations

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .commands import TeaLightCode, make_command
from .const import DOMAIN, SIGNAL_CODE_SENT


class TeaLightIrEntity(InfraredEmitterConsumerEntity):
    """Tea Light IR base entity.

    Availability is tracked against the underlying infrared emitter by the
    :class:`InfraredEmitterConsumerEntity` base class.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_emitter_entity_id: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize Tea Light IR entity."""
        self._entry_id = entry.entry_id
        self._infrared_emitter_entity_id = infrared_emitter_entity_id
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Tea Lights",
            manufacturer="Generic",
            model="IR Tea Light Candles",
        )

    async def _send_code(self, code: TeaLightCode) -> None:
        """Send an IR command to the tea lights via the emitter.

        Every entity of the entry is told about the sent code, so the light's
        assumed state follows the buttons as well as its own turn on/off.
        """
        await self._send_command(make_command(code))
        async_dispatcher_send(self.hass, SIGNAL_CODE_SENT.format(self._entry_id), code)
