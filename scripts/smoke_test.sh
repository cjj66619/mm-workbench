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
PLOT="$ROOT/.agents/skills/3coding-visual/scripts"
WORK="$(mktemp -d /tmp/mm-smoke.XXXXXX)"
trap '[[ "${KEEP:-0}" == 1 ]] && echo "产物保留在 $WORK" || rm -rf "$WORK"' EXIT

step() { printf '\n== %s\n' "$*"; }

step "准备 figures/（matplotlib 中文图，经 mm_plot_style 统一风格）"
mkdir -p "$WORK/figures" "$WORK/code"
cp "$PLOT/mm_plot_style.py" "$WORK/code/"
(cd "$WORK" && python3 - <<'PY'
import sys
sys.path.insert(0, "code")
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mm_plot_style import apply_style, COLORS, figsize, save_fig

info = apply_style(lang="zh")
print(f"字体: latin={info['latin']} cjk={info['cjk']} ({info['cjk_kind']}) pdf.fonttype={info['pdf_fonttype']}")
assert info["cjk"], "未找到中文字体"
assert info["cjk_kind"] == "truetype" and info["pdf_fonttype"] == 42, "中文字体不是 TrueType，无法用 fonttype=42 安全导出"
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=figsize("full", aspect=0.5))
ax.hist(rng.normal(size=500), bins=30, color=COLORS[0], label="残差频数")
ax.axvline(0, color=COLORS[1], lw=1, label="零均值线")
ax.set_xlabel("残差 (万元)"); ax.set_ylabel("频数"); ax.legend()
# matplotlib 直出 PNG 作为参考；论文只用 PDF，让 docx-export 走 PDF→PNG 转换链路
fig.savefig("code/ref_q1.png", dpi=300)
save_fig(fig, "figures/fig_q1", formats=("pdf",), source="smoke:rng(0)", params={"n": 500, "bins": 30})
PY
)
python3 "$PLOT/check_figures.py" --expect-cjk --strict "$WORK/figures/fig_q1.pdf"
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
        s/\[中文摘要内容：[^]]*\]/本文建立回归模型，测试集 $R^2$ 达到 0.896。/;
        s/\[关键词1\] #h(2em) \[关键词2\] #h(2em) \[关键词3\]/[回归] #h(1em) [优化]/' "$WORK/paper/main.typ"
cat >> "$WORK/paper/sections/5_problem1.typ" <<'EOF'

#figure(image("../../figures/fig_q1.pdf", width: 85%), caption: [问题一残差分布])
#figure(image("../../figures/flow.pdf", width: 70%), caption: [求解流程])
EOF
(cd "$WORK" && typst compile --root . paper/main.typ paper/main.pdf)
test -s "$WORK/paper/main.pdf"

step "Typst → DOCX（--strict，允许残留的 学校/队号 封面占位符不在正文，应为 0 占位符）"
python3 "$DOCX" --paper "$WORK/paper" --out "$WORK/paper/main.docx" --pdf --strict | tail -12

step "DOCX 链路中文图不乱码：docx-export 转出的 PNG 与 matplotlib 直出 PNG 一致"
(cd "$WORK" && python3 - <<'PY'
import zipfile
import numpy as np
from PIL import Image

# docx-export 从 fig_q1.pdf 转出的 PNG（与嵌入 Word 的是同一张） vs matplotlib 直出的参考 PNG
conv = np.asarray(Image.open("figures/fig_q1.png").convert("L"), dtype=float)
ref = np.asarray(Image.open("code/ref_q1.png").convert("L"), dtype=float)
assert abs(conv.shape[0] - ref.shape[0]) <= 4 and abs(conv.shape[1] - ref.shape[1]) <= 4, f"尺寸不一致 {conv.shape} vs {ref.shape}"
h = min(conv.shape[0], ref.shape[0]); w = min(conv.shape[1], ref.shape[1])
diff = np.abs(conv[:h, :w] - ref[:h, :w])
ink_ref = (ref[:h, :w] < 128).sum(); ink_conv = (conv[:h, :w] < 128).sum()
ratio = ink_conv / max(ink_ref, 1)
print(f"转换图 {conv.shape[1]}x{conv.shape[0]} 参考图 {ref.shape[1]}x{ref.shape[0]} 墨量比 {ratio:.3f} 平均像素差 {diff.mean():.2f}")
assert 0.9 < ratio < 1.1, "PDF→PNG 转换后墨量与参考图相差过大（中文丢失或方块）"
assert diff.mean() < 6, "PDF→PNG 转换图与参考图像素差异过大"
media = [n for n in zipfile.ZipFile("paper/main.docx").namelist() if n.startswith("word/media/")]
assert len(media) >= 2, f"DOCX 内嵌图片不足: {media}"
print("DOCX media:", media)
PY
)

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
