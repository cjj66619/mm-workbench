"""mm-workbench 统一绘图风格（Matplotlib）。

规范来源：nature-skills/nature-figure 的 Python 后端约定（sans-serif、7–9 pt、
细坐标轴、无图例边框、svg.fonttype=none、pdf.fonttype=42）+ 华为杯中文论文与
DOCX 交稿链路的字体约束。详细说明见 `_references/figure_style.md`。

用法（把本文件复制到项目 `code/` 目录，与绘图脚本同级）::

    from mm_plot_style import apply_style, COLORS, figsize, save_fig

    apply_style(lang="zh")                    # 中文论文；英文论文用 lang="en"
    fig, ax = plt.subplots(figsize=figsize("full"))
    ax.plot(x, y, color=COLORS[0], label="预测值")
    save_fig(fig, "figures/fig_q1_fit", source="results/q1_fit.csv")

中文乱码根因：Linux 上常见的 Noto CJK 是 CFF(OTF) 轮廓，Matplotlib 在
``pdf.fonttype=42`` 下会把它当 TrueType 嵌入，生成非法字体流，PDF→PNG 转换后
乱码；而 ``pdf.fonttype=3`` 虽能显示，但文字不可提取/检索。因此本模块只挑选
TrueType(glyf) 轮廓的中文字体（如 WenQuanYi Micro Hei / Zen Hei、AR PL UMing），
配合 ``pdf.fonttype=42``；``save_fig`` 默认调用 ``check_pdf`` 做字体与文本自检。
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
from cycler import cycler
from matplotlib import font_manager as fm

__all__ = [
    "COLORS",
    "PALETTES",
    "SEQUENTIAL_CMAP",
    "DIVERGING_CMAP",
    "TEXT_WIDTH_CM",
    "FIG_WIDTHS_CM",
    "apply_style",
    "figsize",
    "save_fig",
    "check_pdf",
    "resolve_fonts",
    "active_fonts",
    "label_panels",
]

# --------------------------------------------------------------------------- #
# 调色板（nature-skills DEFAULT_COLORS 语义色 + 同方法族 pastel + 灰度）
# --------------------------------------------------------------------------- #
PALETTES: dict[str, list[str]] = {
    # 语义清晰、灰度下明暗有序：主方法蓝、对照红、第二组绿、青、紫、中性灰
    "default": ["#1F77B4", "#D62728", "#2CA02C", "#17BECF", "#9467BD", "#7F7F7F"],
    # 同一方法族多面板对比（NMI pastel）
    "pastel": ["#8EC1DA", "#F4A582", "#A6D96A", "#B2ABD2", "#FDB863", "#BABABA"],
    # 黑白打印/灰度审稿
    "gray": ["#000000", "#4D4D4D", "#7F7F7F", "#A6A6A6", "#CCCCCC", "#E5E5E5"],
}
COLORS: list[str] = PALETTES["default"]
SEQUENTIAL_CMAP = "viridis"   # 单向数值：热力图、密度
DIVERGING_CMAP = "RdBu_r"     # 有中心值：相关系数、残差
# 禁止：jet / rainbow / hsv 等彩虹色

# --------------------------------------------------------------------------- #
# 尺寸：A4 210 mm − 2×25 mm 边距 = 160 mm 版心
# --------------------------------------------------------------------------- #
TEXT_WIDTH_CM = 16.0
FIG_WIDTHS_CM: dict[str, float] = {
    "full": 14.0,        # 单栏整宽图，插入论文时按 ≈85–90% 版心
    "two-thirds": 10.5,
    "half": 7.5,         # 两图并排
    "third": 5.0,
}
_CM = 1 / 2.54

# --------------------------------------------------------------------------- #
# 字体候选（按优先级；只保留 Matplotlib 能识别、且轮廓为 TrueType 的）
# --------------------------------------------------------------------------- #
LATIN_SANS = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]
LATIN_SERIF = ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
CJK_SANS = [
    "SimHei", "Microsoft YaHei", "PingFang SC", "Heiti SC",
    "Source Han Sans SC", "Noto Sans CJK SC",
    "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Noto Sans CJK JP",
    "Droid Sans Fallback",
]
CJK_SERIF = [
    "SimSun", "Songti SC", "STSong",
    "Source Han Serif SC", "Noto Serif CJK SC",
    "AR PL UMing CN", "AR PL SungtiL GB", "Noto Serif CJK JP",
]
_CJK_PROBE = "中文图例测试"
_ACTIVE: dict[str, object] = {}


def _outline_kind(path: str) -> str:
    """返回字体轮廓类型：'truetype' | 'cff' | 'unknown'。"""
    try:
        with open(path, "rb") as fh:
            head = fh.read(4)
            if head == b"ttcf":
                fh.seek(12)
                off = int.from_bytes(fh.read(4), "big")
                fh.seek(off)
                head = fh.read(4)
    except OSError:
        return "unknown"
    if head in (b"\x00\x01\x00\x00", b"true"):
        return "truetype"
    if head == b"OTTO":
        return "cff"
    return "unknown"


def _find_font(name: str) -> str | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return fm.findfont(fm.FontProperties(family=name), fallback_to_default=False)
    except ValueError:
        return None


def _font_has_glyphs(path: str, text: str) -> bool:
    try:
        from matplotlib.ft2font import FT2Font
        face = FT2Font(path)
        return all(face.get_char_index(ord(ch)) != 0 for ch in text)
    except Exception:  # noqa: BLE001 - 探测失败视为不可用
        return False


def resolve_fonts(font: str = "sans", lang: str = "zh", require_truetype: bool = True) -> dict[str, object]:
    """挑选 Latin 与中文字体，返回 {'latin','cjk','cjk_kind','pdf_fonttype','family'}。"""
    latin_cands = LATIN_SANS if font == "sans" else LATIN_SERIF
    cjk_cands = (CJK_SANS if font == "sans" else CJK_SERIF + CJK_SANS)

    latin = next((n for n in latin_cands if _find_font(n)), "DejaVu Sans")

    cjk: str | None = None
    cjk_kind = "none"
    fallback: tuple[str, str] | None = None
    if lang == "zh":
        for name in cjk_cands:
            path = _find_font(name)
            if not path or not _font_has_glyphs(path, _CJK_PROBE):
                continue
            kind = _outline_kind(path)
            if kind == "truetype":
                cjk, cjk_kind = name, kind
                break
            fallback = fallback or (name, kind)
        if cjk is None and fallback is not None:
            cjk, cjk_kind = fallback
    pdf_fonttype = 42
    if lang == "zh" and cjk is None:
        warnings.warn(
            "未找到任何中文字体，中文将显示为方块；请安装 fonts-wqy-microhei / fonts-wqy-zenhei。",
            stacklevel=2,
        )
    elif cjk_kind == "cff":
        if require_truetype:
            pdf_fonttype = 3
        warnings.warn(
            f"中文字体 {cjk} 为 CFF/OTF 轮廓，pdf.fonttype=42 会导出非法 PDF；"
            "已降级为 fonttype=3（文字不可检索）。建议安装 fonts-wqy-microhei 以获得 TrueType 中文字体。",
            stacklevel=2,
        )
    family = [latin] + ([cjk] if cjk else []) + ["DejaVu Sans"]
    return {"latin": latin, "cjk": cjk, "cjk_kind": cjk_kind, "pdf_fonttype": pdf_fonttype, "family": family}


def apply_style(
    *,
    font: str = "sans",
    lang: str = "zh",
    base_size: float = 9.0,
    palette: str = "default",
    spines: str = "open",
    extra: dict | None = None,
) -> dict[str, object]:
    """应用统一 rcParams。

    font: 'sans'（默认，正文图）| 'serif'
    lang: 'zh' 启用中文字体 fallback；'en' 仅 Latin
    base_size: 图内基准字号（pt），期刊 7–9，论文正文图 9
    spines: 'open' 关闭上/右脊线（默认）| 'box' 四边框
    """
    if font not in ("sans", "serif"):
        raise ValueError("font 必须是 'sans' 或 'serif'")
    if palette not in PALETTES:
        raise ValueError(f"palette 必须是 {sorted(PALETTES)} 之一")
    info = resolve_fonts(font=font, lang=lang)
    family = info["family"]
    rc = {
        "font.family": family,
        "font.sans-serif": family if font == "sans" else LATIN_SANS,
        "font.serif": family if font == "serif" else LATIN_SERIF,
        "font.size": base_size,
        "axes.titlesize": base_size,
        "axes.labelsize": base_size,
        "xtick.labelsize": base_size - 1,
        "ytick.labelsize": base_size - 1,
        "legend.fontsize": base_size - 1,
        "legend.title_fontsize": base_size - 1,
        "figure.titlesize": base_size,
        "mathtext.fontset": "dejavusans" if font == "sans" else "dejavuserif",
        "axes.unicode_minus": False,        # 负号用 ASCII '-'，避免中文字体缺 U+2212
        "pdf.fonttype": info["pdf_fonttype"],
        "ps.fonttype": 42,
        "svg.fonttype": "none",             # SVG 保留可编辑文字
        "axes.linewidth": 0.8,
        "axes.spines.top": spines == "box",
        "axes.spines.right": spines == "box",
        "axes.grid": False,
        "axes.axisbelow": True,
        "axes.prop_cycle": cycler(color=PALETTES[palette]),
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "patch.linewidth": 0.6,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.width": 0.6,
        "ytick.minor.width": 0.6,
        "legend.frameon": False,
        "legend.handlelength": 1.5,
        "legend.borderaxespad": 0.3,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "figure.dpi": 100,
        "image.cmap": SEQUENTIAL_CMAP,
        "errorbar.capsize": 2,
    }
    if extra:
        rc.update(extra)
    mpl.rcParams.update(rc)
    _ACTIVE.clear()
    _ACTIVE.update({**info, "font": font, "lang": lang, "base_size": base_size, "palette": palette})
    return dict(_ACTIVE)


def active_fonts() -> dict[str, object]:
    """最近一次 apply_style 选定的字体信息。"""
    return dict(_ACTIVE)


def figsize(width: str | float = "full", aspect: float = 0.62, height_cm: float | None = None) -> tuple[float, float]:
    """按版心宽度给出 figsize（英寸）。width 可为 FIG_WIDTHS_CM 的键或 cm 数值。"""
    w_cm = FIG_WIDTHS_CM[width] if isinstance(width, str) else float(width)
    h_cm = height_cm if height_cm is not None else w_cm * aspect
    return (w_cm * _CM, h_cm * _CM)


def label_panels(axes: Iterable, labels: Sequence[str] | None = None, *, x: float = -0.12, y: float = 1.05,
                 fontsize: float | None = None, weight: str = "bold") -> None:
    """为多面板图加 (a)(b)(c) 标签，位置以每个 axes 的左上角为基准。"""
    axes = list(axes)
    labels = labels or [f"({chr(ord('a') + i)})" for i in range(len(axes))]
    for ax, lab in zip(axes, labels):
        ax.text(x, y, lab, transform=ax.transAxes, fontsize=fontsize or mpl.rcParams["font.size"],
                fontweight=weight, va="bottom", ha="left")


# --------------------------------------------------------------------------- #
# PDF 自检（供 save_fig 与 check_figures.py 共用）
# --------------------------------------------------------------------------- #
_CJK_RANGES = ((0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x3000, 0x303F), (0xFF00, 0xFFEF))


def _has_cjk(text: str) -> bool:
    return any(any(lo <= ord(ch) <= hi for lo, hi in _CJK_RANGES) for ch in text)


def check_pdf(pdf: str | os.PathLike, *, expect_cjk: bool | None = None, strict: bool = False,
              max_width_cm: float = TEXT_WIDTH_CM, min_font_pt: float = 5.0) -> list[tuple[str, str]]:
    """用 PyMuPDF 检查图 PDF：字体嵌入/轮廓合法性、文本可提取、字号下限、页数与宽度。

    返回 [(level, message)]，level ∈ {'FAIL','WARN'}；空列表表示通过。
    expect_cjk=None 时按 apply_style 的 lang 自动判断（zh → 期望能提取出中文）。
    """
    try:
        import pymupdf
    except ImportError:  # pragma: no cover
        return [("WARN", "未安装 pymupdf，跳过 PDF 自检")]

    pdf = Path(pdf)
    out: list[tuple[str, str]] = []
    doc = pymupdf.open(pdf)
    if doc.page_count != 1:
        out.append(("WARN", f"图 PDF 应为单页，实际 {doc.page_count} 页"))
    page = doc[0]
    w_cm = page.rect.width / 72 * 2.54
    if w_cm > max_width_cm + 0.05:
        out.append(("WARN", f"图宽 {w_cm:.1f} cm 超过版心 {max_width_cm:.1f} cm，插入论文时会被缩放导致字号失真"))

    fonts = page.get_fonts(full=True)
    has_text = False
    for xref, ext, ftype, basefont, *_ in fonts:
        has_text = True
        if ftype == "Type3":
            level = "FAIL" if strict else "WARN"
            out.append((level, f"字体 {basefont} 为 Type3（pdf.fonttype=3），文字不可提取/检索"))
            continue
        try:
            _, ext2, _, buf = doc.extract_font(xref)
        except Exception:  # noqa: BLE001
            buf, ext2 = b"", ext
        if not buf:
            out.append(("FAIL", f"字体 {basefont} 未嵌入，异机渲染会替换字体"))
            continue
        if ext2 in ("ttf", "ttc") and buf[:4] == b"OTTO":
            out.append(("FAIL", f"字体 {basefont} 为 CFF 轮廓却按 TrueType 嵌入（Noto CJK OTF + fonttype=42），PDF→PNG 会乱码"))

    # 实际渲染一次（与 docx-export 的 PDF→PNG 同一路径），捕获 MuPDF 的字形加载失败
    try:
        pymupdf.TOOLS.mupdf_warnings(reset=True)
        page.get_pixmap(dpi=72)
        render_warn = pymupdf.TOOLS.mupdf_warnings()
    except Exception:  # noqa: BLE001
        render_warn = ""
    if "cannot render glyph" in render_warn or "FT_Load_Glyph" in render_warn:
        out.append(("FAIL", "渲染时无法加载字形（嵌入字体损坏），PDF→PNG/Word 内会显示乱码或空白"))
    elif render_warn.strip():
        out.append(("WARN", f"渲染警告: {render_warn.strip().splitlines()[0]}"))

    text = page.get_text()
    if "\ufffd" in text:
        out.append(("FAIL", "提取文本含 U+FFFD 替换符，存在缺字"))
    if expect_cjk is None:
        expect_cjk = _ACTIVE.get("lang") == "zh" and any(ftype != "Type3" for _, _, ftype, *_ in fonts)
    if expect_cjk and has_text and not _has_cjk(text):
        out.append(("FAIL", "期望包含中文但提取不到任何中文字符（字体回退失败或字体损坏）"))

    try:
        sizes = [
            span["size"]
            for block in page.get_text("rawdict")["blocks"] if block.get("type") == 0
            for line in block["lines"] for span in line["spans"]
            if any(ch["c"].strip() for ch in span["chars"])
        ]
    except Exception:  # noqa: BLE001
        sizes = []
    if sizes and min(sizes) < min_font_pt:
        out.append(("WARN", f"最小字号 {min(sizes):.1f} pt < {min_font_pt} pt，打印/缩放后不可读"))
    doc.close()
    return out


# --------------------------------------------------------------------------- #
# 统一保存
# --------------------------------------------------------------------------- #
def save_fig(
    fig,
    path: str | os.PathLike,
    *,
    formats: Sequence[str] = ("pdf", "png"),
    dpi: int = 300,
    source: str | Sequence[str] | None = None,
    params: dict | None = None,
    check: bool = True,
    strict: bool = False,
    manifest: bool = True,
    close: bool = True,
) -> dict[str, str]:
    """统一导出：默认 PDF（论文/DOCX 链路）+ PNG（预览），可加 'svg'（可编辑）。

    path 可带或不带后缀，按 stem 生成各格式。source/params 记录到同目录
    `_manifest.json`，满足“真实数据图必须有数据来源与可复现参数”的要求。
    check=True 时对 PDF 运行 check_pdf，FAIL 会抛出 RuntimeError。
    """
    path = Path(path)
    stem = path.with_suffix("") if path.suffix.lower() in (".pdf", ".png", ".svg") else path
    stem.parent.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for ext in formats:
        ext = ext.lower().lstrip(".")
        target = stem.with_suffix(f".{ext}")
        kw = {"dpi": dpi} if ext == "png" else {}
        fig.savefig(target, **kw)
        written[ext] = str(target)

    findings: list[tuple[str, str]] = []
    if check and "pdf" in written:
        findings = check_pdf(written["pdf"], strict=strict)
        for level, msg in findings:
            print(f"[check_figures] {level}: {stem.name}.pdf: {msg}", file=sys.stderr)

    if manifest:
        mpath = stem.parent / "_manifest.json"
        try:
            data = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
        except json.JSONDecodeError:
            data = {}
        data[stem.name] = {
            "files": written,
            "script": os.path.relpath(os.path.abspath(sys.argv[0])) if sys.argv and sys.argv[0] else None,
            "source": [source] if isinstance(source, str) else (list(source) if source else []),
            "params": params or {},
            "fonts": {k: _ACTIVE.get(k) for k in ("latin", "cjk", "pdf_fonttype")},
            "checks": [f"{lv}: {m}" for lv, m in findings],
            "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        mpath.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if close:
        import matplotlib.pyplot as plt
        plt.close(fig)
    if any(lv == "FAIL" for lv, _ in findings):
        raise RuntimeError(f"{stem.name}.pdf 未通过图检查，见上方 [check_figures] 输出")
    return written
