---
name: _references
description: "共享规范知识库。包含数学建模竞赛的写作规范、题型防错速查、图表规范等参考内容。其他 skills 在执行过程中按需读取，无需单独触发。"
---

# _references

本文件夹是共享规范知识库，不是可独立执行的 skill。

其他 skills 在需要领域判断时会读取 `math_modeling_norms.md` 中的相关小节。请勿手动触发此 skill。

文件清单：

- `math_modeling_norms.md`：通用规范（题型防错、建模、代码、图表、写作、验收）。
- `figure_style.md`：数据图绘图规范（nature-skills 风格落地：字体/字号/线宽/配色/尺寸/导出、中文乱码根因与检查）。`3coding-visual`、`mathmodel-figure-templates` 出图时读取，执行入口为 `3coding-visual/scripts/mm_plot_style.py`。
- `huaweibei_body_format.md`：华为杯官方正文排版参数（页边距、标题、字体、图表题、公式、参考文献）。`5writing`、`docx-export`、`6verity` 的排版改动以此为准。
- `huaweibei_excellent_paper_patterns.md`：华为杯专用。官方模板明文要求（含 AI 工具使用声明格式）、优秀论文结构统计、摘要与小问章节范式、验收对标清单。`hwb-kickoff`、`5writing`、`6verity`、`quality-assurance-auditor` 在华为杯场景下读取。文中 [官方]/[样本]/[建议] 三类标签必须区分使用。
- `rehearsal_2024B_breakpoints.md`：2024-B 全流程演练暴露的断点、已修复项与 TODO。`hwb-kickoff` 开赛前浏览一次，避免重复踩坑。
