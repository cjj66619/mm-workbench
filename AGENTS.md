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

## 工具链

`bash scripts/setup_env.sh` 一次装齐：Typst、XeLaTeX（TeX Live + 中文字体）、Pandoc、LibreOffice、Poppler、draw.io（headless wrapper）、Python 科学栈。Devin 环境蓝图已调用该脚本；本机请把 `~/.local/bin` 加入 `PATH`。

常用编译命令（在 `contest/<年>-<题>/` 内）：

```bash
typst compile --root . paper/main.typ                     # Typst → PDF
(cd paper && xelatex -interaction=nonstopmode main.tex && xelatex -interaction=nonstopmode main.tex)  # LaTeX → PDF
python3 ../../.agents/skills/docx-export/scripts/paper2docx.py --paper paper --pdf   # → DOCX (+PDF 抽检)
python3 ../../.agents/skills/scibox-diagram/scripts/export_figure.py figures/x.drawio # drawio → PNG/PDF
```

## 仓库维护

- 修改 skill 时保持 `SKILL.md` frontmatter 只有 `name` 与 `description`（Devin 按此发现技能）。
- 自检：`bash scripts/smoke_test.sh`（编译两套华为杯模板 + DOCX 导出 + drawio 导出）。
- 第三方来源与许可见 `THIRD_PARTY_NOTICES.md`；改动 vendored skill 时在该文件记录。
- 不要把比赛数据、队号、API Key 提交进仓库；`contest/` 默认被 `.gitignore` 忽略，赛后如需归档另开分支。
