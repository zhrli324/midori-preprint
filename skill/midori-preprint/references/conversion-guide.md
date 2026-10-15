# 转换参考手册

目录
1. 模板命令速查
2. 识别并移除会议模板
3. 宏包冲突表
4. 引用格式与参考文献样式
5. 作者区映射示例
6. 版式适配的写法
7. 双栏论文的特殊情况
8. 逐页检查清单

---

## 1. 模板命令速查

`\usepackage[选项]{preprint}`，选项可以组合：

| 选项 | 作用 |
|---|---|
| （无） | 默认：5.5in 单栏，Midori 绿色，加载写作风格层 |
| `nowritingstyle` | 不加载 researchpaperstyle.sty（原稿没用 `\rps...` 宏时使用） |
| `nonatbib` | 不加载 natbib（原稿用 biblatex 时使用） |
| `toc` | 摘要后单独一页目录。只在原稿有 `\tableofcontents` 或用户要求时使用；原稿的 `\tableofcontents` 可以换成这个选项 |
| `anonymous` | 隐藏作者、单位、作者说明、摘要框里的元信息和 logo |
| `monochrome` | 所有绿色变成黑/灰（logo 不变色） |
| `wide` | 6.5in 正文宽度 |

前言命令（都写在 `\begin{document}` 之前）：

| 命令 | 说明 |
|---|---|
| `\title{...}` | 无衬线粗体 18pt，上方 2.4pt 粗线、下方 0.5pt 细线 |
| `\author[上标]{姓名}` | 每人一行；上标在数学模式里排，可写 `1,2,\star`、`1,\dagger` |
| `\author{整段}` | 旧写法也可用（含 `\\`、`\thanks`），不推荐 |
| `\affiliation[上标]{单位}` | 每个单位一行 |
| `\authornote[符号]{说明}` | 作者下方的小字说明，例如共同一作、通讯作者 |
| `\date{...}` / `\metadata[标签]{内容}` / `\correspondence{...}` | 显示在摘要框底部 |
| `\email{...}` | 生成 mailto 链接的等宽邮箱 |
| `\logos{...}` / `\logoimage[高度]{文件}` / `\logodivider[高度]` | 首页左上角 logo 行，各部件垂直居中 |
| `\runninghead{...}` | 第 2 页起左上角页眉 |

模板对正文的统一处理（属于模板外观，不需要也不应该在正文里改）：
- `\appendix` 会在第一个附录章节前自动加一个深绿色的 “Appendix” 大标题（并在目录里加一行）
- `\textbf` 在正文中是无衬线粗体，在 `tabular` / `tabular*` / `tabularx` 里是衬线粗体（数字字形一致）
- 图注标签 "Figure 1" / "Table 1" 是深绿无衬线粗体，图注一律左对齐
- 章节标题深绿无衬线；`\paragraph` 是黑色无衬线粗体
- 链接颜色 `linkgreen`（#4A8240）

数学字体：模板已经修正了 mathpazo 的希腊字母问题。`\mathbf{\tau}`、`\mathrm{\lambda}` 中的小写希腊字母和标准 LaTeX 一样保持原样（要加粗用 `\bm{\tau}`），`\mathbf{\Omega}` 是粗体直立大写希腊字母。唯一的例外是 `\mathit{\Omega}`（Palatino 没有带希腊字母的斜体文本字体）；原稿用到时改成 `\mathnormal{\Omega}`，属于允许的显示修正，加 `% [preprint]` 注释。

模板另外提供的辅助命令（`\ourscell`、`\gain`、`\drop`、`\rps...`）属于写作风格。原稿没用就不要加进去。

## 2. 识别并移除会议模板

