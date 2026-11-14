# zhenmei-mobile · 真美手机端发布 Skill

Agent Skill（原版为 WorkBuddy 用户级 Skill）：把「真美知识库（AnythingLLM）里的资料」变成「一篇去 AI 味、可发公众号、并存进真美草稿的文章」。为手机端设计，但桌面端同样可用。

## 链路

```
定主题（用户设定 / 种子词自动选题+自动配图）
  → 真美知识库检索 API 取素材（服务端对接 AnythingLLM）
  → 创作（Markdown 中间稿）
  → humanizer 去AI味改写（GitHub: Aboudjem/humanizer-skill）
  → gzh-design 公众号排版（全内联样式 <section> 片段）
  → 存真美草稿（语义 HTML，bodyFormat: "html"）
```

## 前置条件

| 依赖 | 说明 |
|---|---|
| 真美系统 | 需已实现 `POST /api/skill/knowledge/search`（契约见 SKILL.md 第二节）并在「系统设置 → AnythingLLM」配好 AnythingLLM（API Key 只存服务端） |
| 真美 API Token | 真美网页 →「系统设置 → WorkBuddy 文章 Skill」生成（7 天有效，`zmt_` 前缀）；首次使用时私密输入，存 `~/.workbuddy/secrets/zhenmei.token` |
| gzh-design 技能 | 公众号排版引擎；未安装时本 skill 会提示自动安装 |
| humanizer 技能 | 来源 [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill)；未安装时自动安装（含中文 AI 痕迹模式附录） |
| Python（可选） | `scripts/md_to_zhenmei_html.py`（Markdown→真美语义 HTML）与 `scripts/shrink_image.py`（配图压缩到 10KB，需 Pillow） |

## 安装

```bash
从集中仓库安装：

```powershell
.\install.ps1 -Skills zhenmei-mobile
```

技能源目录：`skills/zhenmei-mobile/`。原始独立仓库：[cresjq-sketch/zhenmei-mobile](https://github.com/cresjq-sketch/zhenmei-mobile)。
```

也可在支持 Agent Skills 标准的智能体中，将此目录复制到对应技能目录后加载。`tokens/` 目录运行时自动创建，不入库。

## 安全设计

- AnythingLLM 的 API Key 只存在真美服务端，本端不经手任何 Key。
- 真美 Token 只放 `Authorization` 请求头，不进 URL / 日志 / 文章内容；401/403 时停止重试并提示重新生成。
- 知识库检索接口只返回内容片段（title/content/source），不返回任何配置信息。

## 目录

```
SKILL.md                      # 完整链路指令（含接口契约与错误处理）
scripts/md_to_zhenmei_html.py # Markdown → 真美语义 HTML（零样式 h2/h3/p/…）
scripts/shrink_image.py       # 配图压缩（保画质二分压缩 + 裁水印）
```
