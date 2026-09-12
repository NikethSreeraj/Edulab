$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Create the virtual environment first: python -m venv .venv' }
& $python -m pip install -r requirements.txt pyinstaller
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name Edulab --add-data 'README.md;.' --add-data 'app/data;app/data' run_web.py
Write-Host "Built: $root\dist\Edulab.exe"
