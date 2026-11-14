# Windows Auto Video Editor skill bundle

This package contains a standard Agent Skill and a one-time PowerShell bootstrap installer. It downloads the video tools and installs the skill into detected agent skill directories.

## Install

1. Extract this ZIP on Windows.
2. Open PowerShell in the extracted folder.
3. Run:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\install.ps1
   ```

4. Restart the detected agent. The installed skill is `auto-video-editor-windows`.

The installer uses winget to install Git, Node.js LTS, and FFmpeg; downloads HotClip from its public GitHub repository; installs JavaScript dependencies and its local speech model. It detects Codex, Claude Code, Gemini CLI, Cursor, and OpenCode from their user directories or commands, then installs the skill into each detected skill folder. If none are detected, it installs into `%USERPROFILE%\.agents\skills`.

Installation needs internet access and several GB of free disk space for HotClip and its local speech model. Highlight selection is done by the active assistant from the local transcript; no LLM service is installed or configured. The number of clips adapts to source duration and the number of distinct complete highlights, with fewer clips when the material does not support the suggested range.

This package includes no account credentials or API keys. Software is obtained from winget and the public HotClip GitHub repository. HotClip is open source under AGPL-3.0; its license is available in the downloaded repository.
