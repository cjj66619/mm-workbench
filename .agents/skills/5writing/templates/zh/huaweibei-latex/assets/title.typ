// 封面标题图（title.pdf）的可编辑源文件。
// 每届比赛请核对届数后重新生成：  typst compile title.typ ../title.pdf
// 正式提交时应以当届官方 Word/PDF 模板的封面为准，本文件仅用于赛前演练与排版预览。
#let edition = "第二十三届"   // 2026 年为第二十三届；2025 年为第二十二届
#set page(width: 318.6pt, height: 86.8pt, margin: 0pt, fill: none)
#set text(font: ("STXinwei", "华文新魏", "Noto Serif CJK SC", "Noto Sans CJK SC"), weight: "bold", lang: "zh")
#set align(center + horizon)
#stack(
  dir: ttb,
  spacing: 8pt,
  text(size: 15pt)[中国研究生创新实践系列大赛],
  text(size: 18pt)[“华为杯”#edition\中国研究生],
  text(size: 18pt)[数学建模竞赛],
)
