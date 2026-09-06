# mm-workbench — 华为杯数学建模工作台（Devin 使用说明）

本仓库是一个 **skills 驱动**的数学建模竞赛工作台，没有应用代码可运行，核心资产是 `.agents/skills/` 下的技能与 `scripts/` 下的工具链脚本。所有比赛工作都在 `contest/<年份>-<题号>/` 子目录中进行。

## 入口

| 场景 | 调用 |
| --- | --- |
| 华为杯开赛（拿到题目/附件） | `hwb-kickoff` → 内部委托 `1start-mathmodel` |
| 其他比赛或练手 | `1start-mathmodel` |
| 只想检查环境 | `doctor` 或 `bash scripts/setup_env.sh --check` |
| 只想把论文转 Word | `docx-export` |

## 六阶段主流程（来自 MathModelAgent）

```text
1start-mathmodel → 2analysis-modeling → 3coding-visual → 4drawio → 5writing → 6verity
```

补强 skill 的插入点：

- `data-auditor-cleaner`：2 之后、3 之前（有附件数据时必做）
- `robustness-checker`：3 之后、5 之前
- `scibox-diagram`：与 4 并列，做技术路线图 / 框架图
- `consistency-auditor`、`quality-assurance-auditor`：6 之中/之后
- `docx-export`：6 通过后，需要 Word 交稿时

阶段之间只通过文件交接（`plan.md`、`todo.md`、`reports/*.md`、`code/`、`results/`、`figures/`、`paper/`），不要假设上一阶段的对话上下文仍在。

## 硬规则

1. **数值只有一个来源**：论文里所有数字来自 `reports/RESULTS_REPORT.md` / `results/`，不得估算、编造或另行四舍五入。
2. **原始数据只读**：附件放 `data/raw/`，任何清洗写 `data/clean/`，并在 `reports/DATA_REPORT.md` 记录每一步。
3. **建模判断归人**：模型选型、假设取舍、结论强弱由用户决定；AI 提供证据、选项与机械正确性。关键决策记入 `plan.md`。
4. **可复现**：固定随机种子，结果写文件，`code/` 能从零跑通。
5. **正文干净**：论文正文/摘要不得出现队号、学校、`reports/`、`figures/`、`AGENTS.md` 等内部名称与模板占位符。
6. **封面年年变**：华为杯官方模板（尤其封面）每届更新，开赛后按 `hwb-kickoff` Step 2 对照官方模板替换 `paper/title.pdf` / `paper/logo.pdf` 与 `assets/title.typ` 中的届数，不要沿用往届封面直接提交。
7. **图片路径**：Typst 相对于所在文件（`sections/` 中用 `../../figures/`，编译加 `--root .`）；LaTeX 相对于 `main.tex`（统一 `../figures/`）。
8. **数据图统一出口**：matplotlib 图一律 `from mm_plot_style import apply_style, save_fig`（模块在 `.agents/skills/3coding-visual/scripts/`，规范见 `.agents/skills/_references/figure_style.md`）。中文字体必须是 TrueType + `pdf.fonttype=42`；不要手写 `font.family`。Noto CJK（CFF）配 fonttype 42 会使 PDF 字体损坏、DOCX 转 PNG 乱码；`fonttype=3` 虽能显示但文字不可提取，不作为修复手段。插图前跑 `check_figures.py --expect-cjk figures/`。
9. **华为杯排版单一真源**：页边距/字号/标题/图表题/公式编号以 `.agents/skills/_references/huaweibei_body_format.md` 为准；Typst 模板的字体回退与三线表在 `5writing/templates/zh/huaweibei/lib.typ`（`#three-line-table`），LaTeX 在 `huaweibei-latex/main.tex`（`\threelinetable`、`\papertitle`），DOCX 在 `docx-export/scripts/paper2docx.py`（`--reference` 可套当届官方模板，`--strict` 审计）。改一处要同步三处并跑 smoke_test。

## 工具链

`bash scripts/setup_env.sh` 一次装齐：Typst、XeLaTeX（TeX Live + 中文字体）、Pandoc、LibreOffice、Poppler、draw.io（headless wrapper）、Python 科学栈，以及字体：Noto CJK（Typst/LaTeX 宋黑回退）、文泉驿微米黑（matplotlib 中文 TrueType）、Liberation（Times New Roman 同字宽替代）、文鼎楷体。Devin 环境蓝图已调用该脚本；本机请把 `~/.local/bin` 加入 `PATH`。`--check` 会验证 `mm_plot_style` 能选到 TrueType 中文字体。

常用编译命令（在 `contest/<年>-<题>/` 内）：

```bash
typst compile --root . paper/main.typ                     # Typst → PDF
(cd paper && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex)  # LaTeX → PDF
python3 ../../.agents/skills/docx-export/scripts/paper2docx.py --paper paper --pdf   # → DOCX (+PDF 抽检)
python3 ../../.agents/skills/scibox-diagram/scripts/export_figure.py figures/x.drawio # drawio → PNG/PDF
python3 ../../.agents/skills/3coding-visual/scripts/check_figures.py --expect-cjk figures/  # 数据图 PDF 字体/中文审计
```

Typst 华为杯模板默认用 Linux 已装字体（零 warning）；在装有官方字体的机器上加 `--input official-fonts=true` 切到 Times New Roman/宋体/黑体/楷体。

## 仓库维护

- 修改 skill 时保持 `SKILL.md` frontmatter 只有 `name` 与 `description`（Devin 按此发现技能）。
- 自检：`bash scripts/smoke_test.sh`（matplotlib 中文图 + drawio 导出 + 编译两套华为杯模板 + DOCX strict 导出 + DOCX 链路中文图不乱码校验）。`KEEP=1` 保留产物目录便于目检。
- 第三方来源与许可见 `THIRD_PARTY_NOTICES.md`；改动 vendored skill 时在该文件记录。
- 不要把比赛数据、队号、API Key 提交进仓库；`contest/` 默认被 `.gitignore` 忽略，赛后如需归档另开分支。