| 会议 | 识别 | 移除/替换 |
|---|---|---|
| NeurIPS | `\usepackage[...]{neurips_20xx}` | 删除；`\PassOptionsToPackage{...}{natbib}` 保留；`\workshoptitle` 删除；`sections/checklist.tex` 不 input |
| ICLR / COLM | `iclr20xx_conference.sty`、`colm20xx_conference.sty`，`\iclrfinalcopy` | 删除样式包和 `\iclrfinalcopy`；它们本来就是 5.5in 单栏、author-year |
| ICML | `icml20xx.sty`，`\icmltitle`、`\icmlauthor`、`\icmlaffiliation`、`\icmlcorrespondingauthor`、`\icmlkeywords`、`\printAffiliationsAndNotice`、`\twocolumn[...]` | 删除样式包；把 `\icml...` 作者命令转成 `\author`/`\affiliation`；去掉 `\twocolumn[...]` 包装，标题区交给 `\maketitle` |
| ACL / EMNLP / NAACL | `acl.sty`（`[review]`/`[final]`），`\aclfinalcopy` | 删除；作者块里的 `\And`/`\AND` 拆成逐个 `\author`；Limitations、Ethics 是内容，保留 |
| CVPR / ICCV / ECCV | `cvpr.sty`、`\cvprfinalcopy`、`\def\cvprPaperID`、`\confName`；ECCV 是 `llncs` 文档类 | 删除；ECCV 的 `\institute`、`\inst{}`、`\orcidlink` 转成 `\affiliation` 和上标 |
| AAAI | `aaai2x.sty`，`\pdfinfo{...}`，禁止的包很多 | 删除样式包和 `\pdfinfo`；AAAI 要求的 `\nocopyright` 等删除 |
| 自定义 `.cls`（例如报告类） | `\documentclass{xxx}` 加本地 `.cls` | 阅读 `.cls`，弄清它提供了哪些命令；正文用到的命令要么映射到模板等价命令，要么在导言区补一个最小定义 |

自定义类的常见映射：`\contribution[...]` → `\authornote`，`\checkdata[...]` → `\metadata`，类里的 `\abstract{...}` 命令 → 改成 `\begin{abstract}...\end{abstract}` 放在 `\maketitle` 之后，`\beginappendix` → `\appendix`。字体文件（例如 ByteSans）不要复制，模板用自己的字体。

同时删除这些只为原模板存在的包：`times`、`mathptmx`、`newtxtext`、`newtxmath`（如果正文用到了 newtxmath 独有的符号，改用 amssymb 中的等价符号并在报告中说明）、`helvet`、`courier`、`lmodern`、`geometry`、`fullpage`、`lineno`、`titlesec`（会覆盖模板标题样式）、`fancyhdr` 的页眉设置。`fontenc`、`inputenc`、`microtype` 可以保留。

## 3. 宏包冲突表

preprint.sty 已经加载：`fontenc[T1]`、`tgpagella`、`mathpazo`、`inconsolata`、`montserrat`、`graphicx`、`xcolor[table]`、`array`、`tabularx`、`booktabs`、`fancyhdr`、`natbib`（除非 `nonatbib`）、`etoolbox`、`caption`，以及在导言区末尾才加载的 `tcolorbox`（含 `skins` 库）。默认模式下还会立即加载 `enumitem`、`pifont`、`tcolorbox`（含 `skins,breakable,listings`）和 researchpaperstyle。

“Option clash” 错误的原因是：某个包已经被模板加载过，原稿又带着不同的选项再加载一次。处理方法：

| 原稿写法 | 改成 |
|---|---|
| `\usepackage[dvipsnames,svgnames]{xcolor}` | 在 `\usepackage{preprint}` 之前写 `\PassOptionsToPackage{dvipsnames,svgnames}{xcolor}`，删掉原行 |
| `\usepackage[numbers,sort&compress]{natbib}` | `\PassOptionsToPackage{numbers,sort&compress}{natbib}` 放在 preprint 之前，删掉原行；再按第 4 节设置 `\setcitestyle` |
| `\usepackage[font=small,labelfont=bf]{caption}` | 删掉选项（图注外观归模板管）；只保留 `\usepackage{caption}` 或直接删除 |
| `\usepackage[most]{tcolorbox}`（默认模式） | 改成 `\tcbuselibrary{most}`；`nowritingstyle` 模式下原样保留即可 |
| `\usepackage[shortlabels]{enumitem}`（默认模式） | `\PassOptionsToPackage{shortlabels}{enumitem}` 放在 preprint 之前；`nowritingstyle` 模式下原样保留 |
| `\usepackage{enumerate}`（默认模式） | 会覆盖 enumitem。原稿用了 `\begin{enumerate}[(a)]` 这类写法时，用 `\PassOptionsToPackage{shortlabels}{enumitem}` 并删除 enumerate 包；否则直接删除 |
| `\usepackage{ulem}` | 保留，并加 `\normalem`，避免 `\emph` 变成下划线 |
| `\usepackage{biblatex}` | 用 `nonatbib` 选项；保留 biblatex 原有设置 |
| `\hypersetup{colorlinks, linkcolor=red, ...}` | 删除颜色相关项；`pdftitle` 等其他项保留 |

