---
name: midori-preprint
description: 把已有的 LaTeX 论文（NeurIPS / ICLR / ICML / ACL / CVPR / COLM / AAAI / 自定义 .cls 等任意模板）转换成 Midori Lab 的 arXiv 预印本模板（preprint.sty：Palatino 正文、Montserrat 无衬线标题、#2D4227 深绿配色、NTU + Midori Lab logo、上粗下细双线标题、圆角摘要框）。只换模板和版式，不改正文内容，也不改作者原有的写作格式（粗体/斜体/实体字体/颜色等）。只要用户想“套模板”“换成我们的模板 / 实验室模板 / midori 模板 / preprint 模板”“把这篇 NeurIPS（或其他会议）论文改成 arXiv 版”“convert this paper to our preprint template”，或者给出一个 LaTeX 工程并希望得到实验室风格的预印本，就使用本 skill——即使用户没有点名模板名称。
---

# Midori 预印本模板转换

目标：把用户给的 LaTeX 论文工程转换成 Midori Lab 的 arXiv 预印本模板，得到一个能直接编译、版面干净、可以上传 arXiv 的新工程。

## 核心原则：只换模板，不动论文

使用这个模板的人写作风格各不相同：有人用很多粗体、斜体和实体字体，有人偏好克制严谨的写法。模板只负责“外壳”，所以转换时要严格区分两类东西。

**模板的领域（应当替换）**
- `\documentclass` 和会议样式包（`neurips_2026.sty`、`iclr2025_conference.sty`、`icml2025.sty`、`acl.sty`、`cvpr.sty`、自定义 `.cls` 等）
- 页面尺寸、页边距、分栏、正文字体包（`times`、`newtx*`、`mathptmx`、`geometry`、`fullpage` 等）
- 标题区、作者区、摘要外观、章节标题、图注样式、页眉页脚、链接颜色、参考文献样式文件
- 只为投稿流程存在的东西：会议 checklist、行号（`lineno`）、`\iclrfinalcopy` 一类开关、会议页脚

**论文的领域（保持原样）**
- 所有正文文字、数字、公式内容、引用、标签、图表内容
- 作者自定义的宏及其显示效果（方法名字体、模型/数据集字体、`\eg` 等）
- 正文里的强调方式（粗体、斜体、下划线），作者自己的颜色（表格底色、文字颜色、框的颜色）
- 有没有使用 research-paper-style 的写作格式（`\rps...` 宏、Observation、圈号贡献等）：原稿用了就保留，没用就不要加

判断标准：如果一处改动会让读者看到不同的文字、不同的强调或作者特意选的颜色，它就不属于模板转换。即使你觉得改了更好看（例如把表格的蓝色底色换成模板绿色），也不要做；可以在最后的报告里作为建议提出。

**允许的版式适配（必须做标记并在报告中列出）**
换了版面后，有些为原会议页数限制写的排版技巧会造成重叠或溢出。只在确实出问题或明显是页数技巧时处理，并在改动处加 `% [preprint]` 注释：
1. 正文和浮动体里的负间距（`\vspace{-...}`、`\vskip -...`）：整行注释掉，写成 `% [preprint] NeurIPS spacing hack: \vspace{-0.2in}`。
2. `wrapfigure` / `wraptable`：只有出现文字被挤成窄条、环绕区跨页、公式落进环绕区等问题时，才改成普通的 `figure` / `table`（`[t]`）。如果原稿里注释掉了一个普通 float 版本，优先用它。
3. 溢出的公式：在原有的逗号或运算符处拆成 `aligned`，保持同一个编号，不改任何符号。
4. 宏定义里用 `\textbf` 包住字体切换的写法（例如 `{\fontfamily{lmtt}\selectfont \textbf{Name}}`）：模板的 `\textbf` 是无衬线粗体，会改变显示效果。把定义里的 `\textbf{...}` 换成 `{\bfseries ...}`，让渲染结果和原稿一致。这一步是为了保持原样，不是改风格。
5. 双栏原稿（ICML / ACL / CVPR / AAAI）：按 `\columnwidth` 设置的图和 `\resizebox{\columnwidth}` 表格在 5.5in 单栏里会被放大约 1.7 倍。只在图过高或字明显过大时缩小，具体见参考文档第 7 节。

