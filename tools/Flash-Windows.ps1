param([Parameter(Mandatory=$true)][string]$Port)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$image=Join-Path $projectRoot 'binaries/sonosdial-factory.bin'
$expectedHash=(Get-Content (Join-Path $projectRoot 'binaries/SHA256.json') -Raw | ConvertFrom-Json).'sonosdial-factory.bin'
if(-not $expectedHash -or (Get-FileHash -LiteralPath $image -Algorithm SHA256).Hash -ne $expectedHash){throw 'Firmware-Pruefsumme stimmt nicht. Paket erneut entpacken.'}
$allHashes=Get-Content (Join-Path $projectRoot 'binaries/SHA256.json') -Raw | ConvertFrom-Json
foreach($entry in $allHashes.PSObject.Properties){$filePath=Join-Path (Join-Path $projectRoot 'binaries') $entry.Name; if((Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash -ne $entry.Value){throw "Pruefsumme ungueltig: $($entry.Name)"}}
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python 3 installieren (python.org), danach dieses Fenster neu oeffnen.' }
$flashPython=Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $flashPython)) { & py -3 -m venv (Join-Path $projectRoot '.venv'); if($LASTEXITCODE){throw 'Python-Umgebung konnte nicht erstellt werden'} }
& $flashPython -m pip install 'esptool==4.8.1'
if($LASTEXITCODE){throw 'Installation fehlgeschlagen'}
$binaryDir=Join-Path $projectRoot 'binaries'
$probeOutput = & $flashPython -m esptool --chip esp32s3 --port $Port --baud 115200 --before default_reset --after no_reset flash_id 2>&1 | Out-String
if($LASTEXITCODE -or $probeOutput -notmatch 'ESP32-S3' -or $probeOutput -notmatch 'Detected flash size:\s*8MB\b'){throw 'ESP32-S3 mit 8 MB Flash wurde nicht bestaetigt. Nichts geschrieben; Board ggf. mit RESET neu starten.'}
& $flashPython -m esptool --chip esp32s3 --port $Port --baud 115200 --before default_reset --after hard_reset write_flash --flash_size 8MB 0x0 (Join-Path $binaryDir 'bootloader.bin') 0x8000 (Join-Path $binaryDir 'partitions.bin') 0xe000 (Join-Path $binaryDir 'boot_app0.bin') 0x10000 (Join-Path $binaryDir 'firmware.bin')
if($LASTEXITCODE){throw 'Flash fehlgeschlagen. BOOT halten, RESET kurz druecken, BOOT loslassen; COM-Port erneut pruefen.'}
Write-Host 'Version 1.2.0 geschrieben. NVS wurde ausgespart. Einrichtung im Mini-USB-Assistenten fortsetzen.'