正文自定义宏和模板重名时（例如原稿自己定义了 `\argmax`、`\email`、`\metadata`），优先保留原稿的定义：如果用 `\newcommand` 报“already defined”，就改成 `\renewcommand` 并在报告中注明。

## 4. 引用格式与参考文献样式

| 原稿 | 导言区 | `\bibliographystyle` |
|---|---|---|
| natbib + `numbers`（NeurIPS 常见），或大量裸 `\cite` 且 bst 是 plainnat/plain/abbrv | `\PassOptionsToPackage{numbers,compress}{natbib}`（照抄原选项）+ `\setcitestyle{numbers,square,citesep={,}}` | `preprint` |
| natbib author-year（ICLR、COLM、ACL 的 acl_natbib） | 模板默认 | `preprint` |
| 按引用顺序编号（unsrt、unsrtnat、IEEEtran、splncs04） | `\setcitestyle{numbers,square,citesep={,}}` | 保留原 bst（编号顺序是内容的一部分） |
| biblatex | `[nonatbib]`，biblatex 设置照搬 | 不需要 |

注意：natbib 的 author-year 模式下，裸 `\cite` 等同于 `\citet`，会输出没有括号的 “Smith et al. (2020)”。所以用裸 `\cite` 写成的论文必须保留数字编号。

## 5. 作者区映射示例

**NeurIPS 风格（上标 + footnotemark）**
```latex
% 原稿
\author{ Alice Wang$^{1}\footnotemark[1]$, Bob Li$^{1}\footnotemark[1]\thanks{Equal Contribution}$,
  ... \textbf{Carol Chen}$^{1}\footnotemark[2]\thanks{Corresponding Author}$ \\
  $^1$University One \\ $^2$... }
% 转换后
\author[1,\star]{Alice Wang}
\author[1,\star]{Bob Li}
\author[1,\dagger]{Carol Chen}
\affiliation[1]{University One}
\authornote[\star]{Equal contribution}
\authornote[\dagger]{Corresponding author}
```
原稿里的 `\textbf`、换行、`\ ,` 这类排版细节不需要保留，作者区外观由模板统一。

**NeurIPS / ACL 风格（每人一块，`\And` 分隔）**
```latex
\author{Alice Smith \\ University A \\ \texttt{alice@a.edu} \And Bob Lee \\ Company B \\ \texttt{bob@b.com}}
```
→ 按出现顺序给单位编号：`\author[1]{Alice Smith}`、`\author[2]{Bob Lee}`、`\affiliation[1]{University A}`、`\affiliation[2]{Company B}`。邮箱只有在原稿标明了通讯作者时才放进 `\correspondence`；否则在报告里问用户。

**ICML**
```latex
\icmlauthor{Alice Smith}{uniA}  \icmlaffiliation{uniA}{University A, City}
\icmlcorrespondingauthor{Alice Smith}{alice@a.edu}  \icmlequalcontribution
```
→ `\author[1,\dagger]{Alice Smith}`、`\affiliation[1]{University A, City}`、`\authornote[\dagger]{Corresponding author}`、`\correspondence{\email{alice@a.edu}}`；`\icmlequalcontribution` 对应的作者加 `\star` 和 `\authornote[\star]{Equal contribution}`。

