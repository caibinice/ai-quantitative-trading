param(
  [string]$Message = '',
  [string[]]$Files = @(),
  [string]$CredentialsPath = '',
  [string]$Proxy = 'http://127.0.0.1:20808',
  [switch]$ValidateOnly,
  [switch]$PushOnly
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($CredentialsPath)) {
  $CredentialsPath = Join-Path $projectRoot 'credentials.txt'
}
if (-not (Test-Path -LiteralPath $CredentialsPath)) {
  throw "缺少项目凭据：$CredentialsPath。独立模式只读取本仓库 credentials.txt。"
}

function Import-IniFile {
  param([Parameter(Mandatory = $true)][string]$Path)
  $result = @{}
  $section = ''
  foreach ($original in Get-Content -LiteralPath $Path -Encoding UTF8) {
    $line = $original.Trim()
    if (-not $line -or $line.StartsWith('#') -or $line.StartsWith(';')) { continue }
    if ($line -match '^\[(.+)\]$') {
      $section = $Matches[1].Trim().ToLowerInvariant()
      if (-not $result.ContainsKey($section)) { $result[$section] = @{} }
      continue
    }
    $parts = $line.Split('=', 2)
    if ($parts.Count -eq 2 -and $section) {
      $result[$section][$parts[0].Trim().ToLowerInvariant()] = $parts[1].Trim()
    }
  }
  return $result
}

$credentials = Import-IniFile -Path $CredentialsPath
if (-not $credentials.ContainsKey('github')) {
  throw 'credentials.txt 缺少 [github]。'
}
$github = $credentials['github']
$token = if ($github.ContainsKey('token')) { $github['token'] } else { '' }
if ([string]::IsNullOrWhiteSpace($token)) {
  throw 'credentials.txt 缺少 [github] token。'
}
$gitUserName = if ($github.ContainsKey('user_name') -and -not [string]::IsNullOrWhiteSpace($github['user_name'])) {
  $github['user_name']
} else {
  'caibinice'
}
$gitUserEmail = if ($github.ContainsKey('user_email') -and -not [string]::IsNullOrWhiteSpace($github['user_email'])) {
  $github['user_email']
} else {
  'caibinice@users.noreply.github.com'
}

$branch = (& git -C $projectRoot branch --show-current).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) {
  throw '当前处于 detached HEAD，不能自动提交或推送。'
}
$basic = [Convert]::ToBase64String(
  [Text.Encoding]::ASCII.GetBytes("x-access-token:$token")
)
$gitEnvironmentNames = @(
  'GIT_CONFIG_COUNT',
  'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0',
  'GIT_CONFIG_KEY_1', 'GIT_CONFIG_VALUE_1',
  'GIT_CONFIG_KEY_2', 'GIT_CONFIG_VALUE_2',
  'GIT_CONFIG_KEY_3', 'GIT_CONFIG_VALUE_3'
)
$previousEnvironment = @{}
foreach ($name in $gitEnvironmentNames) {
  $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

try {
  $env:GIT_CONFIG_COUNT = '4'
  $env:GIT_CONFIG_KEY_0 = 'http.proxy'
  $env:GIT_CONFIG_VALUE_0 = $Proxy
  $env:GIT_CONFIG_KEY_1 = 'http.https://github.com/.extraheader'
  $env:GIT_CONFIG_VALUE_1 = "AUTHORIZATION: basic $basic"
  $env:GIT_CONFIG_KEY_2 = 'user.name'
  $env:GIT_CONFIG_VALUE_2 = $gitUserName
  $env:GIT_CONFIG_KEY_3 = 'user.email'
  $env:GIT_CONFIG_VALUE_3 = $gitUserEmail

  & git -C $projectRoot fetch origin $branch
  if ($LASTEXITCODE -ne 0) { throw 'GitHub fetch 失败。' }
  $divergenceText = ((& git -C $projectRoot rev-list --left-right --count "HEAD...origin/$branch") -join ' ').Trim()
  $divergence = $divergenceText -split '\s+'
  $localAhead = [int]$divergence[0]
  $remoteAhead = [int]$divergence[1]
  if ($remoteAhead -gt 0) {
    throw "远端领先 $remoteAhead 个提交，请先 pull --ff-only。"
  }
  if ($ValidateOnly) {
    Write-Host "OK branch=$branch localAhead=$localAhead remoteAhead=$remoteAhead token=loaded proxy=$Proxy"
    return
  }
  if ($PushOnly) {
    if ($localAhead -eq 0) {
      Write-Host '本地已与远端同步，无需推送。'
      return
    }
  } else {
    if ($localAhead -gt 0) {
      throw "本地已有 $localAhead 个未推送提交；请先用 -PushOnly 或人工确认。"
    }
    if ([string]::IsNullOrWhiteSpace($Message) -or $Files.Count -eq 0) {
      throw '提交模式必须同时提供 -Message 和明确的 -Files。'
    }
    & git -C $projectRoot diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
      throw '仓库已有暂存内容，请先处理暂存区。'
    }
    & git -C $projectRoot add -- @Files
    if ($LASTEXITCODE -ne 0) { throw '暂存指定文件失败。' }
    & git -C $projectRoot diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { throw '指定文件没有可提交的变化。' }
    & git -C $projectRoot diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw '暂存内容检查失败。' }
    & git -C $projectRoot commit -m $Message
    if ($LASTEXITCODE -ne 0) { throw 'Git 提交失败。' }
  }
  & git -C $projectRoot push origin $branch
  if ($LASTEXITCODE -ne 0) { throw 'GitHub 推送失败。' }
  $revision = (& git -C $projectRoot rev-parse --short HEAD).Trim()
  Write-Host "Pushed branch=$branch commit=$revision" -ForegroundColor Green
} finally {
  foreach ($name in $gitEnvironmentNames) {
    [Environment]::SetEnvironmentVariable(
      $name,
      $previousEnvironment[$name],
      'Process'
    )
  }
}
