param(
    [switch]$SeedDemo
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw '未找到 Python。请先安装 64 位 Python 3.11 或更高版本。'
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw '未找到 npm。请先安装 Node.js 20 或更高版本。'
}

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv (Join-Path $Root '.venv')
    if ($LASTEXITCODE -ne 0) { throw '创建 Python 虚拟环境失败。' }
}

& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw '升级 pip 失败。' }
& $Python -m pip install -r (Join-Path $Root 'backend\requirements-dev.txt')
if ($LASTEXITCODE -ne 0) { throw '安装 Python 依赖失败。' }

Push-Location (Join-Path $Root 'frontend')
try {
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw '安装前端依赖失败。' }
} finally {
    Pop-Location
}

if ($SeedDemo) {
    Push-Location (Join-Path $Root 'backend')
    try {
        & $Python 'scripts\seed_demo.py'
        if ($LASTEXITCODE -ne 0) { throw '初始化演示数据失败。' }
    } finally {
        Pop-Location
    }
}

Write-Host '安装完成。运行 pwsh -File scripts/dev.ps1 启动项目。' -ForegroundColor Green
