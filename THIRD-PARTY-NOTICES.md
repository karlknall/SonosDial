# Third-party notices and corresponding source

This is a component-specific license mapping, not a blanket MIT license.

| Component | License and supplied material |
|---|---|
| SonosDial Windows assistant (app.py/device.py/i18n.py) | GPL-3.0-or-later; licenses/GPL-3.0.txt; source and build scripts included |
| Own firmware application, documentation and other own helper scripts | MIT; licenses/MIT-SonosDial.txt |
| esptool 4.8.1 | GPL-2.0-or-later; full official source under third_party/esptool-4.8.1 |
| esptool Legacy Flasher Stub 1.3.0 | GPL-2.0-or-later; full source and original build instructions/Makefiles under third_party/esptool-legacy-flasher-stub-1.3.0 |
| Newer esptool stub files | Apache-2.0 or MIT as stated in the corresponding upstream directory; original notices retained |
| Arduino-ESP32 2.0.17 | LGPL-2.1-or-later, with additional per-file original notices; actual source and replaceable .a/.o files under firmware-relink |
| ESP-IDF 4.4.7 and additional SDK components | Apache-2.0, BSD/MIT and original Espressif-specific conditions; licenses/esp-idf-4.4.7, licenses/sdk-upstream and firmware-relink/SDK-VERSIONS.txt |
| TinyXML2 10.0.0 | zlib; lib/tinyxml2/LICENSE.txt and source included |
| ArduinoJson 6.21.5 | MIT; licenses/ArduinoJson; version pinned in platformio.ini |
| Python 3.12.14 and Tcl/Tk 8.6 | Original texts under licenses/runtime/Python-Tcl-Tk, including additional conditions for Microsoft distributable runtime code |
| pyserial, bitstring/tibs, cryptography, cffi, ecdsa, reedsolo, PyYAML, intelhex, six, pycparser | Original package metadata/notices and available package source under licenses/runtime; exact versions in installer/requirements-build.txt |
| PyInstaller 6.16.0 | GPL with bootloader exception; original COPYING.txt and metadata under licenses/runtime; this exception does not override esptool's license |
| Inno Setup 7.1.1 | Separate build tool; generated installer retains vendor notices. The compiler is not redistributed. |
| GCC/newlib runtime components | Original notices and runtime exceptions under firmware-relink/licenses; compiler not redistributed |

The combined desktop application is explicitly distributed under GPL-3.0-or-later. Esptool's GPL-2.0-or-later terms permit choosing GPLv3, which also makes the distribution of the combination with Apache-2.0 dependencies explicit. Upstream components retain their original terms. The earlier MIT attribution for own assistant code is preserved. The installer displays the GPL and includes the complete companion source archive; keep source, notices and build scripts with redistributions.

For LGPL components, modification, replacement and relinking are permitted. The supplied relink material was tested: with unchanged archives it produces byte-identical firmware.bin. No signature lock is enabled. The own firmware application remains MIT-licensed; dependencies retain their original conditions.

Original legal license texts are not translated or replaced by the English/German documentation. No upstream component was modified. Public upstream test fixtures may contain example keys; these are not the user's personal credentials. No personal Wi-Fi credentials are hardcoded into SonosDial.

Official references: https://github.com/espressif/esptool/tree/v4.8.1 · https://github.com/espressif/esptool-legacy-flasher-stub/tree/v1.3.0 · https://github.com/espressif/arduino-esp32/tree/2.0.17 · https://github.com/espressif/esp-idf/tree/v4.4.7 . Additional SDK notice receipts are recorded in licenses/sdk-upstream/SOURCES.json.

[Deutsch](docs/de/THIRD-PARTY-NOTICES.md)
