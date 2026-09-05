# 2024-B 全流程演练断点清单

演练：2024 华为杯 B 题（WLAN 组网吞吐量预测），从题面 + 13 个训练 CSV 到 Typst PDF（30 页）+ DOCX 完整跑一遍六阶段流水线。
下面记录暴露出的断点、当时的处理和已经落回工作台的修复；未修复项标 **TODO**。

## 已修复（本次提交）

| # | 阶段 | 断点 | 修复 |
| --- | --- | --- | --- |
| 1 | docx-export | `--pdf` 用 LibreOffice 渲染时写到 `paper/main.pdf`，**覆盖了 Typst 原生 PDF** | 渲染结果改写到 `paper/docx_render/main.pdf` |
| 2 | docx-export | 摘要写在 `#include("abstract.typ")` 里时抽不到，DOCX 出现 `[中文摘要内容]` 占位符 | 抽取时把含 `关键词：` 的 include 文件内联 |
| 3 | docx-export | pandoc 不解析 Typst `@fig-x`/`@tbl-x`，DOCX 里出现 24 处 `[fig-roadmap]` 原文 | 影子目录预处理：按顺序替换为 `图 N`/`表 N`、去 `<label>` |
| 4 | 5writing/typst | `lib.typ` 里 `fig()` 自己 `image()` 相对路径解析到 lib 所在目录，`--root .` 下报 `would escape the project root` | `fig(body, caption)` 只接收已构造好的 `image(...)`，图片路径在 section 文件里写 |
| 5 | 6verity | `lib.typ` 注释里的示例路径 `../../figures/x.pdf` 被当作缺失图 | 注释改为无路径说明 |
| 6 | 3coding-visual ↔ 5writing | 代码 400 棵树，报告/论文写 500 | consistency 审计抓到并改正；规则：超参只从代码 `env_info()`/`results/*.json` 抄 |

## 记录但不阻塞

| # | 阶段 | 现象 | 处理 |
| --- | --- | --- | --- |
| 7 | typst | 字体族 `simsun/simhei/menlo/times new roman` 等 unknown font warning，PDF 用回退字体渲染正常 | 蓝图已装 Noto CJK；正式赛若要求宋体/黑体，装 `fonts-arphic` 或拷官方字体到 `~/.fonts` |
| 8 | typst | `Syntax Error: Suspects object is wrong type (boolean)`，PDF 仍正常生成 | 来自嵌入的 matplotlib PDF 图元数据，不影响输出 |
| 9 | docx-export | DOCX 页数（34）≠ Typst 页数（30） | 转换固有差异，DOCX 只作可编辑交稿件 |
| 10 | 4drawio | 中文标签超出文本槽位，layout check 多次 FAIL | 缩短标签/手工换行后过；建议模板文本槽位留 30% 余量 |
| 11 | 2analysis-modeling | 探针阶段随机 K 折 vs 按地点留一（LOGO）差距大（Q3 级联 80% → 28%） | 已写入 `math_modeling_norms.md`：测试集为未见分组时必须用分组 CV |
| 12 | 全流程 | 用户对话额度紧张，后期要求“快点出论文” | 审计只跑必要项；建议正式赛按 `plan.md` 时间表把审计压缩为 6verity + 一次 QA |

## TODO

- [ ] `hwb-kickoff` Step 2：当届官方封面到位后要有一步 `title.pdf/logo.pdf` 替换 + `assets/title.typ` 届数校对的自动检查（目前靠人工）。
- [ ] `robustness-checker`：CONDITIONAL 结论（本次 Q1-R5、Q2-R5）应自动生成一段可直接粘进论文“模型评价”的风险描述模板。
- [ ] `docx-export`：公式编号 `(1)` 在 DOCX 中丢失（pandoc 限制），如评审要求编号需在 Word 里手工补。
