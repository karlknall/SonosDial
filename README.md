# SonosDial 1.0

An independent, local Sonos volume controller for an **ESP32-S3 DevKitC-1 N16R8** and a **KY-040 rotary encoder**. No display or battery. Software only: no CAD or STL files.

English is the main publication language. [Deutsche Anleitung](docs/de/README.md). The Windows installer and setup assistant support **English and German**. The assistant uses a saved language preference first, otherwise the Windows UI language; other Windows languages fall back to English. Change it anytime using **Language / Sprache** in the sidebar. An explicit `--lang en` or `--lang de` overrides detection for that launch.

## Quick start

1. Run **SonosDial-Setup-1.0-Windows.exe** and launch SonosDial. No separate Python installation, browser or internet connection is required for setup. The installer is unsigned.
2. Connect the board using a **USB data cable** and its native **USB / OTG** port. If there are two sockets, follow the actual board labels rather than the schematic illustration; avoid UART for USB configuration.
3. Select the board and install firmware 1.0. Checksums, the ESP32-S3 chip and 16 MB flash are checked before writing. Existing SonosDial settings are preserved by writing separate firmware areas and leaving NVS untouched.
4. Choose your **2.4 GHz Wi-Fi** and enter its password, or start WPS in the assistant and press the WPS button on your router. The computer stays on its normal network; configuration travels over USB.
5. Select a Sonos room and save. The final page explains the controls. You can then power the controller from a suitable 5 V USB adapter.

If flashing fails: hold BOOT, briefly press RESET, then release BOOT. Refresh the USB port and retry. The port may change after reset. Once firmware 1.0 is detected, settings can be changed without flashing again.

## Wiring

**Disconnect USB before wiring. Connect KY-040 power to 3V3, never 5V.** Use GPIO labels, not counted connector positions on a clone board.

| KY-040 | ESP32-S3 |
|---|---|
| CLK | GPIO4 / 4 |
| DT | GPIO5 / 5 |
| SW | GPIO6 / 6 |
| + | 3V3 |
| GND | GND / G |

The push button is already built into the KY-040. USB powers both components. These GPIOs follow the [Espressif reference pinout](https://docs.espressif.com/projects/esp-idf/en/v4.4.8/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html). No cable connects the ESP32 to Sonos; they communicate through your reachable home LAN.

## Controls

| Gesture | Action |
|---|---|
| Turn right | Volume up |
| Turn left | Volume down |
| Press once | Play/pause |
| Press twice | Next track |
| Press three times | Previous track |
| Hold for 2 seconds | Mute/unmute |

Single and double clicks wait up to 350 ms after the last release for another click. Holding triggers once and does not also trigger a click on release. Unknown playback states do not result in a guessed command. Radio, TV, AirPlay and some music services may reject track changes or pause.

## Rooms, groups and settings

The fixed room is saved by UUID. **Follow the music** selects the only group currently playing; when several groups or none are playing, the fixed room is used. If no valid room is available, no arbitrary group is selected.

Existing Sonos groups are controlled through their coordinator. Volume/mute may apply to the whole group or the chosen room; transport commands always target the coordinator. This firmware does not create or split groups. Invisible stereo/home-theater satellites are not offered as individual rooms.

**More settings** contains rotation direction, volume step (1–5), encoder transitions per detent (2 or 4) and an optional Sonos IP address. Settings apply without rebooting and remain on the device after power is removed. New Wi-Fi credentials are saved only after a confirmed connection. A failed attempt restores the previously saved connection. Changing to a different Wi-Fi network clears the room/IP selection so it can be chosen again.

The encoder is read in its own task. Network delays do not block sampling. Pending turns and button actions are bounded; old commands are discarded rather than replayed after an outage. Ambiguous next/relative-volume results are not retried automatically. Intelligent selection needs extra LAN requests and can be slower in large households.

## Language and optional web fallback

The assistant UI, setup help and known firmware error messages are localized on the PC. SSIDs, passwords and Sonos room names are never translated. Only the UI language is stored on the PC; Wi-Fi credentials remain on the ESP32. Raw diagnostic logs may retain their original language.

The optional local page at `http://sonosdial.local` remains **German** in firmware 1.0. It is not needed for normal USB setup. This localization update deliberately leaves the working firmware byte-for-byte unchanged, so the controller does not need reflashing. The page uses local HTTP and a form token, not an administrator login; NVS is not encrypted. Use a trusted home network. Guest-network/client-isolation/VLAN rules can prevent discovery.

For updates use the assistant. The separate factory image written at address zero can clear NVS because it includes gaps; the assistant instead writes at 0 / 0x8000 / 0xe000 / 0x10000 and skips the NVS area at 0x9000–0xdfff.

## Tested setup and limits

The user reported “works” on **Windows 11 Home, Sonos Five and FRITZ!Box 7590**. WPS, groups and individual gesture cases were not separately confirmed as hardware tests. Windows 10 is a target, not an independently confirmed test setup. See [hardware tests](HARDWARE-TESTS.md), [known issues](KNOWN-ISSUES.md) and [test report](TESTPROTOKOLL.md).

The bilingual package includes 20 Python tests, native firmware logic tests, packaged/installed self-tests and a byte-identical firmware relink test. A cleaned process environment is not a fresh Windows VM. No security audit or universal compatibility claim is made.

## Source, licensing and publication

Desktop assistant: **GPL-3.0-or-later**. Own firmware application: **MIT**. Dependencies retain their original licenses. Full original license texts are preserved under `licenses`; no legal text is translated or replaced. See [LICENSE](LICENSE), [third-party notices](THIRD-PARTY-NOTICES.md) and [build instructions](BUILDING.md).

The installer includes its complete companion source archive, including upstream GPL sources and LGPL object files, libraries and source for replacement/relinking. Distribute the installer, source archive and checksum file together. This package was prepared locally; nothing has been uploaded.
