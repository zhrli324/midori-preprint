# Midori Preprint：LaTeX 模板

设计来源（详见仓库根目录 README 的致谢）：
- **正文版式**：来自 arXiv 2610.18141（COLM 2026 preprint 模式），包括 Palatino 字体、5.5in 单栏、段间空行、紧凑的章节间距。
- **首页与配色**：来自 arXiv 2605.09965 的报告模板，包括上粗（2.4pt）下细（0.5pt）两条线夹住的无衬线标题、逐个书写的作者和单位、带 Date/Code/Correspondence 的圆角摘要框、彩色无衬线章节标题、无衬线粗体，以及彩色的 "Figure 1"/"Table 1" 标签。原报告用的是蓝色，这里全部换成了 Midori Lab 的绿色（见下方配色表）。
- **写作风格层**：`researchpaperstyle.sty`，来自 research-paper-style 写作风格 skill 的组件包；不使用时可用 `nowritingstyle` 选项关闭。

原报告的标题字体 ByteSans 是字节跳动的字体，授权不明，所以没有复制，改用 TeX Live 自带、开源、外形最接近的几何无衬线字体 Montserrat。

| 文件 | 作用 |
|---|---|
| `preprint.sty` | 版式：Palatino + Montserrat、单栏、首页标题与摘要框、绿色标题、页眉、表格/附录辅助命令；会自动加载写作风格层 |
| `researchpaperstyle.sty` | 写作风格层：实体字体、圈号贡献、模块符号、阶段标记、Observation、黑白框（原样复制自 skill 资产，可单独升级） |
| `figures/` | Logo 素材：`ntu-logo.pdf`（矢量 PDF，已裁边）、`midori-icon.png` + `midori-wordmark.png`（Midori Lab 的烧瓶图标和文字，已去白边、背景透明）、`midori-logo.png`（上下排列的完整 logo） |
| `main.tex` | 完整示例，每类元素都用上了（名称和数值都是占位内容） |
| `preprint.bst` | natbib author-year 参考文献格式 |
| `math_commands.tex` | Goodfellow 深度学习记号宏（可选） |
| `preview/` | 默认版 / 纯黑白版 / 宽版的编译效果（在仓库根目录运行 `make preview` 重新生成） |

## 选项

```latex
\usepackage{preprint}                % 默认：5.5in 单栏，Midori 绿色点缀
\usepackage[anonymous]{preprint}     % 匿名：隐藏作者、单位、脚注说明和摘要框里的元信息
\usepackage[monochrome]{preprint}    % 纯黑白：标题线、章节标题、链接、底色全部变黑/灰
\usepackage[wide]{preprint}          % 宽版：6.5in 正文宽度（接近原报告的 2.5cm 边距）
\usepackage[nowritingstyle]{preprint} % 只加载版式，不加载写作风格层（不用 \rps... 宏的论文）
\usepackage[nonatbib]{preprint}      % 不加载 natbib（用 biblatex 的论文）
```

选项可以组合，例如 `\usepackage[wide,monochrome]{preprint}`。

## 配色（Midori）

| 颜色名 | 色值 | 用在哪里 |
|---|---|---|
| `midori`（= `accent`） | `#2D4227` 深绿 | 章节标题、标题上下的细线、摘要框边框和 "Abstract"、图表标签、页眉、Takeaway/Prompt 框的标题栏 |
| `linkgreen` | `#4A8240` 中绿 | 所有链接（引用、交叉引用、网址）；比深绿浅，和正文区分开，对白底对比度 4.6:1 |
| `midorileaf`（= `oursgreen`） | `#5A8F4E` 叶绿 | 画图时的主强调色；附录总览表的底色由它调浅得到 |
| `midorimatcha` | `#8DB06A` 抹茶绿 | 次强调色，例如热力图 |
| `oursbg` | `#E6EFE1` 浅绿 | 本文方法那一行的单元格底色（`\ourscell`） |
| `gaingreen` | `#3B7D3F` | `\gain{}` 的涨幅数字 |
| `dropred` | 红 | `\drop{}` 的跌幅数字（保持红色，好和涨幅区分） |

旧颜色名 `linkblue`、`oursblue`、`gainblue`、`oursteal` 仍然可以用，它们现在都指向对应的绿色。画图时用 `midorileaf` 和 `midorimatcha`，图表就能和正文配色一致。

## 首页写法

