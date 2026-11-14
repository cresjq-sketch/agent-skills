---
name: zhenmei-mobile
description: 真美发布链路的手机端版：主题由用户设定（未设定则按种子词从真美知识库 API 自动选题，并同步生成配图）→ 通过真美系统的知识库检索 API（服务端对接 AnythingLLM，http://115.29.220.203:3001）取素材创作 → humanizer 去AI味优化 → gzh-design 公众号排版 → 存真美草稿。相关技能（humanizer、gzh-design）未安装时自动安装；真美 API Token 只向用户索取一次并记录，失效时明确提示。AnythingLLM 的 Key 只存在真美服务器，本端不需要。
---

# 真美手机端发布（真美知识库 API 取素材 → 创作 → humanizer → 公众号排版 → 真美草稿）

把「真美知识库（AnythingLLM）里的资料」变成「一篇去AI味、可发公众号、并存进真美的文章」。六段链路：

1. **定主题** —— 用户设定；未设定则用种子词查知识库自动选题，**该分支同时自动生成配图**；
2. **取素材** —— 调真美系统的知识库检索 API（`POST /api/skill/knowledge/search`），服务端负责对接 AnythingLLM；
3. **创作** —— 基于素材成文（Markdown 中间稿）；
4. **humanizer 优化** —— 调用 humanizer 技能做「去AI味·人味化」改写；
5. **公众号排版** —— 用 gzh-design 产出可直接粘贴公众号编辑器的 HTML；
6. **保存** —— 语义 HTML 写入真美「文章管理」草稿（默认草稿，不自动发布）。

> 本 skill 是 `zhenmei-article-manager` 的手机端变体：知识库从 ima 换成**真美知识库 API**（AnythingLLM 由真美服务端对接，本端不经手 Key），中间多了 **humanizer** 环节，其余规则（创作边界、两套 HTML 格式、真美接口实测细节）与其保持一致。

---

## 0. Token 管理（只索取一次，失效即提示）

全程只需要**真美 API Token** 一个凭证（知识库检索和写草稿都用它）：

- **首次使用**时，通过**私密输入**向用户索取真美 API Token（在真美网页登录 →「系统设置 → WorkBuddy 文章 Skill」生成，有效期 7 天，`zmt_` 前缀）。
- 取得后**立即写入**（一行纯 Token，不回显、不进日志）：

  ```
  ~/.workbuddy/secrets/zhenmei.token
  ```

  （与 `zhenmei-article-manager` 共用同一文件；写入后 `chmod 600`。**后续所有会话直接读这个文件，不再重复索取。**）
- **失效处理**：任何请求返回 401 / 403 → **停止重试**，明确提示「真美 Token 已失效，请重新生成」，用户重新提供后覆写该文件再继续。403 表示账号或 Token 无权执行此操作，不要尝试绕过。
- **用户拒绝提供或无法提供**：如实说明「没有 Token 无法调用真美知识库与写草稿」，让用户选择改用自己提供的资料直接创作。**不得凭空编造素材，也不得假装检索过。**
- Token 只放请求头 `Authorization: Bearer <token>`；不进 URL、查询参数、日志或文章内容。
- **手机端无文件系统时**：本次会话私密输入取得、仅本次使用，并在结束时提醒用户「下次在桌面端运行一次以便持久化 Token」。

> AnythingLLM 的 API Key **不出现在本端**：它配置在真美后台（设置 → AnythingLLM），由真美服务端持有并调用 `http://115.29.220.203:3001`。

---

## 1. 定主题

- **用户设定了主题** → 直接用，进入第二步。
- **用户没设定主题** → 走「自动选题」分支：
  1. 按 Token 规则连上真美知识库 API（见第二步）；
  2. 用**内置种子词**逐个检索：`亲子沟通`、`情绪管理`、`青春期`、`学习习惯`、`亲子关系修复`、`家庭氛围`（每个词一次 API 调用，取返回条目的标题作选题线索）；
  3. 基于**实际返回结果**拟 1 个选题（可附 1-2 个备选），**并向用户说明自动选了什么、依据是哪些条目**；
  4. 该分支**默认自动生成配图**（见第六步图片规则），交付时说明。
