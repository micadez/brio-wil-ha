# CCEI BRiO WiL

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Home Assistant integration for **CCEI BRiO WiL** pool lighting.

Control your pool lights directly from Home Assistant via local TCP communication — no cloud required.

## Features

- Turn lights on/off
- Adjust brightness
- Select light effects (colors and animations)
- Control animation speed
- Local polling with configurable intervals

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** > **Custom repositories**
3. Add `https://github.com/micadez/brio-wil-ha` as an **Integration**
4. Search for "CCEI BRiO WiL" and install

### Manual

Copy the `custom_components/brio_wil` folder to your Home Assistant `custom_components` directory.

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for "CCEI BRiO WiL"
3. Enter the IP address of your BRiO WiL device
4. Optionally adjust poll and retry intervals in the integration options
