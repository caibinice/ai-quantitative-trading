$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$env:PYTHONUTF8 = '1'
& $Python (Join-Path $PSScriptRoot 'remote\control.py') start
if ($LASTEXITCODE -ne 0) { throw '远程启动失败。' }
