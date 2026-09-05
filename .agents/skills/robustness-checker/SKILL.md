---
name: robustness-checker
description: Design and run risk-targeted robustness, sensitivity, error, and baseline checks for an approved mathematical model, emitting compact machine evidence in lean mode and a final report in submission mode.
---

# 在 mm-workbench（华为杯工作台）中的用法

本 skill 来自 zhnnky329/MathModeling-skills（MIT），在 `3coding-visual` 出结果后、`5writing` 之前调用，用于生成论文"灵敏度/稳健性分析"章节的证据。目录映射：

- 被检模型与代码：`code/`；主结果：`reports/RESULTS_REPORT.md`；数值结果文件：`results/`。
- 输出写到 `robustness/Qx/qx_robustness_summary.json`，`submission` 模式再补 `robustness/Qx/qx_robustness_report.md`，并把结论回填到 `reports/RESULTS_REPORT.md` 的"稳健性"小节，供 `5writing` 引用。
- 灵敏度图仍按 `3coding-visual` 的规范输出到 `figures/`（PDF）。
- 不存在 `planning/manifests/`、`qx_decisions.jsonl` 时忽略相关要求，PASS/CONDITIONAL/FAIL 结论由人确认后再写进论文。

---

# Purpose

Test the claims most likely to fail. Choose checks from the model's assumptions and decision risks rather than filling a generic checklist.

# Preconditions

- Approved main and usable baseline executed.
- Run summary, method card, probe summary, and relevant outputs exist.
- Claim or decision to be tested is known.

# Workflow

1. Identify load-bearing assumptions and claims.
2. Select applicable checks:
   - parameter or weight perturbation;
   - alternate split or resampling;
   - seed stability;
   - outlier/missing-data treatment;
   - constraint/capacity perturbation;
   - baseline comparison;
   - output concentration/rank stability;
   - error and uncertainty analysis.
3. State perturbation ranges and why they are meaningful before interpreting results.
4. Run checks with fixed seeds where stochastic.
5. Save compact metrics to:

`robustness/Qx/qx_robustness_summary.json`

6. In `submission`, also save:

`robustness/Qx/qx_robustness_report.md`

7. If the stability verdict affects method continuation or claim scope, invoke one choice card and log the human answer in `qx_decisions.jsonl`.

# Summary Contract

Record:

- tested claim/assumption;
- input and result source paths;
- perturbation;
- metric and threshold if predeclared;
- observed value;
- status `PASS`, `CONDITIONAL`, or `FAIL`;
- limitation;
- fallback-trigger relevance.

# Rules

- Do not run irrelevant checks merely to reach a count.
- Do not invent a threshold after seeing the result without labeling it exploratory.
- Do not convert stability metrics into the human confidence verdict.
- Do not create `robustness-checker_modeler_decision.md`.
- A failed robustness check is evidence for adjust/fallback/claim downgrade, not permission for AI to decide.

# Verification

- Every major final claim has a supporting check or explicit limitation.
- Perturbations are justified and reproducible.
- Baseline and main comparisons remain metric-compatible.
- Concentration/degeneracy risks are revisited when relevant.
- Submission report sources its numbers from the summary and experiment artifacts.
