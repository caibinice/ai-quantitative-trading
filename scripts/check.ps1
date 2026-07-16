$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'

Push-Location (Join-Path $Root 'backend')
try {
    & $Python -m ruff check app tests scripts
    if ($LASTEXITCODE -ne 0) { throw 'Ruff 检查失败。' }
    & $Python -m pytest
    if ($LASTEXITCODE -ne 0) { throw '后端测试失败。' }
} finally {
    Pop-Location
}

Push-Location (Join-Path $Root 'frontend')
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw '前端构建失败。' }
} finally {
    Pop-Location
}

Write-Host '全部检查通过。' -ForegroundColor Green
