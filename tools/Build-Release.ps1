param([string]$Python='py',[string]$ISCC='iscc',[switch]$BuildFirmware,[switch]$UseExistingEnvironment)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$buildRoot=Join-Path $projectRoot 'build'
$outputRoot=Join-Path $projectRoot 'dist'
New-Item -ItemType Directory -Force $buildRoot,$outputRoot | Out-Null
if($UseExistingEnvironment){$buildPython=$Python}
else{
 $environmentPath=Join-Path $projectRoot '.build-env'
 if($Python -eq 'py'){& $Python -3.12 -m venv $environmentPath}else{& $Python -m venv $environmentPath}
 if($LASTEXITCODE){throw 'Python 3.12 with Tcl/Tk is required for the build.'}
 $buildPython=Join-Path $environmentPath 'Scripts/python.exe'
 & $buildPython -m pip install -r (Join-Path $projectRoot 'installer/requirements-build.txt')
 if($LASTEXITCODE){throw 'Build dependencies could not be installed'}
}
& $buildPython -c 'import sys,tkinter; assert sys.version_info[:2] == (3,12), "Python 3.12 required"'
if($LASTEXITCODE){throw 'Check the Python/Tk version'}
Push-Location $projectRoot
try{
 if($BuildFirmware){
  if($projectRoot.Length -gt 85){throw 'Use a short path for the ESP32 firmware build, such as C:\SonosDial.'}
  & $buildPython -m pip install platformio==6.2.0
  if($LASTEXITCODE){throw 'PlatformIO installation failed'}
  & $buildPython -m platformio run
  if($LASTEXITCODE){throw 'Firmware build failed'}
  & $buildPython tools/make_factory.py
  if($LASTEXITCODE){throw 'Firmware image creation failed'}
 }
 & $buildPython -m unittest discover -s tests -p test_*.py -v
 if($LASTEXITCODE){throw 'Python tests failed'}
 $appRoot=Join-Path $buildRoot 'app'
 & $buildPython -m PyInstaller --noconfirm --windowed --onedir --name SonosDial --icon (Join-Path $projectRoot 'assets/sonosdial.ico') --distpath $appRoot --workpath (Join-Path $buildRoot 'pyinstaller') --specpath $buildRoot --collect-all esptool --add-data "$(Join-Path $projectRoot 'binaries');data" --add-data "$(Join-Path $projectRoot 'assets');assets" installer/app.py
 if($LASTEXITCODE){throw 'Desktop build failed'}
 $selfTest=Join-Path $buildRoot 'SELFTEST.json'
 $app=Join-Path $appRoot 'SonosDial/SonosDial.exe'
 $test=Start-Process -FilePath $app -ArgumentList @('--self-test',"`"$selfTest`"") -WindowStyle Hidden -PassThru
 if(-not $test.WaitForExit(60000)){Stop-Process -Id $test.Id -ErrorAction SilentlyContinue;throw 'Packaged selftest timed out; no verified installer release created'}
 if($test.ExitCode){throw 'Packaged application selftest failed'}
 if(-not(Test-Path -LiteralPath $selfTest)){throw 'Packaged application did not create a selftest result'}
 $report=Get-Content -LiteralPath $selfTest -Raw | ConvertFrom-Json
 foreach($key in @('firmware_sha256','device_guards','bundled_esptool','english_german_screens')){if($report.$key -ne 'pass'){throw "Packaged selftest failed: $key"}}
 $sourceArchive=Join-Path $buildRoot 'SonosDial-Source-1.2.0.zip'
 & $buildPython tools/package_source.py --out $sourceArchive
 if($LASTEXITCODE){throw 'Source package failed'}
 & $ISCC "/DBuildRoot=$buildRoot" "/DOutputRoot=$outputRoot" installer/setup.iss
 if($LASTEXITCODE){throw 'Installer compiler failed'}
 Copy-Item -LiteralPath $sourceArchive -Destination $outputRoot -Force
 foreach($doc in @('tests/README.md')){Copy-Item -LiteralPath (Join-Path $projectRoot $doc) -Destination (Join-Path $outputRoot ([IO.Path]::GetFileName($doc))) -Force}
 $sums=Get-ChildItem -LiteralPath $outputRoot -File | Where-Object Name -ne 'SHA256SUMS.txt' | Sort-Object Name | ForEach-Object {"$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLower())  $($_.Name)"}
 $sums | Set-Content -LiteralPath (Join-Path $outputRoot 'SHA256SUMS.txt') -Encoding ascii
 Write-Output "Release prepared: $outputRoot"
}finally{Pop-Location}
