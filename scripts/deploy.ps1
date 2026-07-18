$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Python)) {
    throw '缺少 .venv。请先运行 pwsh -File scripts/setup.ps1。'
}

& (Join-Path $PSScriptRoot 'check.ps1')
if ($LASTEXITCODE -ne 0) { throw '发布前检查失败。' }

$env:PYTHONUTF8 = '1'
& $Python (Join-Path $PSScriptRoot 'remote\deploy.py')
if ($LASTEXITCODE -ne 0) { throw '远程发布失败。' }

Write-Host '远程发布完成。访问凭据保存在 .deploy\web-auth.json。' -ForegroundColor Green
