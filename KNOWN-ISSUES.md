# Known limitations — 1.0

- Reported working setup: Windows 11 Home, Sonos Five, FRITZ!Box 7590. No universal compatibility guarantee. WPS/group behavior was not separately confirmed on hardware.
- The installer is unsigned; Windows may display an unknown-publisher message. It does not change Windows security settings.
- The ESP32-S3 requires 2.4 GHz Wi-Fi. WPA-Enterprise is not supported. WPS requires router support; password setup remains available.
- Use native USB/OTG and a data cable for configuration. The COM port can change after reset/flash. Several connected boards may require manual selection.
- Sonos must be reachable locally. Guest networks, client isolation and VLAN rules can block discovery. An optional manual Sonos IP is available.
- Single/double clicks wait up to 350 ms for follow-up clicks. Some sources/services reject transport commands. Intelligent selection can be slower with many rooms.
- The assistant preserves the NVS area using segmented writes. The separate factory image can reset it; use the assistant for updates.
- The optional browser fallback remains German; the bilingual desktop interface does not require a browser. Raw diagnostics can remain in their original language.
- The web fallback uses local HTTP, no administrator login, and unencrypted NVS. Use a trusted LAN.
- There is no automatic updater, cloud account, telemetry or internet remote access. Uninstalling the PC assistant does not remove firmware already flashed to the board.
- A cleaned process environment is not a second clean Windows VM. No complete security or long-duration/load audit has been performed.

[Deutsch](docs/de/KNOWN-ISSUES.md)
