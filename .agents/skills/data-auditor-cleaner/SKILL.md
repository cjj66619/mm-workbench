---
name: data-auditor-cleaner
description: Map contest attachments to subquestions, audit and clean raw data, and emit one reusable data profile with quality, coverage, imbalance, concentration, and method-readiness evidence for downstream risk screening.
---

# 在 mm-workbench（华为杯工作台）中的用法

本 skill 来自 zhnnky329/MathModeling-skills（MIT），作为 MathModelAgent 六阶段主流程的补强，在 `2analysis-modeling` 之后、`3coding-visual` 之前调用。目录映射：

- 原始附件只读放在 `data/raw/`，清洗后写入 `data/clean/`（对应原文的 `workspace/data_raw/`、`workspace/data_clean/`）。
- 数据报告写到 `reports/DATA_REPORT.md`，画像写到 `reports/data_profile.json`（对应原文的 `workspace/data/data_report.md` / `data_profile.json`）。
- 子问题 ID 直接使用 `reports/ANALYSIS_MODELING_REPORT.md` 里的问题编号（问题一 = Q1 …）。
- 不存在 `planning/manifests/`、`session_config.json` 时忽略相关要求，按 `lean` 处理。

---

# Purpose

Create traceable cleaned data and one reusable profile. Do not repeat the same data inspection separately for every candidate method.

# Preconditions

- Problem parse and subquestion IDs exist.
- Raw files are available under `workspace/data_raw/` or the workspace's documented legacy raw-data path.
- Required outputs and known field needs are available.

Stop rather than fabricate a missing attachment, unit, field meaning, or label.

# Workflow

1. **Map attachments before cleaning.**
   - List each attachment with name, size, sheet names, headers, and a small preview.
   - Map it to Qx or mark it shared.
   - Ask the user only when two mappings remain materially plausible.

2. **Preserve raw data.**
   - Treat raw files as read-only.
   - Record hashes or stable file metadata when practical.
   - Write cleaned copies under `workspace/data_clean/`.

3. **Audit structure and semantics.**
   - Rows, columns, keys, types, units, categories, time granularity, and encoding.
   - Missing values, duplicates, impossible values, outliers, discontinuities, and leakage risks.
   - Field-to-subquestion and field-to-required-output mapping.

4. **Compute reusable risk-profile statistics.**
   - Effective sample size and rows usable per Qx.
   - Missingness by field and row.
   - Numeric distribution summaries and extreme-value rates.
   - Category/class counts, imbalance ratios, rare levels, and cardinality.
   - Time coverage, gaps, sampling interval, and chronological split constraints.
   - Correlation/redundancy warnings where relevant.
   - Target or score concentration indicators when a target exists.
   - Record facts; do not convert them into a final method verdict.

5. **Plan and apply cleaning.**
   - Separate safe normalization of representation from assumption-bearing imputations or removals.
   - Explain and record every assumption-bearing operation.
   - Keep reproducible cleaning code only when transformations are nontrivial.

6. **Assess readiness per Qx.**
   - `ready`, `ready_with_warnings`, or `blocked`.
   - Name missing fields and risks precisely.
   - Hand the profile to `method-selector` for method-specific risk probes.

# Canonical Outputs

```text
workspace/data/data_report.md
workspace/data/data_profile.json
workspace/data_clean/<cleaned files>
workspace/code/scripts/<cleaning script>   # only when needed
```

Accept legacy `workspace/data/data_clean/` as an input/output location during migration.

# Data Profile Contract

`data_profile.json` contains:

```json
{
  "schema_version": 1,
  "raw_files": [],
  "attachment_mapping": [],
  "fields": [],
  "quality": {
    "missingness": {},
    "duplicates": {},
    "impossible_values": {},
    "outliers": {}
  },
  "coverage": {
    "rows": 0,
    "effective_sample_size": null,
    "time_range": null,
    "time_gaps": null
  },
  "distribution_risks": {
    "class_imbalance": null,
    "rare_categories": [],
    "high_cardinality": [],
    "redundancy_warnings": [],
    "concentration_metrics": {}
  },
  "per_question_readiness": {},
  "cleaned_files": [],
  "unresolved_risks": []
}
```

Use `null` with an explanation when a field is not applicable; do not invent a value to fill the schema.

# Rules

- Do not select the model.
- Do not overwrite raw data.
- Do not silently delete, impute, winsorize, rescale, or recode.
- Do not produce decorative EDA.
- Reuse one profile downstream instead of regenerating statistics.
- Store detailed row-level change logs only when changes occurred; successful no-op checks need only summary counts.

# Verification

- Attachment mapping is unambiguous or human-confirmed.
- Raw files remain untouched.
- Cleaned files trace to raw sources and transformation rules.
- Profile includes effective sample size, imbalance/cardinality, and concentration evidence when applicable.
- Readiness is reported per subquestion.
- Downstream handoff points to paths rather than pasting the full report.
