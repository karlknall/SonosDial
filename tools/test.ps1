param([string]$Compiler='zig')
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$testTemp=Join-Path $projectRoot '.test-build'
New-Item -ItemType Directory -Force $testTemp | Out-Null
foreach($testName in @('input','selection','xml','framing','validation')){
 $testArgs=@('c++','-std=c++17',"-I$projectRoot/lib/tinyxml2","$projectRoot/tests/${testName}_test.cpp",'-o',"$testTemp/$testName.exe")
 if($testName -eq 'xml'){$testArgs+="$projectRoot/lib/tinyxml2/tinyxml2.cpp"}
 & $Compiler @testArgs
 if($LASTEXITCODE){throw "Kompilierung fehlgeschlagen: $testName"}
 & "$testTemp/$testName.exe"
 if($LASTEXITCODE){throw "Test fehlgeschlagen: $testName"}
}
