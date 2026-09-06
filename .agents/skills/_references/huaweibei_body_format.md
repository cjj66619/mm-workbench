# 华为杯论文正文格式规范（从官方 Word 模板提炼）

来源：官方 Word 论文模板（第二十二届版）的 `styles.xml` / `numbering.xml` / `document.xml`。
本文件只收录**正文格式**（摘要页之后的一切排版参数）。**封面页不在本文件范围**：封面（赛徽、届数、
学校、队号、队员）年年变化，由用户拿到当届官方模板后自行替换，工作流不得把封面写死。

三处消费本规范：

- `5writing/templates/zh/huaweibei*`：Typst / LaTeX 模板的排版参数（PDF 交稿）。
- `docx-export/scripts/paper2docx.py`：`build_reference_docx()` 与后处理（DOCX 交稿）。
- `6verity` / `docx-export --strict`：格式审计的判据。

修改任一实现时先改本文件，再同步三处；单位换算：1 pt = 20 twips，1 字符 = 正文字号（12 pt = 240 twips）。

---

## 1. 页面

| 项 | 官方值 | 说明 |
| --- | --- | --- |
| 纸张 | A4（210 × 297 mm，11906 × 16838 twips） | |
| 上/下/左/右边距 | 2.5 cm（1418 twips） | 四边相同 |
| 页眉距边 | 1.5 cm（851 twips） | 页眉内容为空 |
| 页脚距边 | 1.75 cm（992 twips） | |
| 版心宽 | 16.0 cm（9072 twips） | 公式编号右对齐用 |
| 页码 | 页脚居中，宋体/Times New Roman 9 pt（sz 18），`PAGE` 域，段前/段后 3 pt | `pgNumType start=0`：封面为第 0 页不显示，摘要页为第 1 页 |
| 页眉 | 空段落（样式 header：9 pt，居中），渲染无内容；不写题目/队号/页眉线 | |
| 文档网格 | 未启用（`docGrid` 无 type） | 行距按字号自然行距 |

## 2. 字体与正文

| 项 | 官方值 |
| --- | --- |
| 中文正文字体 | 宋体（`w:eastAsia="宋体"`） |
| 西文/数字字体 | Times New Roman（ascii / hAnsi / cs） |
| 正文字号 | 小四 12 pt（sz 24） |
| 首行缩进 | 2 字符（`firstLineChars=200`，即 24 pt / 480 twips） |
| 对齐 | 两端对齐（`jc=both`） |
| 行距 | 单倍行距（未设置 `spacing/line`，即宋体 12 pt 的自然行距约 15.6 pt） |
| 段前/段后 | 0（摘要页段落例外，见 §7） |
| 字距 | `kern=2`（仅影响 ≥1 pt 的西文字距，可忽略） |
| 强调 | 加粗（`<w:b/>`），不用斜体、下划线做中文强调 |
| 段内小标题 | 官方示例：`问题一：数据分析与故障特征提取` 为**加粗独立段**，首行缩进 2 字符（`firstLine=482`），非标题样式，不进目录 |

Linux 无宋体/黑体时的回退（`scripts/setup_env.sh` 已安装）：Times New Roman → Liberation Serif（同字宽）；宋体 → Noto Serif CJK SC；黑体 → Noto Sans CJK SC；楷体 → AR PL KaitiM GB。
DOCX 里写字体名即可（由打开者的 Word 解析），PDF 引擎需要在模板里列回退链：Typst 见 `5writing/templates/zh/huaweibei/lib.typ`（默认 Linux 字体，`--input official-fonts=true` 切换官方字体名），LaTeX 见 `huaweibei-latex/main.tex` 的 `\IfFontExistsTF`。
数据图（matplotlib）不走这套字体：中文必须用 TrueType 字体（文泉驿微米黑等，Noto CJK 为 CFF 会导致 PDF 乱码），由 `3coding-visual/scripts/mm_plot_style.py` 自动选择，见 `_references/figure_style.md`。

## 3. 标题（三级）

编号来自 `numbering.xml`（abstractNum 1，`isLgl` 使二三级恒为阿拉伯数字）。

| 级别 | 样式 | 编号格式 | 编号后 | 中文字体 | 字号 | 加粗 | 对齐 | 段前/段后 | 其它 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 一级 | heading 1 | `一、`（chineseCountingThousand，`%1、`） | 空格 | **黑体** | 14 pt（sz 28，四号） | 否（黑体本身粗，`<w:b/>` 缺省；`bCs` 仅复杂文字） | **居中** | 段前 6 pt / 段后 6 pt（正文实际 `before=120 after=120`；样式默认 0.5 行） | keepNext + keepLines，outlineLvl 0 |
| 二级 | heading 2 | `1.1`（`%1.%2 `，isLgl） | 空格 | 宋体（主题字体；实现时显式写宋体/黑体皆可，官方渲染为宋体加粗） | 12 pt（sz 24） | **是** | 左对齐 | 6 pt / 6 pt | keepNext + keepLines |
| 三级 | heading 3 | `1.1.1`（`%1.%2.%3 `，isLgl） | 无（编号 rPr 为黑体） | 宋体，编号黑体 | 12 pt | 否 | 左对齐 | 6 pt / 6 pt | keepNext + keepLines |

