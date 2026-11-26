"""Config flow for Tea Lights Infrared integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
)

from .const import CONF_INFRARED_EMITTER_ENTITY_ID, DOMAIN


class TeaLightsIrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for Tea Lights Infrared."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        errors: dict[str, str] = {}
        if user_input is not None:
            entity_id = user_input[CONF_INFRARED_EMITTER_ENTITY_ID]
            # An emitter entity_id can change; match on it only to prevent an
            # obvious duplicate rather than baking it into a unique_id.
            self._async_abort_entries_match(
                {CONF_INFRARED_EMITTER_ENTITY_ID: entity_id}
            )
            # The selector only offers emitters, but the one picked may have
            # gone away between showing the form and submitting it.
            if entity_id not in emitter_entity_ids:
                errors[CONF_INFRARED_EMITTER_ENTITY_ID] = "emitter_not_found"
            else:
                return self.async_create_entry(
                    title=f"Tea Lights via {self._async_emitter_name(entity_id)}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_INFRARED_EMITTER_ENTITY_ID): EntitySelector(
                        EntitySelectorConfig(
                            domain=INFRARED_DOMAIN,
                            include_entities=emitter_entity_ids,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    def _async_emitter_name(self, entity_id: str) -> str:
        """Return a display name for the emitter entity."""
        if (registry_entry := er.async_get(self.hass).async_get(entity_id)) is None:
            return entity_id
        return registry_entry.name or registry_entry.original_name or entity_id
