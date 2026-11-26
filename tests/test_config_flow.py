"""Tests for the Tea Lights Infrared config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component

from custom_components.tealights_infrared.const import (
    CONF_INFRARED_EMITTER_ENTITY_ID,
    DOMAIN,
)

from .conftest import EMITTER_ENTITY_ID, FakeEmitter


async def test_user_flow(hass: HomeAssistant, emitter: FakeEmitter) -> None:
    """Picking an emitter creates an entry, and picking it again aborts."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tea Lights via Test emitter"
    assert result["data"] == {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_no_emitters(hass: HomeAssistant) -> None:
    """The flow aborts when there is no infrared emitter."""
    assert await async_setup_component(hass, "infrared", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


async def test_emitter_gone_before_submit(
    hass: HomeAssistant, emitter: FakeEmitter
) -> None:
    """An emitter that disappears after the form is shown is rejected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(
        "custom_components.tealights_infrared.config_flow.async_get_emitters",
        return_value=["infrared.other_emitter"],
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_INFRARED_EMITTER_ENTITY_ID: EMITTER_ENTITY_ID}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_INFRARED_EMITTER_ENTITY_ID: "emitter_not_found"}
