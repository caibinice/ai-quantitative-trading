param(
    [switch]$BuildOnly
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Python)) {
    throw '缺少 .venv。请先运行 pwsh -File scripts/setup.ps1。'
}

Push-Location (Join-Path $Root 'frontend')
try {
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw '前端依赖安装失败。' }
} finally {
    Pop-Location
}

& (Join-Path $PSScriptRoot 'check.ps1')
if ($LASTEXITCODE -ne 0) { throw '发布前检查失败。' }

if ($BuildOnly) {
    Write-Host '量化项目本地检查完成，未连接远程服务器。' -ForegroundColor Green
    return
}

$env:PYTHONUTF8 = '1'
& $Python (Join-Path $PSScriptRoot 'remote\deploy.py')
if ($LASTEXITCODE -ne 0) { throw '远程发布失败。' }

Write-Host '远程发布完成。敏感操作配置保存在 .deploy\action-auth.json。' -ForegroundColor Green
