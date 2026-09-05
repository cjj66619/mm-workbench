# mm-workbench

面向**华为杯（中国研究生数学建模竞赛）**的 AI 数学建模工作台，以 Devin 为运行载体：把开源社区里最好用的数模 skills 整合成一条从「读题」到「PDF + Word 交稿」的完整流水线。

```text
hwb-kickoff（开赛入口，建工作区 / 核对当届封面）
 └─ 1start-mathmodel（总控：plan.md / todo.md）
     ├─ 2analysis-modeling   读题、拆子问题、假设、变量、模型公式
     ├─ data-auditor-cleaner 附件数据审计与清洗（data/raw → data/clean）
     ├─ 3coding-visual       可复现代码、求解、RESULTS_REPORT.md、数据图 PDF
     ├─ robustness-checker   灵敏度 / 稳健性 / 基线对比
     ├─ 4drawio · scibox-diagram   技术路线图、流程图（draw.io 可编辑矢量）
     ├─ 5writing             华为杯 Typst / LaTeX 模板成稿
     ├─ 6verity              编译、数值一致性、占位符、内部文件泄露
     ├─ consistency-auditor · quality-assurance-auditor   终审
     └─ docx-export          Word 交稿（公式为可编辑 OMML）+ PDF 抽检
```

## 快速开始

1. **环境**（Devin 环境蓝图已自动执行；本机手动）：

   ```bash
   bash scripts/setup_env.sh          # Typst / XeLaTeX / Pandoc / LibreOffice / draw.io / Python 科学栈
   bash scripts/setup_env.sh --check  # 只体检
   bash scripts/smoke_test.sh         # 两套华为杯模板 → PDF → DOCX 全链路自检
   ```

2. **开赛**：把赛题 PDF 和附件放进仓库，对 Devin 说 `华为杯开赛，用 B 题，题目在 xxx.pdf，附件在 xxx/`。`hwb-kickoff` 会创建 `contest/<年份>-<题号>/`，然后按上图逐阶段推进；每个阶段的产物都落盘（`plan.md`、`reports/*.md`、`code/`、`results/`、`figures/`、`paper/`）。

3. **交稿**：`6verity` 通过后，`docx-export` 生成 `paper/main.docx`（`--strict` 保证无占位符与内部文件名泄露），Typst/LaTeX 同步产出 PDF。

## 国一对标规则来源

`.agents/skills/_references/huaweibei_excellent_paper_patterns.md` 汇总了三类信息并分层标注：**[官方]** 官方论文模板明文要求（摘要 ≤ 2 页、公式不得截图、AI 工具须列入参考文献并在正文标注、附录含支撑材料清单等）；**[样本]** 2023–2024 年 75 篇公布优秀论文的结构统计（页数、图表、公式、章节出现率、摘要写法）；**[建议]** 工作台据此制定的内部规则（每问"分析 → 建模 → 求解 → 结果分析与验证 → 小结"、每个主模型至少一种验证证据、摘要每问一段含数值）。`2analysis-modeling`、`5writing`、`6verity`、`quality-assurance-auditor` 都引用它；每届开赛先按当届官方模板更新 §1，样本统计只作自查提示、不是评分线。

## 关于封面（每届会变）

华为杯官方模板每届更新，变化主要在**封面**。本仓库模板的封面元素是独立文件，可整体替换：

| 元素 | 文件 | 更新方式 |
| --- | --- | --- |
| 题头文字（届数） | `paper/assets/title.typ` → `paper/title.pdf` | 改 `edition` 后 `typst compile` |
| 校徽 / 赛徽 | `paper/logo.pdf` | 从官方模板导出替换 |
| 整页封面 | `paper/cover.pdf` | 官方封面页导出 PDF，`cover-page()` / `\coverpage` 改为直接插图 |
| 学校 / 队号 / 队员 | `main.typ` `cover-info-table()` / `main.tex` `\coverpage` | 替换 `[学校名称]` `[参赛队号]` `[成员 A/B/C]` |

Word 交稿建议直接在官方 DOCX 模板中保留封面页，把 `docx-export` 生成的正文粘入；或 `--reference 官方.docx` 套用其样式。`hwb-kickoff` Step 2 会提醒对照官网当届模板逐项核对。

## 仓库结构

```text
.agents/skills/        Devin 自动发现的 skills（每个目录一个 SKILL.md）
scripts/setup_env.sh   工具链安装 / 体检
scripts/smoke_test.sh  全链路自检
AGENTS.md              Devin 工作规则（数值单一来源、原始数据只读、建模判断归人等）
THIRD_PARTY_NOTICES.md 上游来源与许可
contest/               比赛工作区（.gitignore 忽略）
```

## 致谢

- [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent)：六阶段建模流水线与全部竞赛论文模板
- [jihe520/sci-box](https://github.com/jihe520/sci-box)：draw.io 技术路线图 / 框架图
- [zhnnky329/MathModeling-skills](https://github.com/zhnnky329/MathModeling-skills)：数据审计、稳健性、一致性与终审 skills（MIT）

许可与改动明细见 `THIRD_PARTY_NOTICES.md`。本仓库仅供个人参赛与学习使用。