- 选题基于检索结果，不凭空编「知识库里有 XX」。

---

## 2. 取素材：真美知识库检索 API（服务端对接 AnythingLLM）

### 接口契约（实测，2026-11-06 已上线）

- **端点**：`POST https://zhenmei.ziykj.net/api/skill/knowledge/search`
- **请求头**：`Authorization: Bearer <真美Token>`、`Content-Type: application/json`、`Accept: application/json`
- **请求体**：`{"topic": "<主题，必填>", "limit": 10}`（limit 1–20，缺省 10）
- **成功 200**（实测顶层字段）：

  ```json
  { "topic": "亲子沟通", "source": "anythingllm", "count": 12,
    "items": [ { "id": "anythingllm:...", "title": "文档标题", "content": "知识片段正文（可达数千字）", "source": "来源说明" } ] }
  ```

  - `source` 取值 `anythingllm | ima | local | mixed`；`count` 是检索池大小。
  - 实测 `limit` 未必截断 `items`（可能返回全部 count 条）：**自行按相关度取前 N 条**，不要把上万字全部塞进创作上下文。
  - item 的 `id`/`source` 只用于记录来源，不写进文章。
- **错误**：`401` `{"error":"未登录"}` 或 Token 无效/过期（→ 按 Token 失效流程处理）；`403` Token 无权访问该路由；`400` topic 为空/超长；`502` 服务端知识库配置问题（`error` 字段有人话说明，如「请先完成 AnythingLLM 配置」——如实转告用户去真美后台配置）。

### 服务端前置（真美系统侧，已实现）

- 路由用 `createSourceAwareKnowledgeRetriever`（`server/src/knowledge/retrieval.ts`）按主题检索，只回 `title/content/source` 等内容字段，**不回任何 Key 或配置**；路由加入 `server/src/auth/skill-api-token.ts` 的 `allowedSkillTokenRoutes` 白名单。
- 真美后台须配置 AnythingLLM（设置 → AnythingLLM：地址 `http://115.29.220.203:3001`、API Key、workspace slug；检索策略建议 `anythingllm_only` 或 `all_sources`）。

### 检索方式与使用边界

- 主题作为 `topic` 传入；检索结果不理想时，用「主题词 + 3~5 个近义/相关词」再试几组，别只调一次就下结论。
- **只使用 items 里实际返回的内容作为事实来源**；素材里没有的统计、案例、数据一律不编造。
- 记录条目 `title`/`source`（只用于完成反馈里向用户说明素材来源，**不写进文章**）。
- 素材是养料：可借鉴角度、结构、痛点，但**成文必须重写/原创**，不要整段照搬。`items` 为空时如实说「知识库里没有相关内容」，建议换关键词或由用户补充资料。

---

## 3. 创作

1. 基于素材产出**标题 + Markdown 正文**（中间稿留档，最终提交真美前按第六步转语义 HTML）。
2. 标题与正文引号一律用**中文弯引号** `“”`，不用直引号 `"`。
3. 未经素材或用户确认的事实、数字、疗效、购买/体验类表述一律不写。
4. 正文里**不加**「素材来源 / 本文参考了…」落款（来源只在交付反馈里说明）。
5. 文章结尾自然收束（结语/金句/互动引导），不挂声明。
6. 用户对体裁、字数、风格、受众有要求时按其要求来；字数上限只在其明说时生效。

---

## 4. humanizer 优化（去AI味·人味化）

创作完成后，**必须**过一遍 humanizer，再进入排版。

### 技能获取

- 若会话中已有 **humanizer** 技能 → 直接加载调用。
- 未安装 → **自动搜索安装**（用户已预授权本 skill 自动安装相关技能）：用平台的技能搜索/安装能力搜 `humanizer` 并安装；安装前按平台安全检查流程审一遍其 SKILL.md 与附带文件。
- **搜不到名为 humanizer 的技能时**（安装来源尚未接入的兜底）：使用下面的**内置人味化改写规则**就地完成优化，并在交付反馈里注明「本次用的是内置去AI味规则，不是 humanizer 技能」。

