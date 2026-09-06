# 数据图绘图规范（Matplotlib）

本规范把 [nature-skills](https://github.com/Yuan1z0825/nature-skills) `nature-figure` 的期刊级绘图约定，按华为杯中文论文与 DOCX 交稿链路做了落地。执行入口是 `3coding-visual/scripts/mm_plot_style.py`（统一 rcParams、调色板、`figsize`、`save_fig`、`check_pdf`）与 `check_figures.py`（批量检查 PDF）。`3coding-visual` Step 4 强制使用，`mathmodel-figure-templates` 的模板脚本同样套用。

标签：[Nature] 来自 nature-figure 规范；[mm] 本仓库为中文论文/DOCX 链路加的约束；[环境] 当前 Linux 工具链的实测事实。

## 1. 设计原则

- [Nature] 一张图只服务一个结论：先确定“读者看完要记住什么”，再决定图型。多面板时一个 hero panel + 若干证据 panel，不做图表拼贴。
- [Nature] 去装饰：无图内大标题（标题由论文 caption 给）、无背景网格（确需辅助读数时用浅灰细线）、无阴影/3D 效果/渐变。
- [Nature] 上、右脊线默认关闭；图例无边框；背景纯白。
- [mm] 图内文字与论文语言一致：中文论文用中文坐标轴/图例/注记，单位写法与正文统一（如“成本/万元”或“成本 (万元)”，全篇只选一种）。
- [mm] 同类图（同一子问题的多张对比图）配色、线型、坐标范围、尺寸保持一致，方便读者横向比较。
- [mm] 真实数据图必须能追溯：`save_fig(..., source=..., params=...)` 写入 `figures/_manifest.json`，`RESULTS_REPORT.md` 引用。

## 2. 字体与字号

| 项目 | 规范 |
| --- | --- |
| 字族 | [Nature] 默认 sans-serif（Arial/Helvetica → Liberation Sans → DejaVu Sans）。正文图统一 `font="sans"`；需与 Times 正文呼应时可 `font="serif"`（Times New Roman → Liberation Serif）。 |
| 中文 | [mm] 自动在 `CJK_SANS` / `CJK_SERIF` 候选中选**Matplotlib 能识别且轮廓为 TrueType** 的字体（见 §6）。 |
| 基准字号 | [Nature] 期刊最终图 7–9 pt；[mm] 华为杯正文小四 12 pt，图内文字 9 pt（约小五），tick/图例 8 pt。`apply_style(base_size=9)`。 |
| 下限 | [Nature] 任何 glyph ≥ 5 pt（`check_pdf` 检查 rawdict 字号）。 |
| 负号 | [mm] `axes.unicode_minus=False`，用 ASCII `-`，避免中文字体缺 U+2212 出现方块。 |
| 数学 | `mathtext.fontset` 跟随字族（dejavusans/dejavuserif），不用 `text.usetex`。 |

## 3. 线宽与标记

- [Nature] 坐标轴线宽 0.8 pt，tick 0.8 pt 长 3 pt，方向 out；数据线 1.2 pt；标记 4 pt；误差线 capsize 2。
- [mm] 重点曲线可加粗到 1.6 pt，背景/对照曲线 0.8 pt 或半透明（alpha 0.6），用线宽而不是颜色数量来分层。
- 面板 (a)(b)(c) 标签：`label_panels(axes)`，粗体、与基准字号一致、每个 axes 左上角外侧。

## 4. 配色

`PALETTES` 三套，通过 `apply_style(palette=...)` 设为 `axes.prop_cycle`：

| 名称 | 用途 | 颜色 |
| --- | --- | --- |
| `default` | 语义色：主方法蓝、对照红、第二组绿、青、紫、中性灰。灰度下明暗有序。 | `#1F77B4 #D62728 #2CA02C #17BECF #9467BD #7F7F7F` |
| `pastel` | 同一方法族多面板对比（[Nature] NMI pastel） | `#8EC1DA #F4A582 #A6D96A #B2ABD2 #FDB863 #BABABA` |
| `gray` | 黑白打印 | 6 级灰 |

- 连续数值 `SEQUENTIAL_CMAP="viridis"`，有中心值（相关系数、残差）`DIVERGING_CMAP="RdBu_r"`。
- [Nature] 禁止 jet/rainbow/hsv；分类颜色不超过 6 种，超出改用分面或线型+标记区分。
- [mm] 全文同一对象同一颜色（例如“模型 A”在所有图中都用 `COLORS[0]`）。

## 5. 尺寸与导出

A4 页边距 2.5 cm，版心 16 cm：

| `figsize(width)` | 宽 | 场景 |
| --- | --- | --- |
| `"full"` | 14 cm | 单张整宽图，Typst `image(width: 88%)` / LaTeX `width=0.88\textwidth` 时实际约 14 cm，字号保真 |
| `"two-thirds"` | 10.5 cm | 单张竖向或方形图 |
| `"half"` | 7.5 cm | 两图并排 |
| `"third"` | 5 cm | 三图并排 |

默认高宽比 0.62；`figsize("full", height_cm=...)` 可指定高度。图宽超过 16 cm 时 `check_pdf` 给 WARN——排版时被缩放会让字号失真。

导出（`save_fig`）：

- [mm] **PDF 为主**：论文（Typst/LaTeX）直接引用；`docx-export` 用 PyMuPDF 把 PDF 转 300 dpi PNG 嵌入 Word。
- PNG 300 dpi：预览、报告、`RESULTS_REPORT.md`。
- [Nature] SVG（`formats=("pdf","png","svg")`）：`svg.fonttype="none"` 保留可编辑文字，用于需要二次加工的图。
- `savefig.bbox="tight"`, `pad_inches=0.02`，白底。
- `pdf.fonttype=42`（TrueType 子集嵌入，文字可提取可检索）；`ps.fonttype=42`。

## 6. 中文乱码根因与排查

**根因**（[环境]，已复现）：

1. Linux 常见的 `fonts-noto-cjk` 是 **CFF 轮廓（OTF/`OTTO`）**。Matplotlib `pdf.fonttype=42` 只会把字体当 TrueType 嵌入，遇到 CFF 轮廓会写出非法字体流；PDF 阅读器/PyMuPDF 渲染出方块或错字，`docx-export` 转 PNG 后随之乱码。
2. `pdf.fonttype=3` 能渲染，但文字被拆成 Type3 路径，PyMuPDF/Word 提取不到中文，无法检索、无法审计。
3. Matplotlib 按字体文件内部 family 名注册，本机 Noto CJK TTC 被识别为 `Noto Sans CJK JP` 而不是 `SC`；直接写死 `font.family="Noto Sans CJK SC"` 会 `findfont` 失败回退到 DejaVu Sans，中文变空白/方块。

**方案**（`mm_plot_style.resolve_fonts`）：

- 在候选列表里逐个 `findfont(fallback_to_default=False)` → 检查能否渲染“中文图例测试” → 读文件头判定轮廓（`00 01 00 00`/`true` 为 TrueType；`OTTO` 为 CFF；`ttcf` 取第一面）；选第一个 TrueType 中文字体。
- 当前环境命中：sans → `WenQuanYi Micro Hei`（`fonts-wqy-microhei`），serif → `AR PL UMing CN`（`fonts-arphic-uming`）；`setup_env.sh` 已装。
- 全部候选都是 CFF 时降级 `pdf.fonttype=3` 并给 warning，提示安装 `fonts-wqy-microhei`。
- `font.family` 设为 `[Latin, CJK, DejaVu Sans]` 列表，Matplotlib ≥ 3.6 逐字回退：西文/数字走 Liberation Sans，中文走 CJK 字体。

**检查**（`check_figures.py` / `save_fig(check=True)`）：

| 现象 | 判定 |
| --- | --- |
| 字体未嵌入（`extract_font` 为空） | FAIL |
| 嵌入 ext 为 ttf 但字节头 `OTTO` | FAIL（就是上面的根因 1） |
| Type3 字体 | WARN，`--strict` 下 FAIL |
| 提取文本含 U+FFFD | FAIL |
| `--expect-cjk` 但提取不到 CJK 字符 | FAIL |
| 最小字号 < 5 pt | WARN |
| 图宽 > 16 cm 或非单页 | WARN |

排查步骤：`fc-list :lang=zh family file` 看系统有哪些中文字体 → `python3 -c "from matplotlib import font_manager as fm; print(sorted({f.name for f in fm.fontManager.ttflist if 'CJK' in f.name or 'WenQuanYi' in f.name or 'AR PL' in f.name}))"` 看 Matplotlib 识别的 family 名 → 装了新字体后删 `~/.cache/matplotlib` 重建缓存 → 重新 `check_figures.py --expect-cjk`。

## 7. 多面板与 QA

- [Nature] 面板边界对齐（同一行上下缘、同一列左右缘误差 ≤ 1.5 pt）：用 `plt.subplots(..., constrained_layout=True)` 或 `gridspec`，不要手动 `add_axes` 拼；共享轴 `sharex/sharey` 保证刻度一致。
- 图例放在数据空白区或图外顶部；不遮挡数据。
- 坐标轴标签写“量 (单位)”或“量/单位”，与正文一致；时间轴用真实日期时对刻度做 `autofmt_xdate`。
- 出图后必看 PNG 预览：文字是否重叠、图例是否遮挡、中文是否为方块。
- 提交前 `check_figures.py --expect-cjk figures/`（英文论文去掉参数）无 FAIL。

## 8. Caption 与统计信息

- 标题、结论性描述在论文 caption 中给出，图内只保留必要注记。
- 显示统计量时在图内或 caption 注明样本量 n、误差带含义（SD/SE/95% CI）、显著性检验方法。
- 图中数值必须与 `RESULTS_REPORT.md` 一致，不得在绘图脚本里另行四舍五入后写进标注。

## 9. `mathmodel-figure-templates` 的套用方式

模板脚本的 `configure_matplotlib()` 统一改为先 `apply_style(font=..., lang="en", ...)`，再叠加模板专属的线宽/字号；`render_template.py` 复制模板到工作区时同时复制 `mm_plot_style.py`，因此复刻输出与 `3coding-visual` 出图共享同一字体解析、导出与检查逻辑。复刻中文版时把 `lang` 改为 `"zh"` 并把图内文字改成中文即可。
