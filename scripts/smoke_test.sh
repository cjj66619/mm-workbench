#!/usr/bin/env bash
# 工作台自检：用华为杯 Typst / LaTeX 两套模板 + 一张 matplotlib 图 + 一张 drawio 图，
# 走完 编译 PDF → 导出 DOCX(+PDF) → 占位符/泄露检查 全链路。
#   bash scripts/smoke_test.sh            # 临时目录，跑完即删
#   KEEP=1 bash scripts/smoke_test.sh     # 保留产物目录供目检
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/.agents/skills/5writing/templates/zh"
DOCX="$ROOT/.agents/skills/docx-export/scripts/paper2docx.py"
DRAWIO="$ROOT/.agents/skills/scibox-diagram/scripts/export_figure.py"
WORK="$(mktemp -d /tmp/mm-smoke.XXXXXX)"
trap '[[ "${KEEP:-0}" == 1 ]] && echo "产物保留在 $WORK" || rm -rf "$WORK"' EXIT

step() { printf '\n== %s\n' "$*"; }

step "准备 figures/"
mkdir -p "$WORK/figures"
python3 - "$WORK/figures/fig_q1.pdf" <<'PY'
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rng = np.random.default_rng(0)
plt.figure(figsize=(6, 3.5)); plt.hist(rng.normal(size=500), bins=30); plt.title("residuals")
plt.tight_layout(); plt.savefig(sys.argv[1])
PY
cat > "$WORK/figures/flow.drawio" <<'EOF'
<mxfile><diagram name="p1"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="2" value="数据预处理" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="3" value="模型求解" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="240" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="4" style="edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="2" target="3"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel></diagram></mxfile>
EOF

step "drawio → PNG/PDF"
timeout 180 python3 "$DRAWIO" "$WORK/figures/flow.drawio" >/dev/null
test -s "$WORK/figures/flow.pdf" && test -s "$WORK/figures/flow.png"

step "Typst 模板：填占位符 + 插图 + 编译"
cp -r "$TPL/huaweibei" "$WORK/paper"
sed -i 's/\[论文标题\]/基于混合整数规划的冒烟测试论文/g;
        s/\[\[中文摘要内容：[^]]*\]\]/[本文建立回归模型，测试集 $R^2$ 达到 0.896。]/;
        s/\[关键词1\] #h(1em) \[关键词2\] #h(1em) \[关键词3\]/[回归] #h(1em) [优化]/' "$WORK/paper/main.typ"
cat >> "$WORK/paper/sections/5_problem1.typ" <<'EOF'

#figure(image("../../figures/fig_q1.pdf", width: 85%), caption: [问题一残差分布])
#figure(image("../../figures/flow.pdf", width: 70%), caption: [求解流程])
EOF
(cd "$WORK" && typst compile --root . paper/main.typ paper/main.pdf)
test -s "$WORK/paper/main.pdf"

step "Typst → DOCX（--strict，允许残留的 学校/队号 封面占位符不在正文，应为 0 占位符）"
python3 "$DOCX" --paper "$WORK/paper" --out "$WORK/paper/main.docx" --pdf --strict | tail -12

step "LaTeX 模板：填占位符 + 插图 + 编译"
cp -r "$TPL/huaweibei-latex" "$WORK/paper_tex"
sed -i 's/\[论文标题\]/基于混合整数规划的冒烟测试论文/g;
        s/中文摘要内容：问题概述 + 每个子问题的方法和数值结果 + 结论/本文建立回归模型，测试集 $R^2$ 达到 0.896。/;
        s/关键词1 \\quad 关键词2 \\quad 关键词3/回归 \\quad 优化/' "$WORK/paper_tex/main.tex"
cat >> "$WORK/paper_tex/sections/5_problem1.tex" <<'EOF'

\begin{figure}[H]\centering\includegraphics[width=0.85\textwidth]{../figures/fig_q1.pdf}\caption{问题一残差分布}\end{figure}
\begin{figure}[H]\centering\includegraphics[width=0.7\textwidth]{../figures/flow.pdf}\caption{求解流程}\end{figure}
EOF
(cd "$WORK/paper_tex" && xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null)
test -s "$WORK/paper_tex/main.pdf"

step "LaTeX → DOCX（--strict）"
python3 "$DOCX" --paper "$WORK/paper_tex" --out "$WORK/paper_tex/main.docx" --pdf --strict | tail -12

step "全部通过"
