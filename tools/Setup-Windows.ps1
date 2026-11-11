param([Parameter(Mandatory=$true)][string]$Port)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$setupPython=Join-Path $projectRoot '.venv/Scripts/python.exe'
if(-not(Test-Path -LiteralPath $setupPython)){throw 'Zuerst Flash-Windows.ps1 ausfuehren.'}
& $setupPython (Join-Path $PSScriptRoot 'serial_info.py') $Port
if($LASTEXITCODE){throw 'USB-Port konnte nicht gelesen werden. Port nach Neustart erneut im Geraete-Manager pruefen.'}
