[CmdletBinding()]
param(
  [string[]]$Skills
)
$ErrorActionPreference = 'Stop'
$repoSkills = Join-Path $PSScriptRoot 'skills'
if (-not (Test-Path $repoSkills)) { throw "Skills directory not found: $repoSkills" }
$availableSkills = @(Get-ChildItem -Path $repoSkills -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | Select-Object -ExpandProperty Name)
if ($availableSkills.Count -eq 0) { throw "No skills with SKILL.md found under $repoSkills" }
if (-not $Skills -or $Skills.Count -eq 0) { $Skills = $availableSkills }
$unknownSkills = @($Skills | Where-Object { $_ -notin $availableSkills })
if ($unknownSkills.Count -gt 0) { throw "Unknown skill(s): $($unknownSkills -join ', '). Available: $($availableSkills -join ', ')" }

$userProfilePath = $env:USERPROFILE
$skillTargets = [System.Collections.Generic.List[string]]::new()
$detectors = @(
  @{ Path = (Join-Path $userProfilePath '.codex'); Command = 'codex'; Skills = (Join-Path $userProfilePath '.codex\skills') },
  @{ Path = (Join-Path $userProfilePath '.claude'); Command = 'claude'; Skills = (Join-Path $userProfilePath '.claude\skills') },
  @{ Path = (Join-Path $userProfilePath '.gemini'); Command = 'gemini'; Skills = (Join-Path $userProfilePath '.gemini\skills') },
  @{ Path = (Join-Path $userProfilePath '.cursor'); Command = 'cursor'; Skills = (Join-Path $userProfilePath '.cursor\skills') },
  @{ Path = (Join-Path $userProfilePath '.config\opencode'); Command = 'opencode'; Skills = (Join-Path $userProfilePath '.config\opencode\skills') }
)
foreach ($agent in $detectors) {
  if ((Test-Path $agent.Path) -or (Get-Command $agent.Command -ErrorAction SilentlyContinue)) {
    if (-not $skillTargets.Contains($agent.Skills)) { $skillTargets.Add($agent.Skills) }
  }
}
$commonSkills = Join-Path $userProfilePath '.agents\skills'
if (-not $skillTargets.Contains($commonSkills)) { $skillTargets.Add($commonSkills) }

foreach ($skill in $Skills) {
  $source = Join-Path $repoSkills $skill
  foreach ($target in $skillTargets) {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item $source (Join-Path $target $skill) -Recurse -Force
  }
}

if ('auto-video-editor-windows' -in $Skills) {
  function Require-Winget {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
      throw 'winget is required. Install/update App Installer from Microsoft Store, then rerun this script.'
    }
  }
  function Install-WingetPackage([string]$Id) {
    Write-Host "Installing $Id ..."
    winget install --id $Id --exact --source winget --accept-source-agreements --accept-package-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw "winget failed installing $Id (exit $LASTEXITCODE). Fix the reported issue and rerun installer." }
  }
  Require-Winget
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Install-WingetPackage 'Git.Git' }
  if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Install-WingetPackage 'OpenJS.NodeJS.LTS' }
  if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Install-WingetPackage 'Gyan.FFmpeg.Shared' }
  $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
  $env:Path += ";$env:ProgramFiles\nodejs;$env:ProgramFiles\Git\cmd;$env:LOCALAPPDATA\Microsoft\WinGet\Links"
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is not on PATH. Restart PowerShell and rerun installer.' }
  if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js is not on PATH. Restart PowerShell and rerun installer.' }

  $hotclipDir = Join-Path $env:LOCALAPPDATA 'HotClip\app'
  New-Item -ItemType Directory -Force -Path (Split-Path $hotclipDir) | Out-Null
  if (Test-Path $hotclipDir) {
    git -C $hotclipDir pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'HotClip update failed. Resolve the Git message and rerun installer.' }
  } else {
    git clone --depth 1 https://github.com/xixihhhh/hotclip.git $hotclipDir
    if ($LASTEXITCODE -ne 0) { throw 'Could not download HotClip from its public GitHub repository.' }
  }
  Set-Location $hotclipDir
  corepack enable
  corepack prepare pnpm@latest --activate
  pnpm install
  if ($LASTEXITCODE -ne 0) { throw 'HotClip dependency installation failed.' }
  pnpm cli doctor --download
  if ($LASTEXITCODE -ne 0) { Write-Warning 'HotClip installed, but ASR model pre-download failed; it will retry at first transcription.' }
  Write-Host "HotClip installed at: $hotclipDir"
}

Write-Host "Installed skill(s): $($Skills -join ', ')"
Write-Host "Agent skill directories: $($skillTargets -join ', ')"
Write-Host 'Restart the agent to load the installed skills.'