**带 `\thanks` 的普通写法**：`\thanks` 里如果是通讯作者、共同一作 → `\authornote`；如果是资助声明 → 保留为脚注（放进 `\authornote` 会改变它的位置，在报告中说明你的选择）。

## 6. 版式适配的写法

所有改动都加 `% [preprint]` 注释，方便作者搜索和撤销。

**负间距**
```latex
% [preprint] NeurIPS spacing hack: \vspace{-0.2in}
```
只注释整行的负间距。正间距和 `\vspace` 以外的命令不动。

**环绕浮动体 → 普通浮动体**（只在出问题时）
```latex
% [preprint] wrapfigure -> figure: equation (3) sat inside the wrap region.
\begin{figure}[t]
    \centering
    \includegraphics[width=0.9\linewidth]{figs/proj.pdf}
    \caption{...原 caption 不变...}
    \label{fig:proj}
\end{figure}
```
宽度怎么选：原来是 `0.6\textwidth` 的环绕图，改成普通图后可以用 0.8–0.9`\linewidth`，以图中文字不被放得过大为准；表格类用 `0.7`–`1.0\linewidth`。

**溢出的公式**
```latex
% [preprint] Same two losses, split over two aligned lines (one equation
% number): on one line they overflow the column in Palatino math.
\begin{equation}
\begin{aligned}
\mathcal{L}_{a} &= ... ,\\
\mathcal{L}_{b} &= ... ,
\end{aligned}
\end{equation}
```
只在原有的逗号或关系符处断开，不改符号、间距命令和编号。

**宏定义里的 `\textbf` + 字体切换**
```latex
% 原稿
\def\method{{\fontfamily{lmtt}\selectfont \textbf{MethodName}}\xspace}
% [preprint] \bfseries instead of \textbf (template \textbf is sans-serif)
\def\method{{\fontfamily{lmtt}\selectfont\bfseries MethodName}\xspace}
```

## 7. 双栏论文的特殊情况

ICML、ACL、CVPR、AAAI 是双栏版式。转成 5.5in 单栏后：
- `figure*` / `table*` 在单栏里和 `figure` / `table` 一样，不需要改。
- 按 `\columnwidth` 或 `\linewidth` 设置宽度的单栏图会从约 3.3in 变成 5.5in，放大约 1.7 倍。只有在图变得过高（超过约半页）或图中文字明显过大时才调整：把宽度改成 `0.6\linewidth` 左右，并加 `% [preprint] two-column figure, scaled for single column` 注释。
- 为双栏写的 `\resizebox{\columnwidth}{!}{...}` 表格会被放大到 5.5in，字体可能大于正文。如果出现这种情况，改成 `\resizebox{0.6\linewidth}{!}{...}` 或不超过表格原始宽度，同样加注释。
- 页数会变化，这是正常的，不需要压缩。

单栏但比 5.5in 宽的原稿（自定义报告类、`geometry` 设成 2.5cm 页边距等，约 6.5in）：用 `[wide]`，否则所有按 `\textwidth` 缩放的表格和图都会缩小到约 0.84 倍。`scan_source.py` 的 “Text width” 一节会给出估算和建议。

## 8. 逐页检查清单

用 55 dpi 概览全部页面，再对可疑区域放大到 150–220 dpi：
- 首页：logo 行、两条标题线、作者是否在姓名中间断行、单位列表是否完整、摘要框（有无负间距残留、Code 行是否重复）
- 图注或表格压到正文上（负间距残留）
- 环绕区域跨页、文字被挤成窄条、公式落入环绕区域
- 公式超出正文右边界
- 表格：粗体数字是否为衬线体、表格是否超出版心、文字是否小到看不清（原稿就很小的不算问题）
- 作者自定义的框、颜色和原稿一致（不要统一成模板配色）
- 参考文献格式、数字编号或作者-年份和原稿一致
- 附录从新的一页开始；checklist 已经不在 PDF 里
- 只有浮动体的页面从顶部开始排（模板已处理）
