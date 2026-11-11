"""Run after `pio run`; requires esptool 4.x. No device access."""
import hashlib,json,pathlib,shutil,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1]
build=root/'.pio/build/sonosdial'
out=root/'binaries'
out.mkdir(exist_ok=True)
for name in ('firmware.bin','bootloader.bin','partitions.bin'):
    shutil.copy2(build/name,out/name)
# boot_app0.bin is the standard ESP32 Arduino OTA boot-selection image.
# It is supplied in the release. On a fresh source-only checkout locate it in
# the pinned framework package and copy it into binaries before packaging.
if not (out/'boot_app0.bin').exists():
    raise SystemExit('Copy framework tools/partitions/boot_app0.bin to binaries first')
subprocess.run([sys.executable,'-m','esptool','--chip','esp32s3','merge_bin',
    '-o',str(out/'sonosdial-factory.bin'),'--flash_size','8MB',
    '0x0',str(out/'bootloader.bin'),'0x8000',str(out/'partitions.bin'),
    '0xe000',str(out/'boot_app0.bin'),'0x10000',str(out/'firmware.bin')],check=True)
merged=(out/'sonosdial-factory.bin').read_bytes()
for offset,name in ((0,'bootloader.bin'),(0x8000,'partitions.bin'),(0xe000,'boot_app0.bin'),(0x10000,'firmware.bin')):
    image=(out/name).read_bytes()
    if merged[offset:offset+len(image)]!=image:raise SystemExit(f'Offset validation failed: {name}')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.bin'))}
(out/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
print('PASS: merged offsets 0x0 / 0x8000 / 0xe000 / 0x10000; SHA256.json written')
