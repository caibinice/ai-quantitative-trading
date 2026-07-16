$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
$Vite = Join-Path $Root 'frontend\node_modules\vite\bin\vite.js'

if (-not (Test-Path -LiteralPath $Python) -or -not (Test-Path -LiteralPath $Vite)) {
    throw '依赖尚未安装。请先运行 pwsh -File scripts/setup.ps1 -SeedDemo。'
}

$Backend = Start-Process `
    -FilePath $Python `
    -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload') `
    -WorkingDirectory (Join-Path $Root 'backend') `
    -WindowStyle Hidden `
    -PassThru

try {
    Write-Host 'API: http://127.0.0.1:8000/docs' -ForegroundColor Cyan
    Write-Host 'Web: http://127.0.0.1:5173' -ForegroundColor Cyan
    Write-Host '按 Ctrl+C 同时停止前后端。' -ForegroundColor DarkGray
    & (Get-Command node).Source $Vite --host 127.0.0.1 --port 5173
} finally {
    if ($Backend -and -not $Backend.HasExited) {
        Stop-Process -Id $Backend.Id -Force
    }
}
