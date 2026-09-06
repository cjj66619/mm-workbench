---
name: docx-export
description: "把 Typst / LaTeX 论文源码转换为可编辑的 Word（DOCX）交稿件：公式保留为 Word 原生公式（OMML），PDF 图自动转 PNG 嵌入，自动生成标题/摘要/关键词页，可套用当届官方 Word 模板样式，并顺带导出 PDF 做渲染抽检与占位符/内部文件名泄露检查。在 5writing 完成、6verity 编译通过后调用。"
---

# DOCX 交稿导出

华为杯等比赛要求或允许提交 Word 版论文时，用本 skill 从 `paper/` 目录一键生成 `main.docx`。
它不重新写论文，只做格式转换与检查；论文内容仍以 Typst/LaTeX 源码为唯一真源。

## 何时调用

1. `5writing` 已完成，`6verity` 已确认 Typst/LaTeX 能编译且数值、图表引用一致。
2. 用户要求 Word/DOCX 交稿，或赛题通知要求提交 `.docx`。

## 前置条件

`pandoc`、`python-docx`、`pymupdf`（或 `pdftoppm`），可选 `soffice`（LibreOffice，用于 `--pdf` 抽检）。
缺失时先运行 `scripts/setup_env.sh` 或调用 `doctor` skill。

## 用法

在项目根目录执行：

```bash
python3 .agents/skills/docx-export/scripts/paper2docx.py --paper paper --pdf
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `--paper DIR` | 论文目录，需含 `main.typ` 或 `main.tex`（自动识别引擎） |
| `--out FILE` | 输出路径，默认 `<paper>/main.docx` |
| `--reference official.docx` | 当届官方 Word 模板；作为 pandoc reference.docx，页面设置以它为准。不传时用内置的 A4 reference.docx，样式按 `../_references/huaweibei_body_format.md` 的官方参数直接写入输出文档（不依赖样式名对得上） |
| `--cover-placeholder` | 最前面加一页空白封面节（页码 0 不显示），摘要页从 1 起，供在 Word 中粘进官方封面 |
| `--figure-dpi N` | PDF 图转 PNG 的分辨率，默认 300 |
| `--title / --abstract-file / --keywords` | 模板里抽不到或想覆盖时手动指定（关键词用 `;` 分隔） |
| `--no-front-matter` | 不生成标题/摘要页（官方模板自带、准备手工粘贴时用） |
| `--pdf` | 用 LibreOffice 把 DOCX 再转 PDF 到 `<paper>/docx_render/`，供逐页目检（不会覆盖 Typst/LaTeX 原生 `main.pdf`） |
| `--keep-entry` | pandoc 失败时保留 `_docx_body.*` 中间文件排查 |
| `--strict` | 占位符 / 内部文件名泄露 / 格式审计（页面、页边距、标题、图表题、公式编号、目录域、页码）不达标时以退出码 2 结束；终稿导出必加 |

## 转换规则（脚本已实现，无需手工做）

- 只转正文：从 `main.typ` 的 `#include` / `main.tex` 的 `\input` 收集章节，跳过封面、手写目录等 Word 不需要的排版代码。摘要既可直接写在 `main.typ` 里，也可 `#include` 一个含 `关键词：` 的文件（如 `abstract.typ`，须放在 `paper/` 根目录）。
- 交叉引用：pandoc 不解析 Typst `@fig-x` / `@tbl-x`，脚本会按出现顺序把它们替换为 `图 N` / `表 N` 并去掉 `<label>`（在临时影子目录中完成，不改源文件）。
- 标题/摘要/关键词：从模板抽取后用源语言重写为正文开头一页，因此摘要里的公式也能保留；之后分页。
- 公式：pandoc 输出 Word 原生 OMML，Word 里可继续编辑。
- 图：`figures/*.pdf` 用 PyMuPDF 自动渲染为同名 `.png`（默认 300 dpi，写入 dpi 元数据保持物理尺寸）后嵌入；图题自动加"图 N"。同名 PNG 已存在且不比 PDF 旧时直接复用。**matplotlib 图的中文若用 Noto CJK（CFF/OTF）+ `pdf.fonttype=42` 导出，PDF 字体流非法，转 PNG 后乱码**；图必须由 `3coding-visual/scripts/mm_plot_style.py` 生成，导出前可用 `3coding-visual/scripts/check_figures.py --expect-cjk figures/` 审计（见 `../_references/figure_style.md`）。
- 三线表：Typst `#three-line-table(...)`（`lib.typ`）与 LaTeX `\threelinetable{表题}{列}{表头}{表体}` 都转为顶/底 1.5pt、表头下 0.5pt 的 Word 表格，表题在表上。LaTeX 侧的 `\threelinetable` 定义在转换时由脚本内联（不读 `main.tex` 导言），模板里改它的参数个数需同步 `paper2docx.py`。
- 章节编号与正文格式：按 `../_references/huaweibei_body_format.md`——A4 / 2.5cm 边距，一级标题“一、”黑体四号居中，二/三级“1.1”“1.1.1”，正文宋体/Times New Roman 小四首行缩进 2 字符，图题在下表题在上，公式右侧编号，目录域，页脚页码。
- 分页：Typst `#pagebreak()`、LaTeX `\newpage` 转为 Word 分页符。

## 输出与检查

脚本最后打印 JSON 报告：段落数、图片数、公式数、表格数、残留占位符、泄露的内部文件名（`reports/`、`figures/`、`AGENTS.md` 等）。

- `placeholders` 非空 → 回到 `5writing` 把 `[论文标题]`、`[关键词1]` 等替换掉后重跑。
- `leaked_internal_names` 非空 → 论文正文出现了工作流内部名称，必须删除。
- `--pdf` 生成的 PDF 需逐页导出 PNG 查看（同 `6verity` Step 8）。注意 LibreOffice 对个别数学符号（如 `‖`）显示为 `¿` 属于其字体回退问题，DOCX 内 OMML 数据本身完整，在 Word 中正常。

## 与官方模板的关系

- 组委会每年更新 Word 模板（主要是封面）。拿到当届模板后：
  1. 用 `--reference 官方模板.docx` 套样式；
  2. 在 Word 中打开生成的 `main.docx`，把官方模板的封面页复制到最前面（或反过来把正文粘进官方模板）；
  3. 核对页边距、页眉页脚、页码起始与官方要求一致。
- 本 skill 不承诺自动满足当届格式要求；最终必须由人在 Word 中目检一遍。
- 官方正文参数（上届 Word 模板实测）固定在 `../_references/huaweibei_body_format.md`，脚本内置样式与 Typst/LaTeX 模板都以它为准；当届模板如有变化，先更新该文件再改三处实现。用 `--reference` 传入当届模板后，需实测一次其 Heading 1/2/3、Caption、Body Text 样式名是否与脚本预期一致。
