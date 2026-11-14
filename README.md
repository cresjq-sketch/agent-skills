# Agent Skills Collection

一个集中维护、跨智能体安装的个人技能仓库。所有技能以标准 `SKILL.md` 为入口，新增技能只需放到 `skills/<skill-name>/`。

## 当前技能

| 技能 | 目录 | 用途 |
|---|---|---|
| `auto-video-editor-windows` | [`skills/auto-video-editor-windows`](skills/auto-video-editor-windows) | Windows 本地视频精剪；按素材情况动态确定高光条数 |
| `zhenmei-mobile` | [`skills/zhenmei-mobile`](skills/zhenmei-mobile) | 真美知识库取材、文章创作与保存草稿 |

技能目录可包含 `SKILL.md` 及其脚本、模板和参考资料。不要提交访问令牌、密码、用户数据或生成的视频。

## Windows 安装

1. 下载此仓库 ZIP 并解压，或克隆仓库。
2. 在 PowerShell 运行：

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\install.ps1
   ```

脚本自动发现 Codex、Claude Code、Gemini CLI、Cursor、OpenCode 的用户级技能目录，并安装所有仓库技能；未发现时安装到 `%USERPROFILE%\.agents\skills`。指定技能可用 `-Skills auto-video-editor-windows,zhenmei-mobile`。

当选择 `auto-video-editor-windows` 时，安装器还会通过 winget 安装 Git、Node.js LTS、FFmpeg，下载 HotClip 和其本地语音识别模型。无需 Ollama 或云端大模型。`zhenmei-mobile` 运行时仍需真美服务端、用户自己的有效 API Token，以及文中列出的排版/改写技能；安装器不会替用户创建或保存凭证。

## 新增技能

1. 新建 `skills/<skill-name>/SKILL.md`，并确保 frontmatter 中有唯一的 `name` 与清晰的 `description`。
2. 将该技能运行所需的脚本、模板、参考资料放在同一目录。
3. 更新上面的技能目录表；如需额外安装软件，在 `install.ps1` 中按技能目录添加明确的依赖安装逻辑。
4. 检查没有凭证、临时文件或用户内容后提交并推送。

安装器会扫描 `skills/` 下所有含 `SKILL.md` 的一级目录，因此以后新增技能无需改动安装目标识别逻辑。
