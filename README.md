# Tea Lights Infrared

A Home Assistant custom component for controlling IR tea light candles via the [Infrared](https://www.home-assistant.io/integrations/infrared/) platform.

## Overview

This integration sends infrared on/off commands to battery-powered IR tea light candles through any Home Assistant infrared transmitter entity. It is built on the HA Infrared entity platform, which provides a hardware-agnostic abstraction layer for IR transmission.

## Requirements

- Home Assistant with the `infrared` platform available (2025.x+)
- An infrared transmitter integration registered as an IR emitter entity (e.g., a Broadlink, ESPHome, or other IR blaster with infrared platform support)

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| Tea Lights | `light` | On/off control with assumed state |
| Turn on | `button` | Send the IR on command |
| Turn off | `button` | Send the IR off command |

## State tracking

IR is a one-way protocol with no feedback channel. The light entity uses **assumed state** -- it tracks what it last sent, not what the tea lights are actually doing. If a command fails to reach the tea lights (out of range, blocked, etc.), the HA state will be wrong. The button entities are stateless.

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
