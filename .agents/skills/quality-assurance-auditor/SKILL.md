---
name: quality-assurance-auditor
description: Perform the final submission-level audit of mathematical-modeling workflow integrity, evidence quality, anti-fabrication, paper coherence, figures, references, and contest readiness after consistency and completeness audits pass.
---

# 在 mm-workbench（华为杯工作台）中的用法

本 skill 来自 zhnnky329/MathModeling-skills（MIT），作为提交前最后一道审计，在 `6verity` 完成编译与格式检查之后调用。映射：

- 事实来源同 `consistency-auditor`（`reports/RESULTS_REPORT.md`、`reports/ANALYSIS_MODELING_REPORT.md`、`plan.md`）。
- 审计结果写到 `reports/audits/final_quality_assurance_audit.md`；PDF/DOCX 交稿件在 `paper/`。
- 华为杯专项检查：封面/摘要页使用当届官方格式、正文无参赛队信息、无工作流内部文件名、图表编号连续、参考文献可追溯。
- 华为杯国一对标（读 `../_references/huaweibei_excellent_paper_patterns.md`，按 §6 清单逐项抽样核对，`6verity` 的 Step 6b 已做过一遍，这里独立复核而不是复制其结论）：
  - [官方] AI 工具声明：参考文献条目 + 正文/附录标注，与 `reports/AI_USAGE.md` 一致——这是 Presentation 维度第 5 条 "AI-use disclosure" 在华为杯下的具体规则；
  - [官方] 摘要 ≤ 2 页、公式非截图、附录含支撑材料文件列表；
  - [建议] 每问具备"结果分析与验证 + 小结"，每个主模型有至少一种验证证据，多方案对比使用同一套指标，小结回到题目原问；
  - [建议] 摘要每问一段且含可核验数值，数值与冻结结果一致；模型评价的优缺点对应本文具体做法。
  - 违反 [官方] 项为 blocking；违反 [建议] 项为 nonblocking，但需在报告中列出位置。

---

# Preconditions

- `rigor_profile` is `submission`.
- All Qx reached G5.
- Final consistency and completeness audits exist.

# Audit Dimensions

1. **Workflow integrity**
   - G1–G5 passed per Qx.
   - Human judgments trace to the decision ledger.
   - Main/baseline/fallback execution respected approved scope.

2. **Evidence integrity**
   - No fabricated data, references, experiments, metrics, or figures.
   - Main claims trace to frozen numbers and robustness evidence.
   - Limitations and uncertainty are visible.

3. **Method quality**
   - Baseline is usable.
   - Assumptions, units, objectives, constraints, and solution steps are coherent.
   - Output concentration/degeneracy and failure triggers were addressed.

4. **Paper quality**
   - Problem, method, results, and conclusions align.
   - Claims are proportional to tested comparisons.
   - Human-owned physical meaning and contribution are present.

5. **Presentation**
   - Required figures/tables exist and passed render checks.
   - Figure types are used correctly.
   - References are real, complete, and consistently cited.
   - AI-use disclosure follows the current contest profile and verified rules.

# Workflow

1. Read the two earlier audits and unresolved blockers.
2. Sample canonical sources directly; do not trust summaries alone.
3. Record blocking and nonblocking findings with artifact paths and repair owners.
4. Save `paper/qa_report.md`.
5. Set verdict:
   - `PASSED`
   - `FAILED`
   - `NOT_RUN`

# Rules

- Do not approve on partial audits.
- Do not use artifact count or bullet count as a proxy for quality.
- Do not repair issues inside QA.
- Do not hide uncertainty or downgrade a blocker silently.
- Do not claim compliance with time-varying contest rules without verification.

# Verification

- All five audit dimensions were evaluated.
- Blocking findings are explicit and actionable.
- QA verdict agrees with consistency/completeness verdicts and sampled evidence.
- Final assembly is recommended only when all three audits pass.
