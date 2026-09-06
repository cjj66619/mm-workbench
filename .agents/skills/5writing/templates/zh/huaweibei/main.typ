#set document(title: "[论文标题]", author: ())

// 排版参数来源：.agents/skills/_references/huaweibei_body_format.md（官方 Word 模板正文格式）。
// 西文/数字 Times New Roman，中文宋体（正文）/ 黑体（标题）；Linux 无宋体黑体时回退到 Noto CJK。
#import "lib.typ": *

// 一级 “一、” 中文数字；二/三级 “1.1” / “1.1.1”（isLgl：恒为阿拉伯数字）
#let heading-numbering(..nums) = {
  let ns = nums.pos()
  if ns.len() == 1 {
    numbering("一、", ns.at(0))
  } else if ns.len() == 2 {
    numbering("1.1", ns.at(0), ns.at(1))
  } else {
    numbering("1.1.1", ns.at(0), ns.at(1), ns.at(2))
  }
}

// A4，四边 2.5 cm，页眉距 1.5 cm（空），页脚距 1.75 cm，页码居中 9 pt
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  header-ascent: 1.5cm,
  footer-descent: 1.75cm - 0.75cm,
  footer: context {
    let n = counter(page).get().first()
    if n > 0 { align(center)[#text(font: song-font, size: 9pt)[#n]] }
  },
)
// 正文：小四 12 pt，首行缩进 2 字符，两端对齐，单倍行距（宋体 12 pt 自然行距 ≈ 15.6 pt → leading 0.3em），段前后 0
#set text(font: song-font, size: 12pt, lang: "zh", region: "cn")
#set par(first-line-indent: (amount: 2em, all: true), justify: true, leading: 0.35em, spacing: 0.35em)
#set enum(numbering: "(1)", indent: 2em)
#set list(indent: 2em)
#set heading(numbering: heading-numbering)
// 行间公式：居中，编号 (N) 全篇连续、右对齐
#set math.equation(numbering: "(1)", supplement: [式])
#show math.equation.where(block: true): set block(above: 0.8em, below: 0.8em)
// 标题：一级 黑体 14 pt 居中；二级 12 pt 加粗；三级 12 pt 不加粗；段前/段后 6 pt；不缩进
#show heading.where(level: 1): it => block(above: 6pt + 0.35em, below: 6pt + 0.35em, width: 100%, sticky: true)[
  #set par(first-line-indent: 0pt)
  #set text(font: hei-font, size: 14pt, weight: "regular")
  #align(center)[#if it.numbering != none [#counter(heading).display(it.numbering)]#it.body]
]
#show heading.where(level: 2): it => block(above: 6pt + 0.35em, below: 6pt + 0.35em, sticky: true)[
  #set par(first-line-indent: 0pt)
  #text(font: song-font, size: 12pt, weight: "bold")[#counter(heading).display(it.numbering) #it.body]
]
#show heading.where(level: 3): it => block(above: 6pt + 0.35em, below: 6pt + 0.35em, sticky: true)[
  #set par(first-line-indent: 0pt)
  #text(font: hei-font, size: 12pt, weight: "regular")[#counter(heading).display(it.numbering)]
  #text(font: song-font, size: 12pt, weight: "regular")[#it.body]
]
// 图题在图下、表题在表上：“图N xxx” / “表N xxx”，11 pt 加粗居中，全篇连续编号
#set figure(numbering: "1")
#show figure.caption: it => block(above: 3pt, below: 6pt)[
  #set par(first-line-indent: 0pt)
  #text(size: 11pt, weight: "bold")[#it.supplement#context it.counter.display(it.numbering) #it.body]
]
#show figure.where(kind: table): set figure.caption(position: top)
#show figure.where(kind: table): set figure(supplement: [表])
#show figure.where(kind: image): set figure(supplement: [图])
#show figure: set block(above: 6pt + 0.35em, below: 6pt + 0.35em)
// 表格：三线表（顶/底 1.5 pt，表头下 0.5 pt，无竖线），单元格 12 pt 居中、无缩进
#set table(stroke: none, align: center + horizon, inset: (x: 0.6em, y: 4pt))
#show table.cell: set par(first-line-indent: 0pt)
#show table.cell.where(y: 0): strong
// 附录代码：等宽 10.5 pt，0.5 pt 全框线，无缩进
#show raw.where(block: true): it => block(
  inset: (x: 0.7em, y: 0.55em),
  stroke: 0.5pt + black,
  width: 100%,
)[#set par(first-line-indent: 0pt, leading: 0.4em); #text(font: code-font, size: 10.5pt)[#it]]
#show raw.where(block: false): set text(font: code-font, size: 10.5pt)


#let cover-info-table() = align(center)[
  #block(width: 15.2cm)[
    #block(width: 100%, height: 1.55cm)[
      #grid(
        columns: (4.2cm, 1fr),
        align: (left + horizon, left + horizon),
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[学 #h(1em) 校]]
        ],
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[[学校名称]]]
        ],
      )
      #line(length: 100%, stroke: 1.2pt)
    ]
    #block(width: 100%, height: 1.55cm)[
      #grid(
        columns: (4.2cm, 1fr),
        align: (left + horizon, left + horizon),
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[参赛队号]]
        ],
        box(height: 1.05cm)[
          #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[[参赛队号]]]
        ],
      )
      #line(length: 100%, stroke: 1.2pt)
    ]
    #grid(
      columns: (4.2cm, 1fr),
      align: (left + horizon, left + top),
      block(height: 3.3cm)[
        #align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[队员姓名]]
      ],
      block(width: 100%)[
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[1. [成员 A]]]]
          #line(length: 100%, stroke: 0.55pt)
        ]
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[2. [成员 B]]]]
          #line(length: 100%, stroke: 0.55pt)
        ]
        #block(width: 100%, height: 1.1cm)[
          #box(height: 0.82cm)[#align(left + horizon)[#text(font: hei-font, size: 20pt, weight: "bold")[3. [成员 C]]]]
          #line(length: 100%, stroke: 1.2pt)
        ]
      ],
    )
  ]
]

