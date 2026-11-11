# SonosDial

![SonosDial logo](assets/sonosdial-128.png)

A small USB-powered rotary controller for Sonos. Turn to adjust volume; press
to control playback. Set up Wi-Fi and choose a room in the English/German Windows
assistant. The controller then works independently of your PC.

**Version 1.2.0 supports only the diymore ESP32-S3 Mini with 8 MB flash and 8 MB
PSRAM.** The large 16 MB DevKit board from v1 is no longer supported by this release.
No battery, external status LED, bridge, display or 3D-print files are required.

[Download releases](https://github.com/karlknall/SonosDial/releases) ·
[Test coverage](tests/README.md)

## Hardware

* diymore ESP32-S3 Mini: 8 MB flash, 8 MB PSRAM, one USB-C port, external U.FL antenna
* KY-040 rotary encoder with built-in push button
* USB data cable for setup; regulated 5 V USB supply rated at least 1 A for operation
* Five wires; attach the board's supplied Wi-Fi antenna before use

The advertised board measures about 21 × 18 mm. Antenna and wiring need extra
space. Similar-looking C3/C6/S3 boards are not automatically interchangeable.

## Wiring

Disconnect USB before wiring. Use the **GPIO number**, not the physical pin count.

| KY-040 terminal | Mini-board pin label | Physical GPIO |
|---|---|---|
| CLK | D3 / A3 | GPIO4 |
| DT | D4 / A4 / SDA | GPIO5 |
| SW | D5 / A5 / SCL | GPIO6 |
| + | 3V3 | 3.3 V supply |
| GND | GND | Ground |

**Never connect KY-040 + to 5 V.** Its pull-ups must use 3.3 V to protect the ESP
inputs. D4 means GPIO5 on this board. Check the seller's pinout if labels differ.
Do not connect anything to the battery pads for this USB-only version.

## Install and set up

1. Download **SonosDial-Setup-1.2.0-Windows.exe** from the release assets and run it.
2. Connect the mini board's USB-C port to your Windows PC with a data cable.
3. Follow the four steps: Connect → Install → Connect Wi-Fi → Choose a room.
4. Join your 2.4 GHz home Wi-Fi with a password or WPS, then select a Sonos room.
5. Keep USB power connected. A USB wall supply can replace the PC afterward.

The assistant contains firmware and flashing tools; end users do not need Python,
PlatformIO, a terminal or a browser. Firmware checksums, ESP32-S3 chip and exactly
8 MB flash are checked before writing. This does not prove a board's brand or
PSRAM size: use the specified hardware. The installer is **not digitally signed**.

If no serial port appears: hold BOOT, tap RESET, release BOOT, then Refresh.
The COM port can change after reset. Close other serial monitors.

## Controls

| Action | Result |
|---|---|
| Turn clockwise | Louder |
| Turn counterclockwise | Quieter |
| Press once | Play / pause |
| Press twice | Next track |
| Press three times | Previous track |
| Hold at least 2 seconds | No playback command; release is suppressed |

Presses are debounced for 25 ms. Leave less than about 350 ms between successive
clicks. Single/double actions wait for the multi-click window. Triple executes
on release. Skipping depends on the current Sonos source (for example radio may
not support Next/Previous).

New configurations use reversed encoder direction by default, matching the user's
tested mini/KY-040 wiring. Saved direction preferences are preserved on upgrade.
Other encoder batches can differ; change Reverse direction in More settings.
Default volume step is 2, adjustable 1–5; detent decoding supports 2 or 4 edges.

## Rooms and groups

Choose a fixed room, optionally control its current group's volume, or enable
Follow the music. Smart selection uses the single playing group; if ambiguous or
idle, it falls back to the selected room. Playback goes to the group coordinator.
The app does not create new Sonos groups. Discovery uses SSDP and local SOAP.
If multicast discovery fails, enter a Sonos IP in More settings. The controller
and Sonos must be reachable on the same home network, not an isolated guest WLAN.

Wi-Fi and room settings remain stored across power loss. USB setup is the main
route; a German local web fallback is also included. Hold the encoder button
while resetting to open setup mode. Normal long-hold gestures remain inactive.

## Upgrade from the mini test build

Install 1.2.0 and explicitly install its firmware on the mini. Existing compatible
SonosDial Wi-Fi, room, encoder and direction settings are preserved. The firmware
write excludes NVS. Do not erase flash if you want to keep those settings.
Old 16 MB board owners must keep the old v1 software; do not use this release.

## Test status and limits

The user reported the preceding mini firmware working and needing direction
reversal. Version 1.2.0 makes that the default for new setups and adds branding.
This report is not a claim that every Sonos model, WPS, groups or gesture was
individually tested on hardware. See tests/README.md.

## Privacy, source and licenses

No cloud account or telemetry is required by SonosDial. Wi-Fi credentials are
stored on the controller; this is a trusted-home-LAN project, not an Internet
service. Do not expose its web interface to the Internet. Wi-Fi credentials are stored on the controller without flash encryption; physical access can expose them.

Own firmware and logo: MIT. Combined Windows assistant: GPL-3.0-or-later.
Dependencies retain their original licenses; see LICENSE and THIRD-PARTY-NOTICES.md.
The **SonosDial-Source-1.2.0.zip release asset** supplies the complete corresponding
source, original notices and replaceable LGPL firmware link inputs. The installer
includes complete corresponding source as well. Keep source and licenses with redistributions.

The lean GitHub checkout excludes generated binaries and SDK link archives; it is
for development. Use the full release source asset for offline packaging/relinking.
See tools/README.md. SonosDial is an independent project, not affiliated with or
endorsed by Sonos. Sonos trademarks belong to their respective owners.
