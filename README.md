# Midori Preprint

Midori Lab 的 arXiv 预印本 LaTeX 模板，以及把已有 LaTeX 论文转换成该模板的 Claude skill。

![Preview](docs/preview.png)

## 模板

```bash
cp -R template my-paper && cd my-paper
latexmk -pdf main.tex
```

用法见 [`template/README.md`](template/README.md)。

## Skill

安装：

```bash
make install
```

或下载 [`dist/midori-preprint.skill`](dist/midori-preprint.skill) 在 Claude 中安装。

使用：对 Claude 说“把这篇论文改成 Midori 预印本模板”。skill 只换模板，不改论文正文和格式。

## 维护

修改 `template/` 后运行：

```bash
make sync && make preview && make skill
```

## 许可

[MIT](LICENSE)
