$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
if (!(Test-Path .venv)) { py -3.12 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -e .
& .\.venv\Scripts\pip.exe install -r requirements-build.txt
Remove-Item -Recurse -Force build,dist -ErrorAction SilentlyContinue
& .\.venv\Scripts\pyinstaller.exe --clean WA_Desktop_Connector.spec

$candidates = @()
$cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($cmd) { $candidates += $cmd.Source }
if (${env:ProgramFiles(x86)}) { $candidates += "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
if ($env:ProgramFiles) { $candidates += "$env:ProgramFiles\Inno Setup 6\ISCC.exe" }
if ($env:LOCALAPPDATA) { $candidates += "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" }
$iscc = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (!$iscc) { throw "Inno Setup 6 was not found." }
Write-Host "Using Inno Setup: $iscc"
& $iscc installer\WA_Desktop_Connector.iss
Write-Host "Installer created in windows\dist"
