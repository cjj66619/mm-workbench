---
name: mathmodel-figure-templates
description: Use this skill in the MathModel LaTeX sandbox when the user asks to reproduce built-in scientific visualization templates, especially prompts from the Improve tab mentioning $mathmodel-figure-templates, 科研绘图模板, SHAP蜂群柱状图, 配对云雨图, 交叉验证ROC, 泰勒图, 相关矩阵组合图, 预测真实值边缘分布图, TPE调参3D曲面, 下三角相关矩阵半边小提琴图, 分组环形热图, 城市公园降温组合图, or Nature和弦图. It provides ready-to-run Python scripts bundled inside the skill.
---

# MathModel Figure Templates

This skill is bundled into the LaTeX sandbox at `/home/user/.claude/skills/mathmodel-figure-templates`. It contains ready-to-run Python/matplotlib scripts for the figure templates exposed in the MathModel Improve tab.

## Fast Path

1. Match the requested chart in `references/figure-catalog.md`.
2. From `/home/user/workspace`, run the renderer with the template id:

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py paired-raincloud
```

3. The renderer copies the bundled template script into `绘图复刻/scripts/`, runs it there, and writes outputs to `绘图复刻/outputs/`.
4. Return the generated PNG/PDF/SVG paths and the copied script path to the user.

Use `--list` to show supported ids:

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py --list
```

## Output Contract

- Work under the current workspace unless the user gives another path.
- Default project folder: `绘图复刻`.
- Script path: `绘图复刻/scripts/make_<template>.py`.
- Outputs: `绘图复刻/outputs/<template>_replica.png`, `.pdf`, `.svg` (plus `outputs/_manifest.json` written by `save_fig`).
- `render_template.py` also copies the shared style module `mm_plot_style.py` (from `../3coding-visual/scripts/`) into `绘图复刻/scripts/`; every template calls `apply_style(...)` and `save_fig(...)` from it, so fonts, export and PDF font checks follow `../_references/figure_style.md`.
- Use the bundled scripts as the first choice; edit the copied workspace script only when the user requests customization.
- The bundled scripts use deterministic simulated data. Do not claim simulated values reproduce a source study exactly.

## Template Ids

- `multiclass-shap-combo`
- `paired-raincloud`
- `cv-roc-ci`
- `taylor-diagram`
- `correlation-pairgrid`
- `prediction-marginal-grid`
- `rf-tpe-surface`
- `grouped-corr-split-violin`
- `grouped-circular-heatmap`
- `urban-park-cooling-combo`
- `nature-chord-diagram`

## When Customizing

If the user asks for changes, copy/run the nearest template first, then edit the copied file in `绘图复刻/scripts/`. Preserve:

- `MPLCONFIGDIR` before importing matplotlib.
- `configure_matplotlib()` built on `mm_plot_style.apply_style(...)`; put template-specific tweaks in its `extra={...}` instead of calling `mpl.rcParams.update` with fonts.
- `save_fig(fig, output_stem, formats=("png", "pdf", "svg"))` for export (runs the PDF font check).
- deterministic seeds for simulated data.
- readable labels, legends, and high-DPI output.

For a Chinese-language paper switch `apply_style(lang="zh")` and translate in-figure text; the module picks a TrueType CJK font so the PDF survives the DOCX conversion.

Use `references/plot-recipes.md` for implementation patterns.
