# Build SonosDial 1.2.0

## Inputs

Use Python 3.12 x64 with Tk, PlatformIO 6.2.0 and Inno Setup 7.1.1.
Pinned firmware dependencies are in platformio.ini; desktop dependencies are in
installer/requirements-build.txt. The target uses a generic S3 variant with
physical GPIO4/5/6, 8 MB flash, qio_opi PSRAM and native USB CDC.

For the complete offline packaging/relink inputs extract the full
SonosDial-Source-1.2.0.zip release asset to a short path (under 85 characters),
such as C:/SonosDial. The lean GitHub checkout omits binaries and large LGPL
objects; do not treat GitHub's automatic source-code ZIP as the complete asset.

## Firmware

    python -m pip install platformio==6.2.0
    python -m platformio run
    python tools/make_factory.py

On a fresh GitHub checkout copy the pinned Arduino framework's
tools/partitions/boot_app0.bin into binaries first. It is already included in the
full source asset. make_factory.py verifies offsets and creates SHA256.json.

## Tests

    python -m pip install -r installer/requirements-build.txt
    python -m unittest discover -s tests -p test_*.py -v
    ./tools/test.ps1 -Compiler PATH/zig.exe

On Linux the native suites can also be built with g++ (see the GitHub workflow).
Tk-based wizard tests need a working graphical session. No test flashes a board.

## Windows app and installer

From the full source package, use PowerShell:

    ./tools/Build-Release.ps1 -ISCC 'C:/Program Files/Inno Setup 7/ISCC.exe'

The script packages the supplied verified firmware by default; add -BuildFirmware
to compile changed firmware first. It runs tests, bundles esptool/assets, runs a
packaged self-test with a timeout, packages source and compiles the installer.
Failure of the packaged test stops the release build. Generated files go to dist.
An existing Python build environment can be passed with -UseExistingEnvironment
and -Python PATH/python.exe. No end-user Python installation is required.

assets/Build-Icons.ps1 regenerates original SVG/PNG/ICO/BMP branding using Windows
System.Drawing. No third-party logo or paid asset is required.

## LGPL replacement and firmware changes

firmware-relink in the full source archive contains current application .o files,
replaceable .a libraries, SDK linker inputs, original Arduino source and notices.
Its relink.py and link-args.json reproduce this firmware with the recorded
compiler and esptool. See firmware-relink/README.md.

After changing firmware, regenerate the kit from the new build before distributing
new binaries: tools/export_relink.py --help documents the required arguments.
Runtime licenses and full esptool/stub sources must remain in the full source
asset. The build tool does not sign or publish anything automatically.
