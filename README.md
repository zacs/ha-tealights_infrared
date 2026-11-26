# Tea Lights Infrared

[![Validate](https://github.com/zacs/ha-tealights_infrared/actions/workflows/validate.yaml/badge.svg)](https://github.com/zacs/ha-tealights_infrared/actions/workflows/validate.yaml)
[![hacs](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom component for controlling IR tea light candles via the [Infrared](https://www.home-assistant.io/integrations/infrared/) platform.

## Overview

This integration sends infrared on/off commands to battery-powered IR tea light candles through any Home Assistant infrared transmitter entity. It is built on the HA Infrared entity platform, which provides a hardware-agnostic abstraction layer for IR transmission.

## Requirements

- Home Assistant 2026.6 or later (for the `infrared` platform and its `InfraredEmitterConsumerEntity` API)
- An infrared transmitter integration registered as an IR emitter entity (e.g., a Broadlink, ESPHome, or other IR blaster with infrared platform support)

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| Tea Lights | `light` | On/off control with assumed state |
| Turn on | `button` | Send the IR on command |
| Turn off | `button` | Send the IR off command |

## State tracking

IR is a one-way protocol with no feedback channel. The light entity uses **assumed state** -- it tracks the last code sent, not what the tea lights are actually doing. That includes codes sent by the Turn on / Turn off buttons, and the state is restored across restarts (even if the transmitter was unavailable when Home Assistant shut down). If a command fails to reach the tea lights (out of range, blocked, etc.), the HA state will be wrong; sending the code again fixes it. Because state is assumed, the frontend shows discrete on/off controls rather than a single toggle.

The entities are built on the `InfraredEmitterConsumerEntity` base class, so they are automatically marked unavailable when the underlying infrared transmitter is unavailable. If you rename the transmitter's entity ID, the integration follows it automatically.

## Installation

### HACS

Add this repository as a custom repository in HACS, then install "Tea Lights Infrared."

### Manual

Copy the `custom_components/tealights_infrared` directory into your Home Assistant `custom_components/` folder and restart.

## Configuration

1. Go to Settings > Devices & Services > Add Integration
2. Search for "Tea Lights Infrared"
3. Select your infrared transmitter entity

## IR codes

The bundled IR codes were captured from a set of generic battery-powered IR tea light candles. The protocol uses pulse-width modulation at 38kHz with ~850us/~1700us timing. If your tea lights use different codes, you will need to modify `commands.py`.

On and off are discrete codes (not a single toggle), so re-sending a code is idempotent. If your transmitter is unreliable and commands are occasionally missed, increase `_ON_REPEATS` / `_OFF_REPEATS` in `commands.py`.

## Development

Tests run against a real Home Assistant core with a fake infrared emitter, via [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component). They need Python 3.14:

```bash
pip install pytest-homeassistant-custom-component infrared-protocols
pytest
```
