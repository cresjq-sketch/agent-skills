#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown -> 真美「图文内容」HTML（语义 HTML）

真美系统 POST /api/articles 的 body 支持两种格式：
  - bodyFormat="markdown"  -> 后台显示在「图文内容（旧版 Markdown）」框（旧版，纯文本）
  - bodyFormat="html"      -> 后台按富文本渲染（推荐）

本脚本把文章 Markdown 转成真美期望的**语义 HTML**：
只保留 h2 / h3 / p / strong / em / blockquote / ol / ul / li，
**不带** style 属性、不带 <span leaf>、不带 <style> 标签、不带目录表。

（这与公众号排版稿不同：公众号稿必须全内联样式；真美后台自己负责样式，
  只要你给它干净的语义标签。二者不能混用。）

用法：
    python3 md_to_zhenmei_html.py 文章.md \\
        --quote "先接住情绪，再处理事情。" \\
        --sign "大强｜心理咨询师" \\
        --out 文章.zhenmei.html

    python3 md_to_zhenmei_html.py 文章.md --quote "…" --stdout     # 直接打印
    python3 md_to_zhenmei_html.py 文章.md --no-signature            # 不加结尾互动句

默认结尾会追加一句互动引导（可用 --signature 覆盖，或 --no-signature 关掉）。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

DEFAULT_SIGN = "大强｜心理咨询师"
DEFAULT_SIGNATURE = (
    "如果你觉得今天这篇有收获，欢迎<strong>点赞、在看、转发</strong>三连，我们下篇见。"
)


def smart_quotes(text: str) -> str:
    """把成对的直引号 " 转成中文弯引号 “ ”。逐行左右交替。"""
    out_lines = []
    for line in text.split("\n"):
        buf = []
        open_q = True
        for ch in line:
            if ch == '"':
                buf.append("“" if open_q else "”")
                open_q = not open_q
            else:
                buf.append(ch)
        out_lines.append("".join(buf))
    return "\n".join(out_lines)


def inline(text: str) -> str:
    """行内标记 -> HTML。先转义，再做 **strong** / *em*。"""
    text = smart_quotes(text)
    text = html.escape(text, quote=False)
    # **bold** 必须先于 *em*
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+?)`", r"<code>\1</code>", text)
    return text


def strip_h1_title(md: str) -> str:
    """去掉首个 H1（标题另有 title 字段，不进正文）。"""
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip():
            if ln.startswith("# "):
                lines.pop(i)
            break
    return "\n".join(lines)


def convert(md: str) -> str:
    md = strip_h1_title(md)
    lines = md.split("\n")

    blocks: list[str] = []
    para: list[str] = []
    lst: list[str] = []
    lst_kind: str | None = None
    quote: list[str] = []

    def flush_para():
        if para:
            blocks.append(f"<p>{inline(''.join(para).strip())}</p>")
            para.clear()

    def flush_list():
        nonlocal lst_kind
        if lst:
            tag = "ol" if lst_kind == "ol" else "ul"
            items = "".join(f"<li>{inline(x)}</li>" for x in lst)
            blocks.append(f"<{tag}>{items}</{tag}>")
            lst.clear()
        lst_kind = None

    def flush_quote():
        if quote:
            inner = "".join(quote)
            blocks.append(f"<blockquote>{inner}</blockquote>")
            quote.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            flush_list()
            flush_quote()
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            flush_para()
            flush_list()
            flush_quote()
            continue  # 分隔线不进真美正文

        m_h = re.match(r"^(#{2,6})\s+(.*)$", stripped)
        if m_h:
            flush_para()
            flush_list()
            flush_quote()
            level = len(m_h.group(1))
            blocks.append(f"<h{level}>{inline(m_h.group(2).strip())}</h{level}>")
            continue

        if stripped.startswith(">"):
            flush_para()
            flush_list()
            quote.append(f"<p>{inline(stripped[1:].strip())}</p>")
            continue

        m_ol = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m_ol:
            flush_para()
            flush_quote()
            if lst_kind != "ol":
                flush_list()
                lst_kind = "ol"
            lst.append(m_ol.group(1).strip())
            continue

        m_ul = re.match(r"^[-*+]\s+(.*)$", stripped)
        if m_ul:
            flush_para()
            flush_quote()
            if lst_kind != "ul":
                flush_list()
                lst_kind = "ul"
            lst.append(m_ul.group(1).strip())
            continue

        if quote:
            flush_quote()
        para.append(stripped)

    flush_para()
    flush_list()
    flush_quote()

    body = "".join(blocks)
    # 相邻 blockquote 合并
    body = re.sub(r"</blockquote><blockquote>", "", body)
    return body


def build(md_path: Path, quote: str | None, sign: str, signature: str | None) -> tuple[str, str]:
    """返回 (title, html_body)"""
    md = md_path.read_text(encoding="utf-8")
    title = ""
    for ln in md.split("\n"):
        if ln.strip():
            title = ln.lstrip("#").strip()
            break

    parts: list[str] = []
    if quote:
        card = f"<p>{inline(quote)}</p>"
        if sign:
            card += f"<p>—— {inline(sign)}</p>"
        parts.append(f"<blockquote>{card}</blockquote>")
    parts.append(convert(md))
    if signature:
        parts.append(f"<p>{signature}</p>")

    return title, "".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> 真美图文内容（语义 HTML）")
    ap.add_argument("md", help="Markdown 文章路径（首个 H1 作为 title，不进正文）")
    ap.add_argument("--quote", default=None, help="开头引言卡的金句；给了才生成引言卡")
    ap.add_argument("--sign", default=DEFAULT_SIGN, help=f"引言卡落款（默认 {DEFAULT_SIGN}）")
    ap.add_argument(
        "--signature",
        default=DEFAULT_SIGNATURE,
        help="结尾互动句；传空字符串则不加",
    )
    ap.add_argument("--no-signature", action="store_true", help="不加结尾互动句")
    ap.add_argument("--out", default=None, help="输出文件路径（默认 <同名>.zhenmei.html）")
    ap.add_argument("--stdout", action="store_true", help="只打印到标准输出，不写文件")
    ap.add_argument("--print-title", action="store_true", help="额外打印一行 title")
    args = ap.parse_args()

    md_path = Path(args.md)
    if not md_path.is_file():
        print(f"❌ 找不到文件：{md_path}", file=sys.stderr)
        return 2

    signature = None if args.no_signature else (args.signature or None)
    title, body = build(md_path, args.quote, args.sign, signature)

    if args.print_title:
        print(f"TITLE\t{title}")

    if args.stdout:
        print(body)
        return 0

    out = Path(args.out) if args.out else md_path.with_suffix("").with_name(
        md_path.stem + ".zhenmei.html"
    )
    out.write_text(body, encoding="utf-8")

    # 自检
    problems = []
    for bad in ("style=", "<style", 'class="', "<span", "<h1", "<div", "<section"):
        if bad in body:
            problems.append(bad)
    print(f"✓ 已生成：{out}")
    print(f"  title      : {title}")
    print(f"  body 字符数 : {len(body)}")
    print(f"  标签统计    : " + ", ".join(
        f"{t}={body.count('<' + t)}" for t in ("h2", "h3", "p", "blockquote", "ol", "ul", "strong", "em")
        if body.count('<' + t)
    ))
    print("  格式自检    : " + ("⚠️ 含不该出现的 " + " / ".join(problems) if problems else "干净（无 style / class / span / h1 / div / section）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