- 标题不首行缩进（`ind left=0 firstLine=0`）。
- 一级标题"参考文献"、"附录"**不编号**（`numId=0`），仍居中 14 pt 黑体，并进目录。
- 一级标题前**不强制分页**（官方模板正文连续排版；只有摘要页、目录页、参考文献/附录之间用分节符）。
- 四级以下不使用。官方 numbering 里 4–7 级定义为 `1.1.1.1` / `(1)` / `1)`，不进目录，工作流禁用。

## 4. 图与图题

| 项 | 官方值（样式 图注 `a1`，基于 表注 `a0`） |
| --- | --- |
| 位置 | 图**下方**，图与图题各自独立段落，**居中** |
| 编号 | `图N`（全篇连续，`%9` 单序列），编号后紧跟一个空格再接题名：`图3 外圈故障示意图` |
| 字体字号 | 宋体/Times New Roman **11 pt（sz 22）加粗**（`<w:b/>`） |
| 段前/段后 | 段前 3 pt（before=60，0.25 行）/ 段后 6 pt（after=120） |
| 缩进 | 无（`firstLineChars=0`） |
| 图片段落 | 居中、无首行缩进、`keepNext`（与图题同页）；`noProof` |
| 图宽 | 不超版心 16 cm；单图建议 12–14 cm，双联图各 7.5 cm |

## 5. 表与表题

| 项 | 官方值（样式 表注 `a0`、表格 `a9`、三线表 `afb`） |
| --- | --- |
| 表题位置 | 表**上方**，居中，`keepNext` |
| 编号 | `表N`（全篇连续，`%8`），格式同图题：`表1 符号说明` |
| 表题字体 | **11 pt（sz 22）加粗**，段前 6 pt（before=120）/ 段后 3 pt（after=60），无缩进 |
| 表格对齐 | 表整体居中（`tblPr/jc=center`），单元格垂直居中 |
| 表宽 | 官方示例 80% 版心（`tblW 4000 pct`）；实现取 80%–100% |
| 三线 | 顶线 1.5 pt（sz 12）、表头下线 0.5 pt（sz 4）、底线 1.5 pt（sz 12）；**无竖线、无其它横线** |
| 表头 | 加粗、居中 |
| 单元格文字 | 12 pt 宋体/Times New Roman，**固定行距 18 pt**（`line=360 lineRule=exact`），无首行缩进；数字列居中或右对齐 |
| 续表 | 跨页时重复表头（`tblHeader`） |

## 6. 公式

| 项 | 官方值（样式 MTDisplayEquation / 行间公式表格） |
| --- | --- |
| 行间公式 | 独立段落，**公式居中、编号右对齐**：制表位 center 4536 twips（版心中点）、right 9072 twips（版心右缘） |
| 编号 | `(1)`、`(2)`…全篇连续，Times New Roman 12 pt，不加粗 |
| 段落 | 无首行缩进，段前/段后 0（继承正文） |
| 形式 | Word 原生公式（OMML）或公式编辑器对象，**禁止截图** |
| 行内公式 | 与正文同基线，变量斜体、函数名/单位正体 |

## 7. 摘要页（正文之前，属于本规范；题头行例外）

| 项 | 官方值 |
| --- | --- |
| 题头三行 | `中国研究生创新实践系列大赛`（华文新魏 18 pt 加粗）、`"华为杯"第X届中国研究生`（22 pt）、`数学建模竞赛`（22 pt）——**届数年年变**，由参数注入，不得写死 |
| 题目行 | `题 目：` 隶书 18 pt（sz 36）+ 题名宋体 14 pt（sz 28）下划线，左对齐，行距 1.5 倍（line=360 auto） |
| "摘 要："行 | 隶书 18 pt，**居中**，行距 1.5 倍 |
| 摘要正文 | 正文样式，首行缩进 2 字符，**段前 3 pt / 段后 3 pt**（before=60 after=60） |
| 小问引导 | `针对问题一，`……**加粗**引导词（run 级加粗），其后正文不加粗 |
| 关键词行 | `关键词：` 隶书 18 pt，左对齐；关键词 12 pt 宋体，词间两个全角空格 |
| 篇幅 | 摘要不超过两页 |
| 分页 | 关键词后分节/分页，进入目录页 |