// 封面：赛徽 / 届数 / 学校 / 队号 年年变，开赛后按当届官方模板替换 logo.pdf、title.pdf 与本函数。封面为第 0 页，不显示页码。
#let cover-page() = {
  counter(page).update(0)
  set par(first-line-indent: 0pt)
  align(center)[#image("logo.pdf", width: 14.5cm)]
  v(1.35cm)
  align(center)[#image("title.pdf", width: 10.8cm)]
  v(2.35cm)
  cover-info-table()
  pagebreak()
}

// 摘要页（第 1 页）：题目行 隶书 18 pt + 题名 14 pt 下划线；“摘 要：”居中；正文段前后 3 pt；关键词间两个全角空格
#let abstract-page() = {
  counter(page).update(1)
  set par(first-line-indent: 0pt, spacing: 3pt)
  align(center)[#image("title.pdf", width: 10.8cm)]
  v(0.65cm)
  block(width: 100%)[
    #set par(leading: 0.75em)
    #text(font: kai-font, size: 18pt)[题#h(1em)目：]#underline(text(size: 14pt)[[论文标题]])
  ]
  v(0.3cm)
  align(center)[#text(font: kai-font, size: 18pt)[摘#h(1em)要：]]
  v(0.3cm)
  block[
    #set par(first-line-indent: (amount: 2em, all: true), spacing: 6pt + 0.35em)
    [中文摘要内容：问题概述 + 每个子问题的方法和数值结果 + 结论]
  ]
  v(0.6cm)
  block[
    #text(font: kai-font, size: 18pt)[关键词：] [关键词1] #h(2em) [关键词2] #h(2em) [关键词3]
  ]
  pagebreak()
}

// 目录页：标题 16 pt 加粗居中；条目 10.5 pt，到三级，点线引导；不进目录
#let toc-page() = {
  set par(first-line-indent: 0pt)
  align(center)[#text(size: 16pt, weight: "bold")[目录]]
  v(0.5em)
  show outline.entry.where(level: 1): set block(above: 3pt + 0.35em, below: 3pt)
  show outline.entry.where(level: 2): set block(above: 3pt, below: 3pt)
  show outline.entry.where(level: 3): set block(above: 3pt, below: 3pt)
  set text(size: 10.5pt)
  outline(title: none, depth: 3, indent: 1em)
  pagebreak()
}

#cover-page()
#abstract-page()
#toc-page()

#include("sections/1_restatement.typ")
#include("sections/2_analysis.typ")
#include("sections/3_assumptions.typ")
#include("sections/4_symbols.typ")
#include("sections/5_problem1.typ")
#include("sections/6_problem2.typ")
#include("sections/7_problem3.typ")
#include("sections/8_sensitivity.typ")
#include("sections/9_evaluation.typ")

// 参考文献 / 附录：一级标题不编号、仍居中 14 pt 黑体、进目录
#heading(level: 1, numbering: none)[参考文献]
#block[
  #set par(first-line-indent: 0pt, hanging-indent: 2em, leading: 0.5em, spacing: 0.5em)
  #include("references.typ")
]

#pagebreak()
#heading(level: 1, numbering: none)[附录]
#include("sections/A_code.typ")
