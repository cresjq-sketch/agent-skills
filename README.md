# Agent Skills Collection

个人技能集中仓库。每个技能独立放在 `skills/<skill-name>/`，包含 `SKILL.md` 及其所需脚本、模板和参考资料。

## 技能与单独安装说明

| 技能 | 技能目录 | 发给智能体的安装说明 |
|---|---|---|
| `auto-video-editor-windows` | [`skills/auto-video-editor-windows`](skills/auto-video-editor-windows) | [`install-auto-video-editor-windows.md`](install-auto-video-editor-windows.md) |
| `zhenmei-mobile` | [`skills/zhenmei-mobile`](skills/zhenmei-mobile) | [`install-zhenmei-mobile.md`](install-zhenmei-mobile.md) |

每份 `install-<技能名>.md` 都只针对一个技能。把对应文件的内容或 GitHub 链接发给智能体即可；智能体按说明使用当前平台的技能安装方式，只安装所选目录。

## 新增技能

1. 新建 `skills/<skill-name>/SKILL.md`，使用 Agent Skills frontmatter（至少包含唯一的 `name` 和清楚的 `description`）。
2. 把运行需要的脚本、模板、参考资料放在同一目录，并在 `SKILL.md` 中说明其用途。
3. 新增一份独立的 `install-<skill-name>.md`，明确仓库路径、技能目录和当前智能体的安装要求。
4. 更新上面的索引；确认没有令牌、密码、临时文件或用户数据后提交并推送。
