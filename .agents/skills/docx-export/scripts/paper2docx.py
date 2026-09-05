#!/usr/bin/env python3
"""把 Typst / LaTeX 论文源码导出为 Word DOCX（华为杯等需要 Word 交稿的赛事）。

流程：
1. 识别 paper/ 下的 main.typ 或 main.tex，按 #include / \\input 顺序收集正文章节。
2. 把正文里引用的 PDF 图转成同名 PNG（Word 不支持 PDF 图片）。
3. 调用 pandoc（typst/latex reader -> docx writer），公式输出为可编辑 OMML。
4. 用 python-docx 补上标题 / 摘要 / 关键词页，并把中文字体设为 宋体 / 黑体。
5. 若有 soffice，顺手转一份 PDF 用于渲染抽检并统计页数。

用法：
    python paper2docx.py --paper paper --out paper/main.docx
    python paper2docx.py --paper paper --title "论文题目" --abstract-file abstract.txt \\
        --keywords "关键词1;关键词2;关键词3"
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor
except ImportError:  # pragma: no cover
    sys.exit("缺少 python-docx：pip install python-docx")

PDF2PNG_LUA = r"""
-- 把 image 的 .pdf 源改为同名 .png（由 paper2docx.py 预先生成）
function Image(el)
  if el.src:match("%.pdf$") or el.src:match("%.PDF$") then
    el.src = el.src:gsub("%.[pP][dD][fF]$", ".png")
  end
  return el
end

