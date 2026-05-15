# 云雾海的个人博客

## 简介

这个仓库用于存放本人平常的文章笔记，使用 Hugo 生成博客网站，并通过 GitHub Pages 发布。

你可以通过[链接](https://yunwuhai.github.io/)访问我的博客网站。

文章笔记主要是个人在学习开发过程中进行的一些记录，不保证内容实现的准确性和一致性，请酌情参考。

## 本地开发

### 环境要求

- Git
- Hugo **extended**
- 当前建议使用与 GitHub Actions 工作流一致的 Hugo `0.150.0`

> 当前主题 `PaperMod` 要求较新的 Hugo 版本；如果使用过旧版本，可能会出现无法构建的问题。

### 首次克隆

推荐在首次克隆时一并拉取主题子模块：

```bash
git clone --recurse-submodules git@github.com:yunwuhai/yunwuhai.github.io.git
```

如果已经克隆了仓库但没有拉取子模块，可以在仓库目录中执行：

```bash
git submodule update --init --recursive
```

### 本地预览

启动本地预览服务：

```bash
hugo server
```

如需同时预览草稿文章：

```bash
hugo server -D
```

### 构建自检

在发布前，可以先本地执行一次正式构建：

```bash
hugo --minify
```

## 发布方式

当前仓库已使用 GitHub Actions + GitHub Pages 自动部署：

1. 将修改提交并推送到 `master`
2. GitHub Actions 会自动执行 Hugo 构建
3. 构建成功后自动发布到 GitHub Pages

因此，本地通常不需要手动提交 `public/` 目录；本地构建主要用于自检。

## 开源协议

博客所有笔记均为原创，采用[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa]协议进行授权，部分文章首发于 CSDN ，可以访问[我的主页](https://blog.csdn.net/qq_44884716)查看。

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
