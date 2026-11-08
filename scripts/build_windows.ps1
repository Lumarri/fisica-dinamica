$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location (Split-Path -Parent $PSScriptRoot)
$DynamisPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path $DynamisPython)) {
    throw 'Primero crea .venv con Python 3.11 o posterior. Consulta README.md.'
}
& $DynamisPython -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias de compilacion.' }
& $DynamisPython -m PyInstaller --noconfirm --clean Dynamis.spec
if ($LASTEXITCODE -ne 0) { throw 'La compilacion no se completo.' }
Write-Host 'Ejecutable creado: dist\Dynamis.exe'
