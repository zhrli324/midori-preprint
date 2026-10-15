# 模板用法

用 pdfLaTeX 编译：

```bash
latexmk -pdf main.tex
```

## 选项

```latex
\usepackage{preprint}                   % 默认
\usepackage[anonymous]{preprint}        % 匿名
\usepackage[monochrome]{preprint}       % 黑白
\usepackage[wide]{preprint}             % 6.5in 正文宽度
\usepackage[nowritingstyle]{preprint}   % 不加载 researchpaperstyle.sty
\usepackage[nonatbib]{preprint}         % 不加载 natbib
```

## 首页

```latex
\title{...}
\author[1,\star]{First Author}
\author[1,\dagger]{Last Author}
\affiliation[1]{University}
\authornote[\star]{Equal contribution}
\authornote[\dagger]{Corresponding author}
\date{\today}
\metadata[Code]{\url{https://github.com/...}}
\correspondence{\email{name@example.com}}
\logos{%
  \logoimage[0.42in]{figures/ntu-logo}%
  \logodivider[0.42in]%
  \logoimage[0.42in]{figures/midori-icon}\hspace{0.6em}%
  \logoimage[0.13in]{figures/midori-wordmark}}
\runninghead{Preprint}
```

完整示例见 `main.tex`，编译效果见 `preview/`。

上传 arXiv 时带上 `main.bbl`、`preprint.sty`、`researchpaperstyle.sty` 和 `figures/`。
