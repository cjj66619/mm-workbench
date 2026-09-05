---
name: hwb-kickoff
description: "华为杯（中国研究生数学建模竞赛）开赛入口。拿到赛题 PDF/附件后，用本 skill 初始化比赛工作区、校对当届官方模板与封面、生成 plan/todo，然后按 1start-mathmodel 的六阶段流水线（分析建模 → 代码图表 → 流程图 → 论文 → 验收）推进，并在结尾产出 PDF + DOCX 交稿件。用户说“开赛了 / 华为杯开始 / 用 X 题开始建模”时使用。"
---

# 华为杯开赛入口

本 skill 是 `1start-mathmodel` 在华为杯场景下的外壳：把华为杯特有的准备工作（题目落盘、官方模板校对、封面替换、交稿格式）前置，其余建模流程全部委托给六阶段 skill，不重复它们的内容。

## Step 0：确认输入

向用户索取（缺一项就先问）：

1. 赛题：题号（A/B/C/D/E/F）、题面 PDF/DOCX、全部附件（数据表、图片、说明）。
2. 当届官方论文模板（Word/PDF）——官网在开赛前后发布，封面年年变。没有就先用仓库内模板演练，并在 `todo.md` 记一条"替换官方封面"。
3. 团队信息：学校、参赛队号（只用于封面；正文与摘要页禁止出现）。
4. 排版引擎偏好：Typst（默认，编译快）或 LaTeX；交稿格式：PDF、DOCX 或两者（华为杯常见要求为 PDF，允许时再出 DOCX）。

## Step 1：初始化工作区

在仓库根目录创建 `contest/<年份>-<题号>/`，例如 `contest/2026-B/`，之后**所有阶段都以该目录为项目根**：

```text
contest/2026-B/
├── problem/            # 题面原文（PDF + 转出的 problem.md），只读
├── data/raw/           # 官方附件原样存放，只读，不得修改
├── data/clean/         # 清洗后数据（data-auditor-cleaner 产出）
├── plan.md  todo.md    # 1start-mathmodel 产出
├── reports/            # ANALYSIS_MODELING_REPORT.md / RESULTS_REPORT.md / DRAWIO_REPORT.md / VERIFY_REPORT.md / DATA_REPORT.md
├── code/  results/  figures/  robustness/
└── paper/              # 从 5writing 模板复制（见 Step 2）
```

把题面转成文本便于反复读取：`pdftotext -layout problem/X.pdf problem/problem.md`；表格附件用 `pandas`/`openpyxl` 先做一次 `head()` 与 `describe()` 记录到 `reports/DATA_REPORT.md` 的开头。

## Step 2：套用并校对当届模板

1. 复制模板到工作区：
   - Typst：`cp -r .agents/skills/5writing/templates/zh/huaweibei contest/<年>-<题>/paper`
   - LaTeX：`cp -r .agents/skills/5writing/templates/zh/huaweibei-latex contest/<年>-<题>/paper`
2. **封面**（每年变化，必须对照官方模板核对）：
   - 题头文字：编辑 `paper/assets/title.typ` 中的 `edition`（如 `第二十三届`）后 `typst compile paper/assets/title.typ paper/title.pdf`；
   - 校徽/赛徽：官方模板的封面若有变化，把官方封面页导出为 PDF 后直接替换 `paper/logo.pdf` / `paper/title.pdf`，或把整页封面另存为 `paper/cover.pdf` 并在 `main.typ` 的 `cover-page()` 中改为 `image("cover.pdf")`；
   - 学校、队号、队员：替换 `main.typ` 中 `cover-info-table()` 内的 `[学校名称]`、`[参赛队号]`、`[成员 A/B/C]`，或 `main.tex` 中 `\coverpage` 定义内的同名占位符（队员姓名按官方要求可留空）。
3. **摘要页与正文格式**：逐项对照官方模板检查字号（正文小四）、页边距、页码起始（摘要页为第 1 页）、标题编号格式、图表题格式；有差异就改 `main.typ` / `main.tex` 顶部的排版参数，不要改章节内容文件。
4. 编译一次空模板确认通过：
   - Typst：在工作区根目录 `typst compile --root . paper/main.typ`
   - LaTeX：在 `paper/` 内 `xelatex -interaction=nonstopmode main.tex` 两遍
5. 把以上核对结果写入 `todo.md` 的"模板校对"小节，未拿到官方模板的项标为待办。

## Step 3：环境体检

运行 `doctor` skill 或 `bash scripts/setup_env.sh --check`，确认 `typst`、`xelatex`、`pandoc`、`soffice`、`pdftoppm`、Python 科学栈可用。缺失项先补齐再进入建模。

## Step 4：进入六阶段流水线

调用 `1start-mathmodel`，把 Step 0 收集到的偏好直接传给它（竞赛类型=华为杯、语言=中文、引擎、交稿格式），由它生成 `plan.md`/`todo.md` 并依次调用：

| 阶段 | Skill | 华为杯补充要求 |
| --- | --- | --- |
| 分析建模 | `2analysis-modeling` | 华为杯题目通常 4–6 个递进小问、数据量大；小问之间的依赖关系必须画出并写进报告 |
| 数据审计 | `data-auditor-cleaner` | 有附件数据时必做；原始附件只读 |
| 代码图表 | `3coding-visual` | 固定随机种子；大数据先抽样调通再全量跑；所有结果写入 `results/` 文件 |
| 稳健性 | `robustness-checker` | 至少对主模型做参数灵敏度 + 数据扰动两类检查，结论回填 `RESULTS_REPORT.md` |
| 流程图 | `4drawio` / `scibox-diagram` | 至少一张技术路线图；drawio 不可用时用 `scibox-diagram` 手写 XML 再转 PDF |
| 论文 | `5writing` | 模板 = `zh/huaweibei`（Typst）或 `zh/huaweibei-latex`；正文禁止出现队号、学校、内部文件名 |
| 验收 | `6verity` + `consistency-auditor` + `quality-assurance-auditor` | 编译 + 一致性 + 终审三道 |
| 交稿 | `docx-export`（需要 DOCX 时） | `--reference 官方模板.docx`，在 Word 中拼回官方封面 |

## Step 5：交稿清单

在 `reports/VERIFY_REPORT.md` 末尾追加"交稿清单"，全部勾选后才算完成：

- [ ] `paper/main.pdf` 编译通过，逐页目检无溢出、无空白页、无占位符
- [ ] 封面为当届官方格式，队号/学校仅出现在封面
- [ ] 摘要页含题目、摘要、关键词，摘要有每个小问的方法与数值结论
- [ ] 正文数值与 `reports/RESULTS_REPORT.md` 一致（`consistency-auditor` PASSED）
- [ ] 图表编号连续、均被正文引用；参考文献可追溯
- [ ] 需要 DOCX 时：`paper2docx.py --paper paper --pdf --strict` 退出码 0（`placeholders` 与 `leaked_internal_names` 为空），在 Word 中拼回官方封面
- [ ] 代码可复现：`code/` 附 README 或运行说明，随机种子固定
- [ ] 文件命名按官方要求（通常为 队号.pdf / 队号.docx），不含中文与空格

## 时间建议（4 天赛程）

- D1：Step 0–3 + `2analysis-modeling` + 数据审计，晚间前定下每个小问的主模型。
- D2：`3coding-visual` 跑通全部小问，先出结果再优化。
- D3：稳健性、流程图、`5writing` 初稿全文。
- D4 上午：`6verity` + 两道审计 + 交稿件；下午留给人工目检与修改，不再改模型。
