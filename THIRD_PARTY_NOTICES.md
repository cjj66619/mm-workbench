# 第三方来源与许可说明

本仓库为**个人参赛用途**的公开仓库，vendored 内容如下。任何商业用途前请先核对各上游许可。

| 目录（`.agents/skills/`） | 上游 | 提交 | 许可 | 本仓库改动 |
| --- | --- | --- | --- | --- |
| `1start-mathmodel` `2analysis-modeling` `3coding-visual` `4drawio` `5writing` `6verity` `doctor` `_references` `typst-author` `mathmodel-figure-templates` | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) `skills/` | `83d8783` | 作者自定：个人免费使用、禁止商业用途、禁止闭源分发、不得据此提供商业服务（见上游 `docs/md/License.md`） | 删除 `allowed-tools` frontmatter；修正 LaTeX 图片路径说明与 `--root .` 编译说明；华为杯模板增加 Linux 字体回退、去掉 `fontset=mac`、加 `float` 包；新增 `templates/zh/huaweibei/assets/title.typ`（题头可编辑源）；`3coding-visual` 新增 `scripts/mm_plot_style.py` / `check_figures.py` 并强制使用；`mathmodel-figure-templates` 的 11 个模板脚本改为调用 `mm_plot_style.apply_style/save_fig`（保留原数据、种子与布局），`render_template.py` 一并复制该模块 |
| `_references/figure_style.md`、`3coding-visual/scripts/mm_plot_style.py`（规范来源） | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) `skills/nature-figure/` | `28150f3` | Apache-2.0 | 未直接 vendored 上源代码；参考其设计原则、字号/线宽/尺寸/导出与 QA 约定，结合华为杯中文论文需求自行实现 |
| `scibox-diagram` | [jihe520/sci-box](https://github.com/jihe520/sci-box) `skills/` | `9687d2a` | 上游未附独立 LICENSE 文件，作者同上，按 MathModelAgent 同等条款理解 | 无实质改动 |
| `data-auditor-cleaner` `robustness-checker` `consistency-auditor` `quality-assurance-auditor` | [zhnnky329/MathModeling-skills](https://github.com/zhnnky329/MathModeling-skills) `.codex/skills/` | `046a6e7` | MIT（Copyright (c) 2026 Zhijun Zhang） | 每个 `SKILL.md` 顶部增加「工作台适配说明」，把上游 `workspace/data_raw` 等路径映射到本仓库 `data/raw` 等 |
| `docx-export` `hwb-kickoff` | 本仓库原创 | — | 与本仓库相同 | — |

未采用：[XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) 的 DOCX 工具随附的是 Anthropic 使用协议而非开源许可，故本仓库 DOCX 链路改用 Pandoc + python-docx 自行实现。

华为杯官方论文模板（封面、校徽、赛徽等）版权归中国研究生创新实践系列大赛组委会；`paper/logo.pdf` / `title.pdf` 仅作排版演练占位，正式提交须以当届官网发布的模板为准。