local PAGE_BREAK = pandoc.RawBlock("openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

-- typst #pagebreak() -> Div.page-break；latex \newpage / \clearpage -> RawBlock；本脚本生成的摘要页 -> Div.pagebreak
function Div(el)
  if el.classes:includes("page-break") or el.classes:includes("pagebreak") then
    return PAGE_BREAK
  end
end

function RawBlock(el)
  if el.format == "latex" and (el.text:match("\\newpage") or el.text:match("\\clearpage")) then
    return PAGE_BREAK
  end
end

-- 图/表题自动编号：“图 N  xxx” / “表 N  xxx”（Typst/LaTeX 编译时由排版引擎自动加，pandoc 不加）
local fig_n, tab_n = 0, 0

local function prefix_caption(cap, label)
  if cap == nil or cap.long == nil or #cap.long == 0 then
    return cap
  end
  local first = cap.long[1]
  if first.t == "Plain" or first.t == "Para" then
    first.content:insert(1, pandoc.Str(label))
    first.content:insert(2, pandoc.Space())
    first.content:insert(3, pandoc.Space())
  end
  return cap
end

function Figure(el)
  fig_n = fig_n + 1
  el.caption = prefix_caption(el.caption, "图 " .. fig_n)
  return el
end

function Table(el)
  tab_n = tab_n + 1
  el.caption = prefix_caption(el.caption, "表 " .. tab_n)
  return el
end
"""

TITLE_MARK = "\u200b\u200bTITLE\u200b\u200b"
ABSTRACT_MARK = "\u200b\u200bABSTRACT\u200b\u200b"

INCLUDE_TYP = re.compile(r'#include\s*\(?\s*"([^"]+)"\s*\)?')
INCLUDE_TEX = re.compile(r'\\(?:input|include)\{([^}]+)\}')
IMAGE_TYP = re.compile(r'image\(\s*"([^"]+\.pdf)"', re.I)
IMAGE_TEX = re.compile(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+\.pdf)\}', re.I)
PLACEHOLDER = re.compile(r'\[(论文标题|学校名称|参赛队号|成员 ?[A-C]|关键词\d|中文摘要内容[^\]]*)\]')


@dataclass
class FrontMatter:
    title: str = ""
    abstract: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def detect_engine(paper: Path) -> tuple[str, Path]:
    if (paper / "main.typ").exists():
        return "typst", paper / "main.typ"
    if (paper / "main.tex").exists():
        return "latex", paper / "main.tex"
    sys.exit(f"{paper} 下找不到 main.typ 或 main.tex")


def collect_sections(engine: str, main: Path) -> list[Path]:
    text = main.read_text(encoding="utf-8")
    pattern = INCLUDE_TYP if engine == "typst" else INCLUDE_TEX
    if engine == "latex" and "\\begin{document}" in text:
        # 序言区里的 \input 通常是宏定义的附录 / 参考文献，排到正文之后
        preamble, body = text.split("\\begin{document}", 1)
        text = body + "\n" + preamble
    out: list[Path] = []
    for m in pattern.finditer(text):
        rel = m.group(1)
        p = main.parent / rel
        if engine == "latex" and not p.suffix:
            p = p.with_suffix(".tex")
        if p.exists():
            out.append(p)
        else:
            print(f"[warn] include 目标不存在，跳过: {rel}")
    return out


def extract_front_matter(engine: str, main: Path) -> FrontMatter:
    """从模板 main 文件中尽力抽取标题 / 摘要 / 关键词；抽不到就留空让 CLI 参数补。"""
    fm = FrontMatter()
    text = main.read_text(encoding="utf-8")
    if engine == "typst":
        m = re.search(r'#set document\(\s*title:\s*"([^"]*)"', text)
        if m:
            fm.title = m.group(1)
        lines = text.splitlines()
        start = next((i for i, l in enumerate(lines) if '要：' in l and '摘' in l), None)
        end = next((i for i, l in enumerate(lines) if '关键词：' in l), None)
        if start is not None and end is not None and end > start:
            noise = re.compile(r'^\s*(v\(|block\[|#set\b|pagebreak|\]\s*$)')
            kept = [l for l in lines[start + 1:end] if not noise.match(l)]
            body = '\n'.join(l.strip() for l in kept).strip()
            if body.startswith('[') and body.endswith(']'):
                body = body[1:-1].strip()
            fm.abstract = [p.strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
            kw_line = lines[end].split('关键词：]', 1)[-1]
            fm.keywords = [k.strip() for k in re.findall(r'\[([^\]]+)\]', kw_line) if k.strip()]
    else:
        m = re.search(r'\\heiti\\bfseries\s*(.+?)\}%', text)
        if m:
            fm.title = m.group(1).strip()
        m = re.search(r'要：\}[^\n]*\n(?:\s*\\end\{center\}\s*\n)?(.*?)\\par\s*\n', text, re.S)
        if m:
            fm.abstract = [p.strip() for p in re.split(r'\n\s*\n', m.group(1).strip()) if p.strip()]
        m = re.search(r'关键词：\}(.*?)\\par', text)
        if m:
            fm.keywords = [k.strip() for k in re.split(r'\\quad', m.group(1)) if k.strip()]
    return fm


def convert_pdf_figures(engine: str, sections: list[Path], paper: Path) -> list[Path]:
    """把章节里引用的 PDF 图转成 PNG（同目录同名）。返回生成的 PNG 列表。

    Typst 图片路径相对于所在文件；LaTeX 图片路径相对于 main.tex 所在目录。
    """
    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            pymupdf = None
    pattern = IMAGE_TYP if engine == "typst" else IMAGE_TEX
    made: list[Path] = []
    for sec in sections:
        for m in pattern.finditer(sec.read_text(encoding="utf-8")):
            base = sec.parent if engine == "typst" else paper
            pdf = (base / m.group(1)).resolve()
            png = pdf.with_suffix(".png")
            if not pdf.exists():
                print(f"[warn] 图片不存在: {pdf}")
                continue
            if png.exists() and png.stat().st_mtime >= pdf.stat().st_mtime:
                continue
            if pymupdf is not None:
                doc = pymupdf.open(pdf)
                doc[0].get_pixmap(dpi=200).save(png)
                doc.close()
            elif shutil.which("pdftoppm"):
                run(["pdftoppm", "-png", "-r", "200", "-singlefile", str(pdf), str(png.with_suffix(""))])
            else:
                print(f"[warn] 无 pymupdf/pdftoppm，无法转换 {pdf}")
                continue
            made.append(png)
    return made


def build_reference_docx(dst: Path) -> None:
    """基于 pandoc 默认 reference.docx 生成中文字体版参考文档。"""
    raw = run(["pandoc", "-o", str(dst), "--print-default-data-file", "reference.docx"])
    if raw.returncode != 0:
        sys.exit(f"pandoc 生成 reference.docx 失败: {raw.stderr}")
    d = docx.Document(str(dst))
    for st in d.styles:
        if st.type != 1:  # WD_STYLE_TYPE.PARAGRAPH
            continue
        name = st.name or ""
        is_heading = name.startswith("Heading") or name == "Title"
        west = "Times New Roman"
        east = "黑体" if is_heading else "宋体"
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rfonts)
        rfonts.set(qn("w:ascii"), west)
        rfonts.set(qn("w:hAnsi"), west)
        rfonts.set(qn("w:eastAsia"), east)
        if name in ("Normal", "Body Text", "First Paragraph", "Compact"):
            st.font.size = Pt(12)
            st.paragraph_format.first_line_indent = Pt(24)
            st.paragraph_format.line_spacing = 1.25
        elif is_heading:
            st.font.color.rgb = RGBColor(0, 0, 0)
            st.font.bold = True
            st.font.size = Pt({"Heading 1": 15, "Heading 2": 14}.get(name, 12))
        elif name in ("Image Caption", "Table Caption", "Caption"):
            st.font.color.rgb = RGBColor(0, 0, 0)
            st.font.italic = False
            st.font.size = Pt(10.5)
            st.paragraph_format.first_line_indent = Pt(0)
            st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for section in d.sections:
        section.top_margin = Pt(85)
        section.bottom_margin = Pt(71)
        section.left_margin = Pt(64)
        section.right_margin = Pt(64)
    d.save(str(dst))


def front_matter_source(engine: str, fm: FrontMatter) -> str:
    """用排版源语言写出标题 / 摘要 / 关键词，交给 pandoc 一起转，这样摘要里的公式也能保留。"""
    title = fm.title or "[论文标题]"
    abstract = fm.abstract or ["[中文摘要内容]"]
    keywords = fm.keywords or ["[关键词]"]
    if engine == "typst":
        return (
            f"{TITLE_MARK}{title}\n\n"
            f"{ABSTRACT_MARK}摘\u3000\u3000要：\n\n"
            + "\n\n".join(abstract)
            + "\n\n*关键词：* " + " #h(1em) ".join(keywords) + "\n\n#pagebreak()\n\n"
        )
    return (
        f"{TITLE_MARK}{title}\n\n"
        f"{ABSTRACT_MARK}摘\u3000\u3000要：\n\n"
        + "\n\n".join(abstract)
        + "\n\n\\textbf{关键词：} " + " \\quad ".join(keywords) + "\n\n\\begin{pagebreak}\n\\end{pagebreak}\n\n"
    )


def _set_run_font(run_, west: str, east: str, size: int, bold: bool = False) -> None:
    run_.font.name = west
    run_.font.size = Pt(size)
    run_.font.bold = bold
    rpr = run_._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), east)


def style_front_matter(docx_path: Path) -> None:
    """根据标记把标题 / 摘要标题段落设为居中黑体，并删除标记字符。"""
    d = docx.Document(str(docx_path))
    for p in d.paragraphs[:8]:
        if TITLE_MARK in p.text or ABSTRACT_MARK in p.text:
            is_title = TITLE_MARK in p.text
            mark = TITLE_MARK if is_title else ABSTRACT_MARK
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            for r in p.runs:
                if mark in r.text:
                    r.text = r.text.replace(mark, "")
                _set_run_font(r, "Times New Roman", "黑体", 16 if is_title else 14, bold=True)
    d.save(str(docx_path))


def inspect(docx_path: Path) -> dict:
    import zipfile

    z = zipfile.ZipFile(docx_path)
    xml = z.read("word/document.xml").decode("utf-8")
    text = re.sub(r"<[^>]+>", "", xml)
    return {
        "paragraphs": xml.count("<w:p>") + xml.count("<w:p "),
        "images": sum(1 for n in z.namelist() if n.startswith("word/media/")),
        "equations": xml.count("<m:oMath>") + xml.count("<m:oMath "),
        "tables": xml.count("<w:tbl>"),
        "placeholders": sorted(set(PLACEHOLDER.findall(text))),
        "leaked_internal_names": sorted({w for w in ("reports/", "figures/", "RESULTS_REPORT", "CLAUDE.md", "AGENTS.md") if w in text}),
    }


def docx_to_pdf(docx_path: Path) -> Path | None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("[info] 未找到 soffice，跳过 DOCX->PDF 渲染抽检")
        return None
    r = run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent), str(docx_path)], timeout=300)
    pdf = docx_path.with_suffix(".pdf")
    if r.returncode != 0 or not pdf.exists():
        print(f"[warn] soffice 转换失败: {r.stderr[-500:]}")
        return None
    return pdf


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", default="paper", help="论文源码目录（含 main.typ 或 main.tex）")
    ap.add_argument("--out", default=None, help="输出 DOCX 路径，默认 <paper>/main.docx")
    ap.add_argument("--reference", default=None, help="Word 参考样式文档（当届官方 DOCX 模板可直接传入）")
    ap.add_argument("--title", default=None)
    ap.add_argument("--abstract-file", default=None, help="摘要纯文本文件，空行分段")
    ap.add_argument("--keywords", default=None, help="分号分隔")
    ap.add_argument("--no-front-matter", action="store_true", help="不生成标题/摘要页（例如官方模板已含）")
    ap.add_argument("--pdf", action="store_true", help="用 soffice 顺带导出 PDF 做渲染抽检")
    ap.add_argument("--keep-entry", action="store_true", help="pandoc 失败时保留 _docx_body.* 中间文件")
    ap.add_argument("--strict", action="store_true", help="发现占位符或内部文件名泄露时以非零退出（终稿检查用）")
    args = ap.parse_args()

    if not shutil.which("pandoc"):
        sys.exit("缺少 pandoc，请先运行 scripts/setup_env.sh 或 @skills:doctor")

    paper = Path(args.paper).resolve()
    engine, main_file = detect_engine(paper)
    out = Path(args.out).resolve() if args.out else paper / "main.docx"
    sections = collect_sections(engine, main_file)
    if not sections:
        sys.exit("没有找到任何章节文件（#include / \\input）")
    print(f"[info] 引擎={engine}，章节 {len(sections)} 个")

    fm = extract_front_matter(engine, main_file)
    if args.title:
        fm.title = args.title
    if args.abstract_file:
        fm.abstract = [p.strip() for p in re.split(r"\n\s*\n", Path(args.abstract_file).read_text(encoding="utf-8")) if p.strip()]
    if args.keywords:
        fm.keywords = [k.strip() for k in re.split(r"[;；]", args.keywords) if k.strip()]
    print(f"[info] 标题={fm.title!r} 摘要段数={len(fm.abstract)} 关键词={fm.keywords}")

    pngs = convert_pdf_figures(engine, sections, paper)
    if pngs:
        print(f"[info] 生成 PNG 图 {len(pngs)} 张")

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        lua = tdp / "pdf2png.lua"
        lua.write_text(PDF2PNG_LUA, encoding="utf-8")
        ref = Path(args.reference).resolve() if args.reference else tdp / "reference.docx"
        if not args.reference:
            build_reference_docx(ref)

        # 正文入口：摘要页 + 章节，不带封面 / 手写目录等 Word 不需要的排版代码
        head = "" if args.no_front_matter else front_matter_source(engine, fm)
        if engine == "typst":
            entry = paper / "_docx_body.typ"
            entry.write_text(head + "".join(f'#include("{s.relative_to(paper).as_posix()}")\n' for s in sections), encoding="utf-8")
            fmt = "typst"
        else:
            entry = paper / "_docx_body.tex"
            entry.write_text(
                "\\documentclass{ctexart}\n\\usepackage{graphicx,amsmath,amssymb,booktabs,float}\n\\begin{document}\n"
                + head
                + "".join(f"\\input{{{s.relative_to(paper).as_posix()}}}\n" for s in sections)
                + "\\end{document}\n",
                encoding="utf-8",
            )
            fmt = "latex"
        try:
            cmd = [
                "pandoc", str(entry), "-f", fmt, "-t", "docx",
                "--number-sections",
                "--reference-doc", str(ref),
                "--lua-filter", str(lua),
                "--resource-path", str(paper),
                "-o", str(out),
            ]
            r = run(cmd, cwd=str(paper))
        finally:
            if r.returncode == 0 or not args.keep_entry:
                entry.unlink(missing_ok=True)
        if r.returncode != 0:
            hint = f"（已保留 {entry} 供排查）" if args.keep_entry else "（加 --keep-entry 可保留中间文件排查）"
            sys.exit(f"pandoc 失败{hint}:\n{r.stderr}")
        if r.stderr.strip():
            print("[pandoc]", r.stderr.strip()[-800:])

    if not args.no_front_matter:
        style_front_matter(out)

    report = inspect(out)
    report["docx"] = str(out)
    if args.pdf:
        pdf = docx_to_pdf(out)
        if pdf:
            report["pdf"] = str(pdf)
            try:
                import pymupdf  # type: ignore

                report["pdf_pages"] = pymupdf.open(pdf).page_count
            except Exception:
                pass
    print(json.dumps(report, ensure_ascii=False, indent=2))
    dirty = False
    if report["placeholders"]:
        dirty = True
        print("[warn] DOCX 中仍有模板占位符，提交前必须替换")
    if report["leaked_internal_names"]:
        dirty = True
        print("[warn] DOCX 中出现工作流内部文件名，提交前必须删除")
    if dirty and args.strict:
        sys.exit(2)


if __name__ == "__main__":
    main()
