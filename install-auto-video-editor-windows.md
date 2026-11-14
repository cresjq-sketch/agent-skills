# Install `auto-video-editor-windows` in the current agent

This file is the installation request for the single `auto-video-editor-windows` skill.

## Source

- Repository: `cresjq-sketch/agent-skills`
- Skill directory: `skills/auto-video-editor-windows`
- Branch: `main`

## Instructions for the agent receiving this file

1. Use your platform's native skill installer for the repository path above. In Codex, use the built-in `skill-installer` with repository `cresjq-sketch/agent-skills` and path `skills/auto-video-editor-windows`.
2. Install only this skill into the current agent's user-level skill directory. Fetch the complete skill directory and preserve its structure. Do not fetch other skills or the whole repository.
3. Inspect the installed `SKILL.md` and confirm it is discoverable by this agent.
4. The skill targets Windows. If the current environment is Windows and the user asked for a ready-to-run setup, install only its stated dependencies using the platform's package manager and obtain HotClip from its public source. This skill requires spoken subtitles burned into each output MP4 plus a matching SRT by default, and careful removal of confirmed filler words such as isolated “嗯/呃” and stutter repeats. The skill instructions specify when context-dependent words like “这/这个/然后” must be preserved. Do not run a repository PowerShell bootstrap script. If the current environment is not Windows, install the skill files only and report that its runtime dependencies are Windows-specific.
5. Report the installation path, verification result, and any dependencies that still need attention. Mention if the agent must restart or start a new session to load the skill.

If this skill already exists, compare it with the requested repository version before changing anything. Preserve unrelated skills and user data.
