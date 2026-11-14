# Install the video editing skill in the current agent

This is the single-skill installation request for `auto-video-editor-windows` (the repository directory keeps its historical name; the skill supports macOS and Windows).

## Source

- Repository: `cresjq-sketch/agent-skills`
- Skill directory: `skills/auto-video-editor-windows`
- Branch: `main`

## Instructions for the agent receiving this file

1. Use your platform's native skill installer for the repository path above. In Codex, use the built-in `skill-installer` with repository `cresjq-sketch/agent-skills` and path `skills/auto-video-editor-windows`.
2. Install only this skill into the current agent's user-level skill directory. Fetch the complete skill directory and preserve its structure. Do not fetch other skills or the whole repository.
3. Inspect the installed `SKILL.md` and confirm it is discoverable by this agent.
4. This skill runs on macOS and Windows. If the user wants it ready to run, install Git, Node.js LTS, FFmpeg, pnpm and HotClip using the current operating system's normal package manager. On macOS, use the HotClip CLI source workflow in the skill; the official GUI DMG is currently Apple Silicon only. On Windows, use winget for prerequisites. Do not use or create a repository bootstrap script. No Ollama or LLM endpoint is required for transcript-led highlight selection.
5. Report the installation path, runtime setup completed, and any remaining platform limitations. Mention if the agent must restart or start a new session to load the skill.

If this skill already exists, compare it with the requested repository version before changing anything. Preserve unrelated skills and user data.
