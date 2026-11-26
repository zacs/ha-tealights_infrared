"""Constants for the Tea Lights Infrared integration."""

DOMAIN = "tealights_infrared"
CONF_INFRARED_EMITTER_ENTITY_ID = "infrared_emitter_entity_id"

# Dispatcher signal sent after a code has been transmitted for a config entry,
# formatted with the entry ID. The payload is the TeaLightCode that was sent.
SIGNAL_CODE_SENT = f"{DOMAIN}_code_sent_{{}}"