隶书/华文新魏在 Linux 无等价字体，DOCX 写字体名即可（Word 端有），PDF 引擎回退到黑体。

## 8. 目录页

| 项 | 官方值 |
| --- | --- |
| 标题 | `目录`，样式 TOC 标题1：16 pt（sz 32）加粗居中，固定行距 20 pt，段后 0.5 行；不编号、不进目录 |
| 条目 | TOC1 / TOC2 / TOC3：正文实例 10.5 pt（sz 21；样式默认 12 pt 被实例覆盖），段前 3 pt / 段后 3 pt，两端对齐；TOC2 左缩进 1 字符（240 twips），TOC3 左缩进 2 字符（480 twips） |
| 引导符 | 右对齐制表位 9060 twips，点线（`leader=dot`） |
| 深度 | 到三级标题 |
| 实现 | DOCX 用 `TOC \o "1-3" \h \z \u` 域 + `updateFields`，同时写入静态条目作缓存；PDF 引擎用原生目录 |

## 9. 列表

| 项 | 官方值（样式 有序列表 `a3`） |
| --- | --- |
| 编号 | `(1)`（`(%1)`），Times New Roman，不加粗 |
| 缩进 | 左缩进 585 twips、悬挂 347 twips（约首行 2 字符起） |
| 段前/段后 | 6 pt / 6 pt，同列表内 `contextualSpacing` |
| 用途 | 模型假设、优缺点等条目；正文论证段**不得**用列表代替 |

## 10. 参考文献与附录

| 项 | 官方值 |
| --- | --- |
| 标题 | `参考文献` / `附录` 一级标题、不编号、居中 14 pt 黑体、进目录 |
| 文献条目 | 样式 参考文献 `a`：`[N] ` 编号 + 条目，12 pt，两端对齐，固定行距 18 pt，左缀 482 twips 悬挂 |
| 文献格式 | GB/T 7714：`[编号] 作者，书名，出版地：出版社，出版年.` / `[编号] 作者，论文名，杂志名，卷期号：起止页码，出版年.` / 网络资源含访问日期；AI 工具条目 `工具名称, 版本/型号, 开发机构/公司, 使用日期` |
| 附录代码 | 样式 代码清单：等宽字体（Courier New / 宋体）10.5 pt（sz 21），0.5 pt 边框（sz 8）全框线，单倍行距，无缩进 |
| 附录顺序 | 附录 1 支撑材料文件清单 → 附录 2+ 源代码（每段代码前一行说明语言与作用） |

---

## 11. 实现对照表

| 规范项 | Typst 模板 | LaTeX 模板 | paper2docx.py |
| --- | --- | --- | --- |
| 页边距 2.5 cm | `#set page(margin: 2.5cm)` | `geometry{margin=2.5cm}` | `sectPr/pgMar 1418` |
| 正文 12 pt 宋体 + TNR、首行 2 字符、两端对齐、单倍行距 | `#set text(12pt)` `#set par(first-line-indent: 2em, all: true, justify: true, leading: 0.55em?)`（Typst leading 是行间空白；宋体 12 pt 单倍行距 ≈ leading 0.3em，模板取 0.35em） | `\linespread{1.0}` `\parindent=2em` | Normal / Body Text / First Paragraph 样式 |
| 一级 `一、` 居中黑体 14 pt | `numbering: "一、"` 自定义函数 | `\ctexset{section/name={,、}, number=\chinese{section}}` | pandoc `--number-sections` 出 `1 ` → 后处理替换为 `一、`；Heading 1 样式 |
| 二/三级 `1.1` / `1.1.1` 12 pt | 同上 | 同上 | Heading 2 加粗、Heading 3 不加粗 |
| 图题下方 `图N xxx` 11 pt 加粗 | `#show figure.caption` | `\captionsetup` | Lua filter 编号 + Image Caption 样式 |
| 表题上方 `表N xxx` 11 pt 加粗 | `#show figure.where(kind: table)` caption 置顶 | `\captionsetup[table]{position=above}` | Table Caption 样式 + 表格居中 + 三线边框后处理 |
| 公式居中编号右对齐 `(N)` | `#set math.equation(numbering: "(1)")` | amsmath 默认 | oMathPara → 制表位 + 右对齐编号后处理 |
| 页码居中 9 pt | `numbering: "1"` + footer 9 pt | `\pagestyle{plain}` + 9 pt | footer PAGE 域 |
| 目录到三级、点线 | `#outline(depth: 3)` | `\tableofcontents` | TOC 域 + 静态缓存条目 |

