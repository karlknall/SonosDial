"""Create the complete companion source archive, including LGPL relink inputs."""
import argparse,pathlib,hashlib,json,zipfile,os
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
project=pathlib.Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(project).startswith('\\\\?\\'):project=pathlib.Path('\\\\?\\'+str(project))
paths=[]
for path in project.rglob('*'):
    if not path.is_file():continue
    relative=path.relative_to(project)
    if relative.parts[0] in ('build','dist','.pio','.venv','.build-env','.test-build'):continue
    if relative.parts[0]=='firmware-relink' and path.name in ('relinked.elf','relinked.map','link.rsp'):continue
    if any(x in ('.git','__pycache__') for x in relative.parts) or path.suffix in ('.pyc','.log'):continue
    if relative.as_posix()=='SOURCE-MANIFEST.json':continue
    paths.append(path)
paths.sort()
manifest={p.relative_to(project).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths}
destination=pathlib.Path(a.out).resolve();destination.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in paths:z.write(path,'SonosDial/'+path.relative_to(project).as_posix())
    z.writestr('SonosDial/SOURCE-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(destination) as z:
    assert z.testzip() is None
    for name,record in manifest.items():assert hashlib.sha256(z.read('SonosDial/'+name)).hexdigest()==record['sha256']
print(f'Source archive verified: {len(paths)+1} files, {destination.stat().st_size} bytes')
