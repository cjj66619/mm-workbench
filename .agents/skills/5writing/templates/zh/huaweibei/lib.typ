// 华为杯模板共享定义：字体回退链 + 三线表。main.typ 与 sections/*.typ 都通过 #import 使用。
// 官方要求：西文/数字 Times New Roman，中文宋体（正文）/ 黑体（标题）/ 楷体（摘要页标签）。
//
// typst 对字体列表里每个缺失的字体族都会逐条 warning，因此列表只放"当前平台真实安装"的字体：
// - 默认（Linux，setup_env.sh 安装）：Liberation Serif（与 Times New Roman 同字宽）、Noto CJK、
//   文鼎楷体、文泉驿；编译零字体 warning。
// - Windows/macOS 装有官方字体时：typst compile --input official-fonts=true …
//   （或把下面 default 改成 "true"），用 Times New Roman / 宋体 / 黑体 / 楷体 本尊。
// 两套字体字宽接近，页数与版式基本一致；最终提交前请用官方字体编译一次核对。
#let official-fonts = sys.inputs.at("official-fonts", default: "false") == "true"
#let song-font = if official-fonts {
  ("Times New Roman", "SimSun", "Songti SC", "STSong")
} else {
  ("Liberation Serif", "Noto Serif CJK SC")
}
#let kai-font = if official-fonts {
  ("Times New Roman", "KaiTi", "Kaiti SC", "STKaiti")
} else {
  ("Liberation Serif", "AR PL KaitiM GB", "Noto Serif CJK SC")
}
#let hei-font = if official-fonts {
  ("Times New Roman", "SimHei", "Heiti SC", "STHeiti")
} else {
  ("Liberation Serif", "Noto Sans CJK SC", "WenQuanYi Micro Hei")
}
#let code-font = if official-fonts {
  ("Courier New", "Menlo", "Noto Sans Mono CJK SC")
} else {
  ("Liberation Mono", "Noto Sans Mono CJK SC")
}

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
