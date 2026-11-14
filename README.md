# Agent Skills Collection

个人技能集中仓库。每个技能独立放在 `skills/<skill-name>/`，包含 `SKILL.md` 及其所需脚本、模板和参考资料。用户选择后，由当前智能体通过自己的技能安装能力安装指定目录。

## 技能目录

| 技能 | 目录 | 用途 |
|---|---|---|
| `auto-video-editor-windows` | [`skills/auto-video-editor-windows`](skills/auto-video-editor-windows) | Windows 本地视频剪辑；根据素材质量和时长动态确定高光数量 |
| `zhenmei-mobile` | [`skills/zhenmei-mobile`](skills/zhenmei-mobile) | 真美知识库取材、文章创作与保存草稿 |

## 如何让智能体安装一个技能

直接告诉当前智能体，例如：

> 请从 `https://github.com/cresjq-sketch/agent-skills` 只安装 `skills/zhenmei-mobile`。使用你当前平台的原生技能安装方式，安装到当前智能体的用户级技能目录；不要下载整个仓库，不要运行仓库安装脚本。安装后核对目录中有 `SKILL.md` 及该技能需要的配套文件，并告诉我何时可以使用。

把 `zhenmei-mobile` 换成表格中的其他技能名即可。智能体应根据自身平台选择安装方式和技能目录；不要把一个技能安装到其他未指定的智能体里。若目标已存在，先检查现有版本和差异，再处理更新。

Codex 示例：使用其内置 `skill-installer`，仓库为 `cresjq-sketch/agent-skills`，路径为 `skills/<skill-name>`。其他智能体使用各自支持的技能安装方式；若没有专用安装器，则由智能体只读取所选目录并写入当前智能体的技能目录。

## 新增技能

1. 新建 `skills/<skill-name>/SKILL.md`，使用 Agent Skills frontmatter（至少包含唯一的 `name` 和清楚的 `description`）。
2. 把运行需要的脚本、模板、参考资料放在同一目录，并在 `SKILL.md` 中说明其用途。
3. 更新上面的技能目录表；确认没有令牌、密码、临时文件或用户数据后提交并推送。

仓库只管理技能源文件。依赖软件由智能体按所选技能的说明、当前操作系统和用户任务逐项处理；安装一个技能不应自动安装其他技能或无关软件。