### 内置人味化改写规则（兜底）

逐段改写，不改变事实与核心观点：

- **去模板腔**：删掉「首先/其次/总之」「值得注意的是」「不可否认」这类套话开头；段落长短错落，避免每段等长、句式雷同。
- **口语化**：书面长句拆短；多用具体场景和画面代替抽象概括（「孩子发脾气时」好过「在情绪管理情境中」）。
- **人味细节**：保留/补上生活化例子、真实对话感；允许适度的口语词和破折号、省略号，但不堆砌。
- **不制造焦虑、非羞辱**：保持温暖专业，不给家长贴标签，不夸大问题。
- **保持事实边界**：不新增素材里没有的数字、结论、疗效承诺；引号仍用中文弯引号 `“”`。
- 改写后输出仍是 **Markdown**，与中间稿同名加 `_人味` 后缀留档。

### humanizer 技能（已接入）

- **已安装于** `~/.workbuddy/skills/humanizer/`（来源：`https://github.com/Aboudjem/humanizer-skill`，纯 Markdown 提示词技能：55 个 AI 痕迹模式 + 5 种声音风格，零脚本、零网络调用，手机端同样可用）。
- **调用方式**：加载其 `SKILL.md`，用 **rewrite 模式**对第三步的 Markdown 稿整体改写：
  - `--voice warm` 为默认（贴合亲子/心理/教育内容的温暖语气）；观点复盘类可用 `professional`；按文章气质定，不硬套。
  - 中文改写时参考其 `references/patterns.zh.md`（中文 AI 痕迹模式附录）。
  - 可加 `--score` 在改写前后各测一次 AI 痕迹分（0-100，越低越人味），把前后分差写进完成反馈。
- **两条硬性例外（覆盖 humanizer 的默认规则）**：
  1. **P17（弯引号）不适用**：本链路的稿件**必须保留中文弯引号 `“”`**，绝不能按 humanizer 的 P17 规则改成直引号。
  2. **不新增事实**：humanizer 的「Concretizer pass / 具体化」只能用**素材里已有**的细节，不得编造数字、日期、案例（与其自身「No fabrication」原则一致）。
- **产物**：改写后仍是 Markdown，存 `{原文件名}_人味.md` 留档；后续排版与真美写入都用这份改写稿。
- 若当前设备未安装该技能 → **自动安装**（用户已预授权）：优先用平台的技能搜索/安装能力；搜不到时从 `https://github.com/Aboudjem/humanizer-skill` 克隆，把其中 `skills/humanizer/` 目录复制到用户级技能目录（安装前按平台安全检查流程审一遍，该仓库已做过一次审计：纯 Markdown、无脚本无网络，结论安全）。

---

## 5. 公众号排版（gzh-design）

用用户级 skill **`gzh-design`**（公众号排版引擎，提示词工作流）：

- **未安装 → 自动安装**（用户已预授权）：搜索安装 `gzh-design`，安装后读其 `SKILL.md`、`references/theme-index.md` 确认可用。
- ⚠️ 认准 **`gzh-design`**，**不要用 `gzh-design-skill`**（空壳，样式非内联、跑不起来）。
- 流程固定：读 `theme-index.md` 取主题清单 → **用户选择制**（用户没指定排版主题时列全部主题让用户选，不替用户定；用户明说「直接排/一键」才自动选；手机端一次最多给 4 个候选）→ 读该主题 `theme-{英文标识}.md` + `common-components.md` → 按文章类型配方装配。
- 产物：`{原文件名}_排版_{主题中文名}({英文标识}).html`，**纯 `<section>…</section>` 片段**（不带 DOCTYPE/html/head/body），内层文字必须 `<span leaf>` 包裹，样式全内联。
- **强制校验**（桌面端）：`python3 ~/.workbuddy/skills/gzh-design/scripts/validate_gzh_html.py "<生成的.html>"`，ERROR 与半角标点 WARNING 清零；再跑 `wrap_preview.py` 出 `_预览.html`。
- **手机端/无 shell**：手工装配合规片段，但**必须如实声明「未跑校验」**，不要假装校验通过，也不要改用 `gzh-design-skill` 绕行。

