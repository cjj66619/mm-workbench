#!/usr/bin/env bash
# mm-workbench 工具链安装 / 体检脚本（Ubuntu 22.04+ / Debian，需 sudo）。
#   bash scripts/setup_env.sh          # 安装缺失项
#   bash scripts/setup_env.sh --check  # 只检查不安装
# Devin 环境蓝图直接调用本脚本；本机手动使用亦可。
set -euo pipefail

TYPST_VERSION="${TYPST_VERSION:-0.15.1}"
PANDOC_VERSION="${PANDOC_VERSION:-3.8.3}"
DRAWIO_VERSION="${DRAWIO_VERSION:-31.4.2}"
BIN="$HOME/.local/bin"
CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

mkdir -p "$BIN"
export PATH="$BIN:$PATH"

APT_PKGS=(
  texlive-xetex texlive-lang-chinese texlive-latex-extra texlive-fonts-recommended
  # Typst/LaTeX 中文：Noto CJK；matplotlib 中文必须是 TrueType（Noto CJK 为 CFF，配 pdf.fonttype=42 会出乱码 PDF）：文泉驿
  # 西文替代 Times New Roman：Liberation Serif（同字宽）；楷体：文鼎 AR PL KaitiM GB（lib.typ 摘要页标签）
  fonts-noto-cjk fonts-noto-cjk-extra fonts-wqy-zenhei fonts-wqy-microhei fonts-liberation fonts-arphic-gkai00mp fonts-dejavu
  poppler-utils libreoffice-writer libreoffice-math xvfb
  python3-pip python3-venv
)
PY_PKGS=(
  numpy scipy pandas matplotlib seaborn scikit-learn statsmodels
  pulp networkx openpyxl python-docx pymupdf
)

ok()   { printf 'OK   %-14s %s\n' "$1" "$2"; }
miss() { printf 'MISS %-14s %s\n' "$1" "$2"; }

have() { command -v "$1" >/dev/null 2>&1; }

install_apt() {
  local missing=()
  for p in "${APT_PKGS[@]}"; do
    dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p")
  done
  ((${#missing[@]})) || return 0
  echo ">> apt install: ${missing[*]}"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${missing[@]}"
}

install_typst() {
  have typst && return 0
  echo ">> install typst $TYPST_VERSION"
  curl -sSL "https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-x86_64-unknown-linux-musl.tar.xz" \
    | tar -xJ -C /tmp
  install -m755 "/tmp/typst-x86_64-unknown-linux-musl/typst" "$BIN/typst"
}

install_pandoc() {
  have pandoc && return 0
  echo ">> install pandoc $PANDOC_VERSION"
  curl -sSL "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz" \
    -o /tmp/pandoc.tgz
  tar -xzf /tmp/pandoc.tgz -C /tmp
  install -m755 "/tmp/pandoc-${PANDOC_VERSION}/bin/pandoc" "$BIN/pandoc"
}

install_drawio() {
  # draw.io 桌面版自带命令行导出；headless 环境需 xvfb + --no-sandbox，用 wrapper 统一封装
  if ! [[ -x /usr/bin/drawio ]]; then
    echo ">> install drawio $DRAWIO_VERSION"
    curl -sSL "https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb" \
      -o /tmp/drawio.deb
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq /tmp/drawio.deb
  fi
  cat > "$BIN/drawio" <<'EOF'
#!/bin/sh
# headless wrapper: drawio -x -f pdf -o out.pdf in.drawio
if [ -n "${DISPLAY:-}" ] && xdpyinfo >/dev/null 2>&1; then
  exec /usr/bin/drawio --no-sandbox --disable-gpu "$@"
fi
exec xvfb-run -a /usr/bin/drawio --no-sandbox --disable-gpu "$@"
EOF
  chmod +x "$BIN/drawio"
}

install_python() {
  python3 -m pip install -q --user "${PY_PKGS[@]}"
}

check_all() {
  local fail=0
  for c in typst xelatex pandoc soffice pdftoppm drawio xvfb-run python3; do
    if have "$c"; then ok "$c" "$(command -v "$c")"; else miss "$c" ""; fail=1; fi
  done
  for f in "Noto Serif CJK SC" "Noto Sans CJK SC" "WenQuanYi Micro Hei" "Liberation Serif" "AR PL KaitiM GB"; do
    if [[ -n "$(fc-list "$f")" ]]; then ok "font" "$f"; else miss "font" "$f"; fail=1; fi
  done
  python3 - <<'PY' || fail=1
import importlib, sys
mods = {"numpy":"numpy","scipy":"scipy","pandas":"pandas","matplotlib":"matplotlib","seaborn":"seaborn",
        "sklearn":"scikit-learn","statsmodels":"statsmodels","pulp":"pulp","networkx":"networkx",
        "openpyxl":"openpyxl","docx":"python-docx","pymupdf":"pymupdf"}
bad = 0
for m, pkg in mods.items():
    try:
        importlib.import_module(m); print(f"OK   py:{pkg}")
    except ImportError:
        print(f"MISS py:{pkg}"); bad = 1
sys.exit(bad)
PY
  # matplotlib 中文：mm_plot_style 必须能选到 TrueType 中文字体（否则出图中文乱码/不可提取）
  python3 - "$(dirname "$0")/../.agents/skills/3coding-visual/scripts" <<'PY' || fail=1
import os, sys
os.environ.setdefault("MPLBACKEND", "Agg")
sys.path.insert(0, sys.argv[1])
from mm_plot_style import resolve_fonts
info = resolve_fonts(font="sans", lang="zh")
if info["cjk"] and info["cjk_kind"] == "truetype":
    print(f"OK   mpl-cjk        {info['cjk']} (TrueType, pdf.fonttype=42)")
else:
    print(f"MISS mpl-cjk        {info['cjk'] or 'none'} ({info['cjk_kind']})"); sys.exit(1)
PY
  return $fail
}

if (( CHECK_ONLY )); then
  check_all
  exit $?
fi

install_apt
install_typst
install_pandoc
install_drawio
install_python
echo
check_all
echo
echo "完成。请确保 $BIN 在 PATH 中（export PATH=\"$BIN:\$PATH\"）。"
