// 华为杯模板共享定义：字体回退链 + 三线表。main.typ 与 sections/*.typ 都通过 #import 使用。
// 西文/数字 Times New Roman，中文宋体（正文）/ 黑体（标题）；Linux 无宋体黑体时回退到 Noto CJK。
#let song-font = ("Times New Roman", "SimSun", "Songti SC", "STSong", "Noto Serif CJK SC", "Noto Serif SC")
#let kai-font = ("Times New Roman", "KaiTi", "Kaiti SC", "STKaiti", "Noto Serif CJK SC", "Noto Serif SC")
#let hei-font = ("Times New Roman", "SimHei", "Heiti SC", "STHeiti", "Noto Sans CJK SC", "Noto Sans SC", "WenQuanYi Zen Hei")
#let code-font = ("Courier New", "Menlo", "DejaVu Sans Mono", "Noto Sans Mono CJK SC")

// 三线表快捷函数：three-line-table([表题], (列宽…), ([表头]…), ([单元格]…))；表题自动出现在表上方，编号全篇连续
#let three-line-table(caption, columns, header, body) = figure(
  kind: table,
  supplement: [表],
  caption: caption,
  table(
    columns: columns,
    table.hline(y: 0, stroke: 1.5pt),
    ..header,
    table.hline(y: 1, stroke: 0.5pt),
    ..body,
    table.hline(stroke: 1.5pt),
  ),
)
