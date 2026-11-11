"""Export replaceable LGPL inputs after compiling changed firmware (no hardware)."""
import argparse, pathlib, json, re, shutil
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--framework',required=True,help='Pinned framework-arduinoespressif32 package directory')
p.add_argument('--log',default='build-firmware-verbose.log',help='Captured pio run -v output containing final linker command')
a=p.parse_args();root=pathlib.Path(__file__).resolve().parents[1];kit=root/'firmware-relink'
framework=pathlib.Path(a.framework).resolve()
log=(root/a.log).read_text(encoding='utf-8',errors='replace').replace('\\','/')
commands=[s for s in log.splitlines() if s.startswith('xtensa-esp32s3-elf-g++ ') and '-o .pio/build/sonosdial/firmware.elf' in s]
if len(commands)!=1:raise SystemExit('Expected one final linker command in the verbose build log')
args=re.findall(r'(?:[^\s"]|"[^"]*")+',commands[0])[1:];portable=[]
for arg in args:
 arg=arg.replace('"','').replace('\\','/').replace(framework.as_posix()+'/tools/sdk/esp32s3','sdk').replace(root.as_posix()+'/.pio/build/sonosdial','build').replace('.pio/build/sonosdial','build')
 if arg=='build/firmware.elf':arg='relinked.elf'
 if arg.startswith('-Wl,-Map='):arg='-Wl,-Map=relinked.map'
 if re.search(r'[A-Za-z]:/',arg):raise SystemExit('Unmapped absolute linker input: '+arg)
 portable.append(arg)
kit.mkdir(exist_ok=True)
(kit/'link-args.json').write_text(json.dumps(portable,indent=2)+'\n',encoding='utf-8')
build=root/'.pio/build/sonosdial'
for source in build.rglob('*'):
 if source.is_file() and source.suffix in ('.o','.a','.ld'):
  dest=kit/'build'/source.relative_to(build);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
if not (kit/'sdk').is_dir() or not (kit/'sources').is_dir():
 raise SystemExit('Add matching SDK archives, Arduino source and original runtime notices from the full release source asset before distribution')
print('Exported current application objects and portable linker arguments')
