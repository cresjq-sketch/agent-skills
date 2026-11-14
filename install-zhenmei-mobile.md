# Install `zhenmei-mobile` in the current agent

This file is the installation request for the single `zhenmei-mobile` skill.

## Source

- Repository: `cresjq-sketch/agent-skills`
- Skill directory: `skills/zhenmei-mobile`
- Branch: `main`

## Instructions for the agent receiving this file

1. Use your platform's native skill installer for the repository path above. In Codex, use the built-in `skill-installer` with repository `cresjq-sketch/agent-skills` and path `skills/zhenmei-mobile`.
2. Install only this skill into the current agent's user-level skill directory. Fetch the complete skill directory, including its `scripts/` files, and preserve their relative paths. Do not fetch other skills or the whole repository.
3. Inspect the installed `SKILL.md` and confirm both bundled scripts, `scripts/md_to_zhenmei_html.py` and `scripts/shrink_image.py`, are present and the skill is discoverable.
4. Do not create, request, or copy a TrueMe API token during installation. Never put credentials in the repository or skill directory. The token is needed only when the user later runs a TrueMe publishing task.
5. Report the installation path and verification result. Mention if the agent must restart or start a new session to load the skill.

If this skill already exists, compare it with the requested repository version before changing anything. Preserve unrelated skills and user data.