## 工作流程

### 1. 建立新工程，不碰原稿
在原工程里新建子文件夹 `arxiv_preprint/`（除非用户指定位置），把正文 `.tex`、图片、`.bib` 复制进去。所有修改都只在副本里进行，原工程的文件保持不变，这样用户随时可以回到会议版本。

### 2. 扫描原稿
```bash
python3 <skill>/scripts/scan_source.py <原工程目录>
```
脚本会报告：入口文件和 `\input` 树、文档类和会议样式、所有宏包及其选项（标出会和模板冲突的）、引用方式统计（`\cite` / `\citep` / `\citet`）、bst / biblatex、是否使用了 `\rps...` 宏、负间距和环绕浮动体的位置、双栏迹象、需要处理的宏定义、作者块原文、checklist 文件等。先读完这份报告再动手。

### 3. 复制模板文件
从 `<skill>/assets/template/` 复制到新工程：
- `preprint.sty`、`preprint.bst`、`logos/` 整个文件夹
- `researchpaperstyle.sty`：只在原稿使用了 `\rps...` 宏时需要

### 4. 重写导言区
读 `references/conversion-guide.md` 获取完整的对照表。要点：
- `\documentclass{article}`。去掉会议文档类的选项（如 `twocolumn`）。
- 先写需要传给模板内部宏包的选项（`\PassOptionsToPackage{numbers,compress}{natbib}`、`\PassOptionsToPackage{dvipsnames}{xcolor}` 等），再写 `\usepackage[选项]{preprint}`：
  - 原稿没用 `\rps...` 宏 → 加 `nowritingstyle`（只加载版式，不引入写作风格层，也减少宏包冲突）
  - 原稿用 biblatex → 加 `nonatbib`，保留原稿的 biblatex 设置
  - 正文宽度跟原稿走：扫描报告会估算原稿的正文宽度。单栏原稿约 6.5in（例如自定义报告类、2.5cm 页边距）→ 加 `wide`，这样按 `\textwidth` 缩放的整宽表格和图保持原来的大小；5.5in 的原稿（NeurIPS、ICLR、COLM）和双栏原稿用默认宽度
- 引用格式跟原稿一致：数字编号的论文写 `\setcitestyle{numbers,square,citesep={,}}`；作者-年份的论文用模板默认值。大量使用裸 `\cite` 的论文几乎都是数字编号，换成作者-年份会变成没有括号的文字。
- 参考文献样式：按字母排序的数字/作者-年份样式（plainnat、plain、abbrv、iclr、colm、acl_natbib 等）换成 `\bibliographystyle{preprint}`；按引用顺序编号的样式（unsrt、unsrtnat、IEEEtran 等）保留原样式，以免编号顺序改变。
- 删除会议样式包、页面/字体包、`\hypersetup` 里的颜色项（其他项如 `pdftitle` 保留）。
- 其余宏包和作者自定义的宏原样保留，只解决冲突（见参考文档的冲突表）。

### 5. 标题区和元信息
```latex
\title{...}                         % 保留原稿的手动换行
\author[1,\star]{Name}              % 每位作者一行，上标写在可选参数里
\affiliation[1]{University}
\authornote[\star]{Equal contribution}
\authornote[\dagger]{Corresponding author}
\correspondence{\email{...}}        % 只在原稿给出了邮箱时添加
\metadata[Code]{\url{...}}          % 只在代码链接不在摘要里时添加
\logos{%                            % 总是加上 NTU + Midori Lab logo
  \logoimage[0.42in]{logos/ntu-logo}%
  \logodivider[0.42in]%
  \logoimage[0.42in]{logos/midori-icon}\hspace{0.6em}%
  \logoimage[0.13in]{logos/midori-wordmark}}
\runninghead{<短标题>}              % 一般取标题冒号前的部分
```
- logo 总是 NTU + Midori Lab（实验室的固定做法）。如果作者单位里没有 NTU，在报告里提一句，方便用户决定是否需要换成其他 logo；不要自行替换。
- 共同一作、通讯作者等信息通常藏在 `\thanks` / `\footnotemark` 里，把它们转成 `\authornote`。
- 摘要文字一字不改。如果代码链接写在摘要里，就留在摘要里，不要再加一个 Code 行（避免重复），可以在报告里提一句。
- 原稿只有匿名占位作者时，先用 `[anonymous]` 编译，并在报告里请用户提供作者信息，不要编造。
- 不要添加原稿没有的日期、邮箱或链接。

