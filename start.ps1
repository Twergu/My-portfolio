param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$ProjectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $ProjectPython)) {
    throw 'Create the environment first: py -3 -m venv .venv; then install requirements.txt using .venv\Scripts\python.exe -m pip install -r requirements.txt'
}
& $ProjectPython run.py --port $Port
exit $LASTEXITCODE
