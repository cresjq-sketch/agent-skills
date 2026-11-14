[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  $launchArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $PSCommandPath + '"'))
  Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $launchArgs
  exit
}
$skillName = 'auto-video-editor-windows'
$skillTargets = [System.Collections.Generic.List[string]]::new()
$userProfilePath = $env:USERPROFILE
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
$hotclipDir = Join-Path $env:LOCALAPPDATA 'HotClip\app'

function Require-Winget {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'Windows Package Manager (winget) is required. Install/update App Installer from Microsoft Store, then rerun this script.'
  }
}
function Install-WingetPackage([string]$Id) {
  Write-Host "Installing $Id ..."
  winget install --id $Id --exact --source winget --accept-source-agreements --accept-package-agreements --silent
  if ($LASTEXITCODE -ne 0) { throw "winget failed installing $Id (exit $LASTEXITCODE). Fix the reported issue and rerun; installed packages will be detected by winget." }
}

Require-Winget
New-Item -ItemType Directory -Force -Path $skillTargets,(Split-Path $hotclipDir) | Out-Null
Install-WingetPackage 'Git.Git'
Install-WingetPackage 'OpenJS.NodeJS.LTS'
Install-WingetPackage 'Gyan.FFmpeg.Shared'

# Refresh PATH for this process after winget installs.
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
$env:Path += ";$env:ProgramFiles\nodejs;$env:ProgramFiles\Git\cmd;$env:LOCALAPPDATA\Microsoft\WinGet\Links"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git was installed but is not on PATH. Restart PowerShell and rerun install.ps1.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js was installed but is not on PATH. Restart PowerShell and rerun install.ps1.' }

# Install the complete, shareable skill from this bundle.
$sourceSkill = Join-Path $PSScriptRoot $skillName
if (-not (Test-Path (Join-Path $sourceSkill 'SKILL.md'))) { throw "Skill folder missing from install bundle: $sourceSkill" }
foreach ($target in $skillTargets) {
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  Copy-Item $sourceSkill (Join-Path $target $skillName) -Recurse -Force
}

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

# Pre-download the local speech model so the first edit does not unexpectedly wait for it.
pnpm cli doctor --download
if ($LASTEXITCODE -ne 0) { Write-Warning 'HotClip installed, but its optional ASR model pre-download failed; it will retry on first transcription.' }
Write-Host "`nInstalled skill in: $($skillTargets -join ', ')"
Write-Host "HotClip: $hotclipDir"
Write-Host 'Restart your agent to discover the skill. The local speech model download may take time.'
