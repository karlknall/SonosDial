# Tests and limitations — 1.2.0

Automated checks passed: firmware compilation for ESP32-S3 Mini/8 MB flash,
five native C++ suites, 25 Python tests, bilingual packaged application self-test,
and byte-identical firmware relinking from the supplied LGPL replacement kit.
An isolated Windows installation, installed self-test without Python on PATH,
source-manifest verification and uninstallation passed. Logo/layout were inspected.

The user reported the preceding mini firmware working after reversing encoder
direction. New setups now default to that direction; saved choices are preserved.
The exact 1.2.0 binary still needs physical confirmation. WPS, groups and each
gesture were not individually confirmed by the user's report. Automated tests do
not simulate a complete ESP32/Sonos system. No clean Windows VM test or remote
GitHub workflow run is claimed. Installer is unsigned.

Before calling all features hardware-verified, check installation and USB reset,
actual 8 MB PSRAM, saved settings after reboot, clockwise volume increase, all
three click gestures, ignored >2s hold, room/group selection and network recovery.
Encoder batches can differ: direction and 2/4 edges per detent remain adjustable.
Track skipping depends on the Sonos source. Discovery needs a reachable home LAN;
guest isolation can block it. No delayed replay of stale inputs is intended.

Only diymore ESP32-S3 Mini (8 MB flash + 8 MB PSRAM), KY-040 and USB power are
supported. Large v1 board, battery, bridge, external LED and display are excluded.
