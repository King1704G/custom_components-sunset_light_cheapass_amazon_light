# HA Sunset Light Hack

This repository contains a Home Assistant custom component to control a Bluetooth-based sunset light (MeRGBW).

## Protocol profiles

The light control protocol is abstracted behind profiles. The default "Sunset Light" profile matches the original device. A "Hexagon Light" profile is also available (hue/saturation payloads, extended scenes); choose the profile during config flow.

## Installation

1.  Copy the `custom_components/sunset_light` directory to the `custom_components` directory of your Home Assistant configuration.
2.  Restart Home Assistant.

## Configuration

1.  Go to **Settings** -> **Devices & Services**.
2.  Click the **+ Add Integration** button.
3.  Search for "Sunset Light" and select it.
4.  Enter the MAC address of your sunset light and click **Submit**.

## Lovelace Dashboard & Automation Setup

To fully control the light (including Scenes and White mode), you need to add some configurations to your Home Assistant.

### 1. Scene Selector (Helper + Automation)

**Step 1.1: Create a Dropdown Helper**
Add this to your `configuration.yaml` or create a "Dropdown" helper via the UI (Settings > Devices & Services > Helpers):

```yaml
input_select:
  sunset_light_scene_selector:
    name: Sunset Light Scene
    options:
      - Fantasy
      - Sunset
      - Forest
      - Ghost
      - Sunrise
      - Midsummer
      - Tropicaltwilight
      - Green Prairie
      - Rubyglow
      - Aurora
      - Savanah
      - Alarm
      - Lake Placid
      - Neon
      - Sundowner
      - Bluestar
      - Redrose
    initial: Fantasy
    icon: mdi:palette-outline
```

**Step 1.2: Create an Automation**
This automation listens to the dropdown and changes the light scene.

```yaml
alias: Sunset Light - Set Scene
description: Triggers the custom set_scene service when input_select changes
trigger:
  - platform: state
    entity_id: input_select.sunset_light_scene_selector
condition: []
action:
  - service: light.set_scene
    data:
      entity_id: light.sunset_light  # CHANGE THIS to your actual entity ID
      scene_name: "{{ states('input_select.sunset_light_scene_selector') | lower }}"
mode: single
```

### 2. Dashboard Cards (Lovelace)

Add these cards to your dashboard to control the light.

**Basic Control:**
```yaml
type: light
entity: light.sunset_light
name: Sunset Light
features:
  - brightness
  - color_picker
```

**Scene Selector:**
```yaml
type: entities
entities:
  - entity: input_select.sunset_light_scene_selector
    name: Select Scene
```

**White Mode Button:**
```yaml
type: button
name: Set White Light
icon: mdi:lightbulb-on
tap_action:
  action: call-service
  service: light.set_white
  service_data:
    entity_id: light.sunset_light # CHANGE THIS to your actual entity ID
```

## Protocol Details

The `control.py` script contains the logic for controlling the light via Bluetooth LE.

### Bluetooth Protocol

*   **Service UUID:** `0000fff0-0000-1000-8000-00805f9b34fb`
*   **Write Characteristic UUID:** `0000fff4-0000-1000-8000-00805f9b34fb`
*   **Command Structure:** `0x56` + `cmdCode` + `0xff` + `length` + `value` + `checksum`

### Commands

*   **Power On:** `cmdCode 0x01` (Payload: `FF0600EB`)
*   **Power Off:** `cmdCode 0x00` (Payload: `FF0F0064...`)
*   **White Mode:** `cmdCode 0x00` (Payload: `FF0F0164...`)
*   **Set Color:** `cmdCode 0x03`
*   **Set Brightness:** `cmdCode 0x05`
*   **Set Scene:** `cmdCode 0x06` (and some `0x03`)