---

## 6. 保存到真美（默认：创建草稿）

### 正文转换：Markdown → 真美语义 HTML（必做）

- `bodyFormat` 一律 `"html"`（富文本渲染）；`"markdown"` 会落进「旧版 Markdown」框，**不用**。
- 用本 skill 自带脚本转换（不要手写 HTML）：

  ```bash
  python3 <本skill目录>/scripts/md_to_zhenmei_html.py \
    "<文章.md>" --quote "<开头引言卡金句>" --sign "大强｜心理咨询师"
  ```

- 产出 `<同名>.zhenmei.html` 即提交的 `body`：只含 `h2/h3/p/strong/em/blockquote/ol/ul/li`，**零样式**（无 style/class/span leaf/style 标签/div/section）——与公众号排版稿（全内联样式）正好相反，**切勿互相顶替**。
- 首个 `#` H1 自动剔除；直引号自动转弯引号；结尾默认互动引导。
- **手机端无 shell**：按上述标签清单手工转换，转换后自查一遍标签集合，并在反馈中说明「手工转换、未跑脚本自检」。

### 写入流程（继承实测细节）

1. 用最终确认的标题和正文，不擅自改写。
2. 询问未说明的选项：简介（用户提供 / 调 `POST /api/articles/summarize`）、图片、AI 示例评论（默认不生成）。
3. **图片规则**：
   - **自动生成配图**的情形：① 用户未提供主题的自动选题分支；② 用户明确要求配图。用平台的图像生成能力生成，主题贴合文章内容。
   - 有压缩环境时必须先压缩：`<带 Pillow 的解释器> <本skill目录>/scripts/shrink_image.py "<生成图.png>" --target-kb 10 --crop-bottom-pct 8 --max-width 1200 --out "<同名>.cover.webp" --json`（目标 **10KB**，裁掉右下角水印；确认 JSON `ok:true`，达不到如实报告实际体积）。必须用带 Pillow 的解释器。
   - 无压缩环境（手机端）：如实体积未压缩，让用户决定是否仍上传；上传用 `POST /api/article-media/upload`（二进制，头：`Content-Type: application/octet-stream`、`X-Media-Kind: image`、`X-Media-Name`（URL 编码）、`X-Media-Content-Type`）。只把响应中的 `url` 用作封面/正文媒体。
4. 创建草稿：`POST /api/articles`，请求头 `Authorization: Bearer <真美token>`。JSON 结构：

   ```json
   {
     "title": "文章标题",
     "summary": "文章简介",
     "coverUrl": "",
     "body": "<p>文章正文</p>",
     "bodyFormat": "html",
     "contentType": "image_text",
     "media": [],
     "tags": [],
     "comments": [],
     "displayMetrics": { "likes": 0, "shares": 0, "hearts": 0, "comments": 0 }
   }
   ```

   - **`media` 是字符串数组**（URL 字符串），不要传对象数组；封面放 `coverUrl`。
   - `comments` 是对象数组（`{name, content, generated: true}`）；仅在用户明确选择时调 `POST /api/articles/generate-comments`。
   - **标签必须在创建前一次确认**（Token 不能更新已有草稿；历史惯用标签如「亲子」创建前问是否沿用）。
   - 创建成功只返回 `{ "id": "..." }`，**必须**再 `GET /api/articles` 按 id 核对 `status == "draft"`。
5. 接口能力边界：该 Token **不能更新/删除**已有草稿；事后修改任何字段只能重建（重建前必须取得用户同意，旧稿由用户在后台手动删）。Token 不能发布文章；用户要发布时说明需在真美系统内自行发布。

---

## 完成反馈

简洁报告：

- 文章标题、主题来源（用户设定 / 自动选题+依据）；
- 素材来源（真美知识库 API 返回的 `source` 类型与条目标题）。
- humanizer 执行方式（技能 / 内置兜底）；
- 公众号排版稿路径与所用排版主题（并提示「打开 `_预览.html` → 复制到公众号 → 粘贴」；未跑校验时如实声明）;
- 真美草稿是否创建成功（含核对结果）、是否配图（自动/用户要求/未压缩如实说明）。