```latex
\title{...}
\author[1,\star]{First Author}          % 每位作者一行，可选参数是上标
\author[1,\dagger]{Last Author}
\affiliation[1]{University One}
\authornote[\star]{Equal contribution}  % 作者下方的说明
\authornote[\dagger]{Corresponding author}
\date{\today}                           % 以下几行显示在摘要框底部，都是可选的
\metadata[Code]{\url{https://github.com/...}}
\correspondence{\email{name@example.com}}
\logos{%                                % 第 1 页左上角的 logo 行（可选）
  \logoimage[0.42in]{figures/ntu-logo}%
  \logodivider[0.42in]%                 % 两个 logo 之间的灰色竖线
  \logoimage[0.42in]{figures/midori-icon}\hspace{0.6em}%
  \logoimage[0.13in]{figures/midori-wordmark}}
\runninghead{Preprint}
```

旧写法 `\author{整段作者块，含 \\ 和 \thanks}` 仍然可以用。

Logo 行的写法：`\logoimage[高度]{文件}` 会让每张图在同一条水平中线上垂直居中，`\logodivider[高度]` 是 logo 之间的细竖线。Midori 的图标和 NTU 一样高（0.42in），文字部分 0.13in，这样两边的文字视觉重量接近。想用原版上下排列的 Midori logo，可以换成 `\logoimage[0.55in]{figures/midori-logo}`。用 `[anonymous]` 时 logo 会自动隐藏，避免泄露单位信息。

参考文献默认是作者-年份格式。如果想要原报告那种数字编号 [1]，在导言区加一行 `\setcitestyle{numbers,square,citesep={,}}`。

## 写作风格速查

| 角色 | 写法 | 效果 |
|---|---|---|
| 本文方法 | `\rpsMethod{Name}` | 粗等宽 |
| 外部方法 / 数据集 | `\rpsBaseline{}` / `\rpsDataset{}` | 正常正文 |
| 模型 | `\rpsModel{}` | pcr（Courier） |
| Benchmark | `\rpsBenchmark{}` | cmtt；处在粗体语境中也保持常规字重 |
| 命名模块 | `\rpsComponent{95}{Router}` | 小花 + small caps；95/96 = 实心/空心花 |
| 方法阶段 | `\rpsStage{Stage 1: Detect.}` | ▷ + 粗体 |
| 瓶颈/关键短语 | `\rpsStrong{}` | 粗体 |
| 对比维度 | `\rpsTerm{}` | 斜体 |
| 贡献 | `contributions` 环境 + `\rpsStrongTerm{短标题.}` | 自动圈号 + 粗斜体 |
| 实验发现 | `\rpsObservation{判断句}\label{obs:x}` | “Observation ❶:” + 粗体；`\cref` 引用时显示阿拉伯数字 |
| 核心问题 | `rpsquestion` 环境 | 黑白细框、斜体 |
| Takeaway | `rpsinsight{Takeaway}` 环境 | 黑色标题栏框 |
| Prompt / 原始材料 | `rpsprompt{标题}` 环境 | 等宽体、自动折行、可跨页，内容原样保留 |
| 表格 | `\rpsBest{}` / `\rpsSecond{}` / `\ourscell{}` / `\gain{}` / `\drop{}` | 最优粗体 / 次优下划线 / 本文方法行底色 / 涨跌 |

`\textbf`、`\rpsStrong` 和 `\rpsStrongTerm` 都会显示成无衬线粗体（原报告的做法），表格里用 `\rpsBest` 标出的数字仍是衬线粗体。

建议每个名字都在导言区定义成宏（见 `main.tex` 开头），这样全文字体保持一致。粗体只用于有证据支持的判断，背景和机制解释保持普通正文。

数学字体：Palatino 数学字体（mathpazo）原本会让 `\mathbf{\tau}`、`\mathrm{\lambda}` 显示成乱码，模板已修正为和标准 LaTeX 一致：小写希腊字母不受 `\mathbf` 影响（加粗请用 `\bm`），`\mathbf{\Omega}` 是粗体直立大写希腊字母。

编译：`latexmk -pdf main.tex`（pdfLaTeX）。上传 arXiv 时要把 `main.bbl`、`preprint.sty`（以及用到时的 `researchpaperstyle.sty`）和 `figures/` 一起上传。

## 把已有论文换成这个模板

用仓库里的 Claude skill：见 [`../skill/midori-preprint`](../skill/midori-preprint) 和根目录 README 的安装说明。对 Claude 说“把这篇论文套上 Midori 预印本模板”即可：它只换模板和版式，不改正文和作者原有的格式，所有改动记录在新工程的 `PREPRINT_NOTES.md` 里。