### 6. 正文和附录
- 按原顺序 `\input` 各章节。摘要环境里去掉负间距，内容不变。
- 会议 checklist 这类投稿表格（NeurIPS Paper Checklist、ACL Responsible NLP checklist 等）不 `\input`，文件保留。致谢、Impact Statement、Limitations 等是论文内容，保留。
- 附录：`\appendix` 前加 `\clearpage`。

### 7. 编译和检查
```bash
python3 <skill>/scripts/build_check.py <新工程目录> --render 55
```
脚本用 latexmk 编译，汇总错误、未定义引用、overfull（带文件和行号）、字体替换，并把每页渲染成 PNG。按以下顺序处理：
1. 先解决编译错误（几乎都是宏包冲突，见参考文档）。
2. 再处理 overfull 和版式问题（按“允许的版式适配”）。
3. **逐页查看渲染图**，不要只看日志：日志看不出图注压在正文上、环绕区跨页、表格文字太小、prompt 框看不清这类问题。可疑的地方用 `--zoom` 放大到 150–220 dpi 再看。
4. 原会议版本里就存在的 warning（例如 `No positions in optional float specifier`）可以保留，在报告里说明是原稿自带的。
5. 如果 BibTeX 报错（latexmk 退出码 12），先用同样的方式编译一次原稿确认：原稿也有的错误来自 `.bib` 本身，属于论文内容，不要去改 `.bib`。用 `--force` 继续编译，确认引用都已解析，并把这些错误列进 `PREPRINT_NOTES.md` 供作者处理。

### 8. 确认正文没有被改
```bash
python3 <skill>/scripts/text_diff.py <原工程目录> <新工程目录>
```
脚本会比较两边每个 `.tex` 文件去掉命令、注释和纯版式参数（间距、浮动体位置和宽度、缩放）后的文字和数字序列（入口文件改名时加 `--entry 原名 --converted-entry 新名`）。正常情况下只剩这几类差异：入口文件里不再 `\input` 的 checklist 等投稿表格；摘要从自定义类的 `\abstract{...}` 命令移到正文的 `abstract` 环境。其他任何差异（改了措辞、移动或删掉了链接、改了颜色名、加了 `\rps...` 宏）都说明动了论文本身，要改回去。

### 9. 交付
- 把编译好的 `main.pdf` 和 `main.bbl` 放进新工程（上传 arXiv 需要 `.bbl`）。
- 在新工程里写 `PREPRINT_NOTES.md`，逐条列出所有改动：导言区替换了什么、标题区如何映射、每一处 `% [preprint]` 改动的位置和原因、没有处理但值得作者考虑的建议（例如原稿颜色和模板配色不协调）、需要用户补充的信息（例如通讯作者邮箱）。
- 在对话里简要汇报，并把 PDF 发给用户。

## 参考资料
- `references/conversion-guide.md`：各会议模板的识别和替换方法、宏包冲突表、引用格式对照、作者区映射示例、版式适配的具体写法、模板命令速查。转换前读一遍。
- `assets/example/main.tex`：模板的完整示例（使用了写作风格层，仅用于查看命令写法）。
- `scripts/prepare_logo.py`：用户想换成其他 logo 时使用（SVG 转 PDF、PNG 去白边、拆分上下排列的 logo）。
